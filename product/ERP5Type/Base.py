##############################################################################
#
# Copyright (c) 2002-2003 Nexedi SARL and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

from Globals import InitializeClass, DTMLFile
from AccessControl import ClassSecurityInfo
from AccessControl.Permission import pname
from Acquisition import aq_base, aq_inner, aq_acquire, aq_chain

from Products.CMFCore.WorkflowCore import WorkflowMethod
from Products.CMFCore.PortalContent import PortalContent
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.Expression import Expression

from Products.DCWorkflow.Transitions import TRIGGER_WORKFLOW_METHOD


from Products.ERP5Type import _dtmldir
from Products.ERP5Type import PropertySheet
from Products.ERP5Type import Permissions
from Products.ERP5Type.Utils import UpperCase
from Products.ERP5Type.Utils import convertToUpperCase, convertToMixedCase
from Products.ERP5Type.Utils import createExpressionContext
from Products.ERP5Type.Utils2 import _getListFor
from Products.ERP5Type.Accessor.TypeDefinition import list_types
from Products.ERP5Type.Accessor import Base as BaseAccessor
from Products.ERP5Type.XMLExportImport import Base_asXML
from Accessor import WorkflowState

from ZopePatch import ERP5PropertyManager

from CopySupport import CopyContainer
from Errors import DeferredCatalogError
from Products.CMFActivity.ActiveObject import ActiveObject

from string import join
import sys
import psyco
import pickle
import copy

from cStringIO import StringIO
from email.MIMEBase import MIMEBase
from email import Encoders
from socket import gethostname, gethostbyaddr
import random

from zLOG import LOG, INFO, ERROR, WARNING

# Dynamic method acquisition system (code generation)
aq_method_generated = {}
aq_portal_type = {}
aq_related_generated = 0

def _aq_reset():
  global aq_portal_type, aq_method_generated, aq_related_generated
  aq_method_generated = {}
  aq_portal_type = {}
  aq_related_generated = 0

class PropertyHolder:
  isRADContent = 1
  def __init__(self):
    self.__name__ = 'PropertyHolder'

def getClassPropertyList(klass):
  ps_list = getattr(klass, 'property_sheets', ())
  ps_list = tuple(ps_list)
  for super_klass in klass.__bases__:
    if getattr(super_klass, 'isRADContent', 0): ps_list = ps_list + tuple(filter(lambda p: p not in ps_list,
                                                         getClassPropertyList(super_klass)))
  return ps_list

def initializeClassDynamicProperties(self, klass, recursive=0):
  id = ''
  #LOG('before aq_method_generated %s' % id, 0, str(klass.__name__))
  if not aq_method_generated.has_key(klass):
    # Mark as generated
    aq_method_generated[klass] = 1
    # Recurse to superclasses
    for super_klass in klass.__bases__:
      if getattr(super_klass, 'isRADContent', 0): initializeClassDynamicProperties(self, super_klass, recursive=1)
    # Initialize default properties
    #LOG('in aq_method_generated %s' % id, 0, str(klass.__name__))
    from Utils import initializeDefaultProperties
    if not getattr(klass, 'isPortalContent', None):
      initializeDefaultProperties([klass], object=self)

def initializePortalTypeDynamicProperties(self, klass, ptype, recursive=0):
  id = ''
  #LOG('before aq_portal_type %s' % id, 0, str(ptype))
  if not aq_portal_type.has_key(ptype):
    # Mark as generated
    aq_portal_type[ptype] = PropertyHolder()
    prop_holder = aq_portal_type[ptype]
    # Recurse to parent object
    parent_object = self.aq_parent
    parent_klass = parent_object.__class__
    parent_type = parent_object.portal_type
    if getattr(parent_klass, 'isRADContent', 0):
      initializePortalTypeDynamicProperties(self, parent_klass, parent_type, recursive=1)
    if not recursive:
      # Initiatise portal_type properties (XXX)
      ptype_object = getattr(self.portal_types, self.portal_type, None)
      cat_list = []
      prop_list = []
      constraint_list = []
      if ptype_object is not None and ptype_object.meta_type == 'ERP5 Type Information':
        # Make sure this is an ERP5Type object
        ps_list = map(lambda p: getattr(PropertySheet, p, None), ptype_object.property_sheet_list)
        ps_list = filter(lambda p: p is not None, ps_list)
        # Always append the klass.property_sheets to this list (for compatibility)
        # Because of the order we generate accessors, it is still possible
        # to overload data access for some accessors
        ps_list = tuple(ps_list) + getClassPropertyList(klass)
        #LOG('ps_list',0, str(ps_list))
      else:
        ps_list = getClassPropertyList(klass)
      for base in ps_list:
          if hasattr(base, '_properties'):
            prop_list += base._properties
          if hasattr(base, '_categories'):
            if type(base._categories) in (type(()), type([])):
              cat_list += base._categories
            else:
              cat_list += [base._categories]
          if hasattr(base, '_constraints'):
            constraint_list += base._constraints
      if ptype_object is not None and ptype_object.meta_type == 'ERP5 Type Information':
        cat_list += ptype_object.base_category_list
      prop_holder._properties = prop_list
      prop_holder._categories = cat_list
      prop_holder._constraints = constraint_list
      if hasattr(klass, 'security'):
        prop_holder.security = klass.security # Is this OK for security XXX ?
      else:
        prop_holder.security = ClassSecurityInfo() # Is this OK for security XXX ?
      from Utils import initializeDefaultProperties
      #LOG('initializeDefaultProperties: %s' % ptype, 0, str(prop_holder.__dict__))
      initializeDefaultProperties([prop_holder], object=self)
      #LOG('initializeDefaultProperties: %s' % ptype, 0, str(prop_holder.__dict__))
      # We should now make sure workflow methods are defined
      # and also make sure simulation state is defined
      portal_workflow = getToolByName(self, 'portal_workflow')
      #LOG('getWorkflowsFor', 0, str(portal_workflow.getWorkflowsFor(self)))
      for wf in portal_workflow.getWorkflowsFor(self):
        wf_id = wf.id
        try:
          #LOG('in aq_portal_type %s' % id, 0, "found state workflow %s" % wf.id)
          if wf.__class__.__name__ in ('DCWorkflowDefinition', ):
            # Create state var accessor
            state_var = wf.variables.getStateVar()
            method_id = 'get%s' % UpperCase(state_var)
            if not hasattr(prop_holder, method_id):
              method = WorkflowState.Getter(method_id, wf_id)
              setattr(prop_holder, method_id, method) # Attach to portal_type
              prop_holder.security.declareProtected( Permissions.AccessContentsInformation, method_id )
              #LOG('in aq_portal_type %s' % id, 0, "added state method %s" % method_id)
        except:
          LOG('Base', ERROR,
              'Could not generate worklow state method for workflow %s on class %s.' % (wf_id, ptype),
                error=sys.exc_info())
        try:
          #LOG('in aq_portal_type %s' % id, 0, "found transition workflow %s" % wf.id)
          if wf.__class__.__name__ in ('DCWorkflowDefinition', ):
            for tr_id in wf.transitions.objectIds():
              tdef = wf.transitions.get(tr_id, None)
              if tdef.trigger_type == TRIGGER_WORKFLOW_METHOD:
                method_id = convertToMixedCase(tr_id)
                if not hasattr(klass, method_id):
                  method = WorkflowMethod(klass._doNothing, tr_id)
                  setattr(prop_holder, method_id, method) # Attach to portal_type
                  prop_holder.security.declareProtected( Permissions.AccessContentsInformation, method_id )
                  #LOG('in aq_portal_type %s' % id, 0, "added transition method %s" % method_id)
                else:
                  # Wrap method into WorkflowMethod is needed
                  method = getattr(klass, method_id)
                  if callable(method):
                    if not isinstance(method, WorkflowMethod):
                      setattr(klass, method_id, WorkflowMethod(method, method_id))
          elif wf.__class__.__name__ in ('InteractionWorkflowDefinition', ):
            for tr_id in wf.interactions.objectIds():
              tdef = wf.interactions.get(tr_id, None)
              if tdef.trigger_type == TRIGGER_WORKFLOW_METHOD:
                for imethod_id in tdef.method_id:
                  method_id = imethod_id
                  if not hasattr(klass, method_id):
                    method = WorkflowMethod(klass._doNothing, imethod_id)
                    setattr(prop_holder, method_id, method) # Attach to portal_type
                    prop_holder.security.declareProtected( Permissions.AccessContentsInformation, method_id )
                    #LOG('in aq_portal_type %s' % id, 0, "added interaction method %s" % method_id)
                  else:
                    # Wrap method into WorkflowMethod is needed
                    method = getattr(klass, method_id)
                    if callable(method):
                      if not isinstance(method, WorkflowMethod):
                        setattr(klass, method_id, WorkflowMethod(method, method_id))
        except:
          LOG('Base', ERROR,
              'Could not generate worklow transition methods for workflow %s on class %s.' % (wf_id, klass),
                error=sys.exc_info())


class Base( CopyContainer, PortalContent, ActiveObject, ERP5PropertyManager ):
  """
    This is the base class for all ERP5 Zope objects.
    It defines object attributes which are necessary to implement
    relations and data synchronisation

    id  --  the standard object id
    rid --  the standard object id in the master ODB the object was
        subsribed from
    uid --  a global object id which is unique to each ZODB
    sid --  the id of the subscribtion/syncrhonisation object which
        this object was generated from

    sync_status -- The status of this document in the synchronization
             process (NONE, SENT, ACKNOWLEDGED, SYNCHRONIZED)
             could work as a workflow but CPU expensive


    TODO:

      - assess / fix atomicity

      - assess / fix uid during synchronisation / import
  """
  meta_type = 'ERP5 Base Object'
  portal_type = 'Base Object'
  #_local_properties = () # no need since getattr
  isPortalContent = 1 # All those attributes should become a methods
  isRADContent = 1    #
  isCapacity = 0      #
  isCategory = 0      #
  isBaseCategory = 0  #
  isMovement = 0      #
  isDelivery = 0      #
  isIndexable = 1     # If set to 0, reindexing will not happen (useful for optimization)
  is_predicate = 0    # 
  
  # Declarative security
  security = ClassSecurityInfo()

  # Declarative properties
  property_sheets = ( PropertySheet.Base
                      , )

  # We want to use a default property view
  manage_propertiesForm = DTMLFile( 'dtml/properties', _dtmldir )

  security.declareProtected( Permissions.AccessContentsInformation, 'test_dyn' )
  def test_dyn(self):
    """
    """
    initializeClassDynamicProperties(self, self.__class__)

  def _propertyMap(self):
    """ Method overload - properties are now defined on the ptype """
    global aq_portal_type
    ptype = self.portal_type
    #LOG('_propertyMap',0,ptype)
    self._aq_dynamic('id') # Make sure aq_dynamic has been called once
    if aq_portal_type.has_key(ptype):
      #LOG('_propertyMap ptype',0,list(getattr(aq_portal_type[ptype], '_properties', ())))
      return tuple(list(getattr(aq_portal_type[ptype], '_properties', ())) +
                   list(getattr(self, '_local_properties', ())))
    return ERP5PropertyManager._propertyMap(self)

  def _aq_dynamic(self, id):
    global aq_portal_type
    ptype = self.portal_type
   
    #LOG("In _aq_dynamic", 0, str((id, ptype, self)))
   
    # If this is a portal_type property and everything is already defined
    # for that portal_type, try to return a value ASAP
    if aq_portal_type.has_key(ptype):
      return getattr(aq_portal_type[ptype], id, None)

    # Proceed with property generation
    global aq_method_generated, aq_related_generated
    klass = self.__class__
    generated = 0 # Prevent infinite loops

    # Generate class methods
    if not aq_method_generated.has_key(klass):
      try:
        initializeClassDynamicProperties(self, klass)
      except:
        LOG('_aq_dynamic',0,'error in initializeClassDynamicProperties', error=sys.exc_info())
      generated = 1

    # Generate portal_type methods
    if not aq_portal_type.has_key(ptype):
      try:
        initializePortalTypeDynamicProperties(self, klass, ptype)
        #LOG('_aq_dynamic for %s' % ptype,0, aq_portal_type[ptype].__dict__.keys())
      except:
        LOG('_aq_dynamic',0,'error in initializePortalTypeDynamicProperties', error=sys.exc_info())
      generated = 1

    # Generate Related Accessors
    if not aq_related_generated:
      from Utils import createRelatedValueAccessors
      aq_related_generated = 1
      generated = 1
      portal_categories = getToolByName(self, 'portal_categories', None)
      generated_bid = {}
      for id, ps in PropertySheet.__dict__.items():
        if id[0] != '_':
          for bid in getattr(ps, '_categories', ()):
            if bid not in generated_bid:
              #LOG( "Create createRelatedValueAccessors %s" % bid,0,'')
              createRelatedValueAccessors(Base, bid)
	      generated_bid[bid] = 1

    # Always try to return something after generation
    if generated:
      return getattr(self, id)

    # Proceed with standard acquisition
    return None


  # Constructor
  def __init__(self, id, uid=None, rid=None, sid=None, **kw):
    self.id = id
    if uid is not None :
      self.uid = uid # Else it will be generated when we need it
    self.sid = sid

  # XXX This is necessary to override getId which is also defined in SimpleItem.
  security.declareProtected( Permissions.AccessContentsInformation, 'getId' )
  for prop in PropertySheet.Base._properties:
    if prop['id'] == 'id':
      getId = BaseAccessor.Getter('getId', 'id', prop['type'],
                                  default_value = prop.get('default'), storage_id = prop.get('storage_id'))
      break

  # Debug
  def getOid(self):
    """
      Return ODB oid
    """
    return self._p_oid

  # Utils
  def _getCategoryTool(self):
    return aq_inner(self.getPortalObject().portal_categories)

  def _doNothing(self):
    # A method which does nothing (and can be used to build WorkflowMethods which trigger worklow transitions)
    pass

  # Generic accessor
  def _getDefaultAcquiredProperty(self, key, default_value, null_value,
        base_category=None, portal_type=None, copy_value=0, mask_value=0, sync_value=0,
        accessor_id=None, depends=None, storage_id=None, alt_accessor_id=None,
        is_list_type=0, is_tales_type=0):
    """
      This method implements programmable acquisition of values in ERP5.

      The principle is that some object attributes should be looked up,
      copied or synchronized from the values of another object which relates
      to the first thereof.

      The parameters which define value acquisition are:

      base_category --    a single base category or a list of base categories
                          to look up related objects

      portal_type   --    a single portal type or a list of portal types to filter the
                          list of related objects

      copy_value    --    if set to 1, the looked up value will be copied
                          as an attribute of self

      mask_value    --    if set to 1, the value of the attribute of self
                          has priority on the looked up value

      sync_value    --    if set to 1, keep self and looked up value in sync

      accessor_id   --    the id of the accessor to call on the related filtered objects

      depends       --    a list of parameters to propagate in the look up process

      The purpose of copy_value / mask_value / sync_value is to solve issues
      related to relations and synchronisation of data. copy_value determines
      if a value should be copied as an attribute of self. Copying a value is
      useful for example when we do invoices and want to remember the price at
      a given point of time. mask_value allows to give priority to the value
      holded by self, rather than to the lookup through related objects.
      This is for example useful for invoices (again) for which we want the value
      not to change in time.

      Another case is the case of independent modules on multiple Zope. If for example
      a sales opportunity modules runs on a Zope No1 and an Organisation module runs
      on a Zope No 2. We want to enter peoples's names on the Zope No1. They will be entered
      as strings and stored as such in attributes. When such opportunities are synchronized
      on the Zope No 2, we want to be able to augment content locally by adding some
      category information (in order to say for example that M. Lawno is client/person/23)
      and eventually want M. Lawno to be displayed as "James Lawno". So, we want to give
      priority to the looked up attribute rather than to the attribute. However,
      we may want Zope No 1 to still display "James Lawno" as "M. Lawno". This means
      that we do not want to synchronize back this attribute.

      Other case : we add relation after entering information...

      Other case : we want to change the phone number of a related object without
      going to edit the related object

    """
    # Push context to prevent loop
    # We use TRANSACTION but should use REQUEST
    from Globals import get_request
    TRANSACTION = get_transaction()
    if not hasattr(TRANSACTION, '_erp5_acquisition_stack'): TRANSACTION._erp5_acquisition_stack = {}
    if type(portal_type) is type([]):
      portal_type = tuple(portal_type)
    acquisition_key = ('_getDefaultAcquiredProperty', self.getPath(), key, base_category,
                       portal_type, copy_value, mask_value, sync_value,
                       accessor_id, depends, storage_id, alt_accessor_id, is_list_type, is_tales_type)
    if TRANSACTION._erp5_acquisition_stack.has_key(acquisition_key): return null_value
    TRANSACTION._erp5_acquisition_stack[acquisition_key] = 1

    #LOG("Get Acquired Property key",0,str(key))
    if storage_id is None: storage_id=key
    #LOG("Get Acquired Property storage_id",0,str(storage_id))
    # If we hold an attribute and mask_value is set, return the attribute
    value = getattr(self, storage_id, None)
    if mask_value and value is not None:
      # Pop context
      del TRANSACTION._erp5_acquisition_stack[acquisition_key]
      if is_tales_type:
        expression = Expression(value)
        econtext = createExpressionContext(self)
        return expression(econtext)
      else:
        return value
    # Retrieve the list of related objects
    #LOG("Get Acquired Property self",0,str(self))
    #LOG("Get Acquired Property portal_type",0,str(portal_type))
    #LOG("Get Acquired Property base_category",0,str(base_category))
    #super_list = self._getValueList(base_category, portal_type=portal_type) # We only do a single jump
    super_list = self._getAcquiredValueList(base_category, portal_type=portal_type) # Full acquisition
    super_list = filter(lambda o: o.getPhysicalPath() != self.getPhysicalPath(), super_list) # Make sure we do not create stupid loop here
    #LOG("Get Acquired Property super_list",0,str(super_list))
    #LOG("Get Acquired Property accessor_id",0,str(accessor_id))
    if len(super_list) > 0:
      super = super_list[0]
      # Retrieve the value
      if accessor_id is None:
        value = super.getProperty(key)
      else:
        method = getattr(super, accessor_id)
        value = method() # We should add depends here XXXXXX
                         # There is also a strong risk here of infinite loop
      if copy_value:
        if getattr(self, storage_id, None) is None:
          # Copy the value if it does not already exist as an attribute of self
          # Like in the case of orders / invoices
          setattr(self, storage_id, value)
      if is_list_type:
        # We must provide the first element of the acquired list
        if value is None:
          result = None
        else:
          if type(value) is type([]) or type(value) is type(()):
            if len(value) is 0:
              result = None
            else:
              result = value[0]
          else:
            result = value
      else:
        # Value is a simple type
        result = value
    else:
      result = None
    if result is not None:
      # Pop context
      del TRANSACTION._erp5_acquisition_stack[acquisition_key]
      return result
    else:
      #LOG("alt_accessor_id",0,str(alt_accessor_id))
      if alt_accessor_id is not None:
        for id in alt_accessor_id:
          #LOG("method",0,str(id))
          method = getattr(self, id, None)
          if callable(method):
            result = method()
            if result is not None:
              if is_list_type:
                if type(result) is type([]) or type(result) is type(()):
                  # We must provide the first element of the alternate result
                  if len(result) > 0:
                    # Pop context
                    del TRANSACTION._erp5_acquisition_stack[acquisition_key]
                    return result[0]
                else:
                  # Pop context
                  del TRANSACTION._erp5_acquisition_stack[acquisition_key]
                  return result
              else:
                # Pop context
                del TRANSACTION._erp5_acquisition_stack[acquisition_key]
                # Result is a simple type
                return result

      if copy_value:
        # Pop context
        del TRANSACTION._erp5_acquisition_stack[acquisition_key]
        return getattr(self,storage_id, default_value)
      else:
        # Pop context
        del TRANSACTION._erp5_acquisition_stack[acquisition_key]
        # Return the default value defined at the class level XXXXXXXXXXXXXXX
        return default_value

  def _getAcquiredPropertyList(self, key, default_value, null_value,
     base_category, portal_type=None, copy_value=0, mask_value=0, sync_value=0, append_value=0,
     accessor_id=None, depends=None, storage_id=None, alt_accessor_id=None,
     is_list_type=0, is_tales_type=0):
    """
      Default accessor. Implements the default
      attribute accessor.

      portal_type
      copy_value
      depends

    """
    # Push context to prevent loop
    from Globals import get_request
    TRANSACTION = get_transaction()
    if not hasattr(TRANSACTION, '_erp5_acquisition_stack'): TRANSACTION._erp5_acquisition_stack = {}
    acquisition_key = ('_getAcquiredPropertyList', self.getPath(), key, base_category,
                       portal_type, copy_value, mask_value, sync_value,
                       accessor_id, depends, storage_id, alt_accessor_id, is_list_type, is_tales_type)
    if TRANSACTION._erp5_acquisition_stack.has_key(acquisition_key): return null_value
    TRANSACTION._erp5_acquisition_stack[acquisition_key] = 1

    if storage_id is None: storage_id=key
    value = getattr(self, storage_id, None)
    if mask_value and value is not None:
      # Pop context
      del TRANSACTION._erp5_acquisition_stack[acquisition_key]
      if is_tales_type:
        expression = Expression(value)
        econtext = createExpressionContext(self)
        return expression(econtext)
      else:
        return value
    super_list = self._getAcquiredValueList(base_category, portal_type=portal_type) # Full acquisition
    super_list = filter(lambda o: o.getPhysicalPath() != self.getPhysicalPath(), super_list) # Make sure we do not create stupid loop here
    if len(super_list) > 0:
      value = []
      for super in super_list:
        if accessor_id is None:
          if is_list_type:
            result = super.getPropertyList(key)
            if type(result) is type([]) or type(result) is type(()):
              value += result
            else:
              value += [result]
          else:
            value += [super.getProperty(key)]
        else:
          method = getattr(super, accessor_id)
          if is_list_type:
            result = method() # We should add depends here
            if type(result) is type([]) or type(result) is type(()):
              value += result
            else:
              value += [result]
          else:
            value += [method()] # We should add depends here
      if copy_value:
        if not hasattr(self, storage_id):
          setattr(self, value)
      # Pop context
      del TRANSACTION._erp5_acquisition_stack[acquisition_key]
      return value
    else:
      # ?????
      if copy_value:
        # Pop context
        del TRANSACTION._erp5_acquisition_stack[acquisition_key]
        return getattr(self,storage_id, default_value)
      else:
        # Pop context
        del TRANSACTION._erp5_acquisition_stack[acquisition_key]
        return default_value

  security.declareProtected( Permissions.AccessContentsInformation, 'getProperty' )
  def getProperty(self, key, d=None, **kw):
    """
      Previous Name: getValue

      Generic accessor. Calls the real accessor
    """
    accessor_name = 'get' + UpperCase(key)
    aq_self = aq_base(self)
    if hasattr(aq_self, accessor_name):
      method = getattr(self, accessor_name)
      return method(**kw)
    # Try to get a portal_type property (Implementation Dependent)
    global aq_portal_type
    if not aq_portal_type.has_key(self.portal_type):
      try:
        self._aq_dynamic(accessor_name)
      except AttributeError:
        pass
    if hasattr(aq_portal_type[self.portal_type], accessor_name):
      method = getattr(self, accessor_name)
      return method(**kw)
    #elif hasattr(aq_self, key):
    #  value = getattr(aq_self, key)
    #  if callable(value): value = value()
    #  return value
    else:
      return ERP5PropertyManager.getProperty(self, key, d=d, **kw)

  security.declareProtected( Permissions.AccessContentsInformation, 'getPropertyList' )
  def getPropertyList(self, key, d=None):
    """
      Previous Name: getValue

      Generic accessor. Calls the real accessor
    """
    return self.getProperty('%s_list' % key)

  security.declareProtected( Permissions.ModifyPortalContent, 'setProperty' )
  def setProperty(self, key, value, type='string', **kw):
    """
      Previous Name: setValue

      New Name: we use the naming convention of
      /usr/lib/zope/lib/python/OFS/PropertySheets.py

      TODO: check possible conflicts

      Generic accessor. Calls the real accessor
    """
    self._setProperty(key,value,type=type, **kw)
    self.reindexObject()

  security.declareProtected( Permissions.ModifyPortalContent, '_setProperty' )
  def _setProperty(self, key, value, type='string', **kw):
    """
      Previous Name: _setValue

      Generic accessor. Calls the real accessor

      **kw allows to call setProperty as a generic setter (ex. setProperty(value_uid, portal_type=))
    """
    #LOG('_setProperty', 0, 'key = %r, value = %r, type = %r, kw = %r' % (key, value, type, kw))
    #LOG('In _setProperty',0, str(key))
    if type is not 'string': # Speed
      if type in list_types: # Patch for OFS PropertyManager
        key += '_list'
    accessor_name = '_set' + UpperCase(key)
    aq_self = aq_base(self)
    # We must use aq_self
    # since we will change the value on self
    # rather than through implicit aquisition
    if hasattr(aq_self, accessor_name):
      #LOG("Calling: ",0, '%r %r ' % (accessor_name, key))
      method = getattr(self, accessor_name)
      method(value, **kw)
      return
      """# Make sure we change the default value again
      # if it was provided at the same time
      new_key = 'default_%s' % key
      if kw.has_key(new_key):
        accessor_name = '_set' + UpperCase(new_key)
        if hasattr(self, accessor_name):
          method = getattr(self, accessor_name)
          method(kw[new_key])"""
    public_accessor_name = 'set' + UpperCase(key)
    if hasattr(aq_self, public_accessor_name):
      #LOG("Calling: ",0, '%r %r ' % (public_accessor_name, key))
      method = getattr(self, public_accessor_name)
      method(value, **kw)
      return
    # Try to get a portal_type property (Implementation Dependent)
    global aq_portal_type
    if not aq_portal_type.has_key(self.portal_type):
      self._aq_dynamic('id') # Make sure _aq_dynamic has been called once
    if hasattr(aq_portal_type[self.portal_type], accessor_name):
      method = getattr(self, accessor_name)
      method(value, **kw)
      return
    if hasattr(aq_portal_type[self.portal_type], public_accessor_name):
      method = getattr(self, public_accessor_name)
      method(value, **kw)
      return
    # Finaly use standard PropertyManager
    #LOG("Changing attr: ",0, key)
    try:
      ERP5PropertyManager._setProperty(self, key, value, type=type)
    except:
      # This should be removed if we want strict property checking
      setattr(self, key, value)

  def _setPropValue(self, key, value, **kw):
    #LOG('_setPropValue', 0, 'self = %r, key = %r, value = %r, kw = %r' % (self, key, value, kw))
    self._wrapperCheck(value)
    if type(value) == type([]):
      value = tuple(value)
    accessor_name = '_set' + UpperCase(key)
    aq_self = aq_base(self)
    # We must use aq_self
    # since we will change the value on self
    # rather than through implicit aquisition
    if hasattr(aq_self, accessor_name):
      #LOG("Calling: ",0, '%r %r ' % (accessor_name, key))
      method = getattr(self, accessor_name)
      method(value, **kw)
      return
      """# Make sure we change the default value again
      # if it was provided at the same time
      new_key = 'default_%s' % key
      if kw.has_key(new_key):
        accessor_name = '_set' + UpperCase(new_key)
        if hasattr(self, accessor_name):
          method = getattr(self, accessor_name)
          method(kw[new_key])"""
    public_accessor_name = 'set' + UpperCase(key)
    if hasattr(aq_self, public_accessor_name):
      #LOG("Calling: ",0, '%r %r ' % (public_accessor_name, key))
      method = getattr(self, public_accessor_name)
      method(value, **kw)
      return
    # Try to get a portal_type property (Implementation Dependent)
    global aq_portal_type
    if not aq_portal_type.has_key(self.portal_type):
      self._aq_dynamic('id') # Make sure _aq_dynamic has been called once
    if hasattr(aq_portal_type[self.portal_type], accessor_name):
      method = getattr(self, accessor_name)
      method(value, **kw)
      return
    if hasattr(aq_portal_type[self.portal_type], public_accessor_name):
      method = getattr(self, public_accessor_name)
      method(value, **kw)
      return
    # Finaly use standard PropertyManager
    #LOG("Changing attr: ",0, key)
    try:
      ERP5PropertyManager._setPropValue(self, key, value)
    except:
      # This should be removed if we want strict property checking
      setattr(self, key, value)

  security.declareProtected( Permissions.View, 'hasProperty' )
  def hasProperty(self, key):
    """
      Previous Name: hasValue

      Generic accessor. Calls the real accessor
      and returns 0 if it fails
    """
    accessor_name = 'has' + UpperCase(key)
    if hasattr(self, accessor_name):
      method = getattr(self, accessor_name)
      try:
        return method()
      except:
        return 0
    else:
      for p_id in self.propertyIds():
        if key==p_id:
          return 1
      return 0

  # Accessors are not workflow methods by default
  # Ping provides a dummy method to trigger automatic methods
  # XXX : maybe an empty edit is enough (self.edit())
  def ping(self):
    pass

  ping = WorkflowMethod( ping )

  # Object attributes update method
  security.declarePrivate( '_edit' )
  def _edit(self, REQUEST=None, force_update = 0, reindex_object = 0, **kw):
    """
      Generic edit Method for all ERP5 object
      The purpose of this method is to update attributed, eventually do
      some kind of type checking according to the property sheet and index
      the object.

      Each time attributes of an object are updated, they should
      be updated through this generic edit method
    """
    try:
      categoryIds = self._getCategoryTool().getBaseCategoryIds()
    except:
      categoryIds = []
    id_changed = 0
    self._v_modified_property_dict = {}
    for key in kw.keys():
      #if key in categoryIds:
      #  self._setCategoryMembership(key, kw[key])
      if key != 'id':
        # We only change if the value is different
        # This may be very long....
        accessor_name = 'get' + UpperCase(key)
        if force_update:
          old_value = None
        elif hasattr(self, accessor_name):
          #LOG("Calling: ",0, accessor_name)
          method = getattr(self, accessor_name)
          old_value = method() # XXX Why not use getProperty ???
          #LOG("Old value: ",0, str(old_value))
          #LOG("New value: ",0, str(kw[key]))
        else:
          old_value = None
        if old_value != kw[key] or force_update:
          self._v_modified_property_dict[key] = old_value # We keep in a thread var the previous values - this can be useful for interaction workflow to implement lookups
          self._setProperty(key, kw[key])
      elif self.id != kw['id']:
        self.recursiveFlushActivity(invoke=1) # Do not rename until everything flushed
        previous_relative_url = self.getRelativeUrl()
        self.aq_parent.manage_renameObjects([self.id], [kw['id']])
        new_relative_url = self.getRelativeUrl()
        id_changed = 1
    if reindex_object: self.reindexObject()
    if id_changed:
      if reindex_object: self.flushActivity(invoke=1) # Required if we wish that news ids appear instantly
      #if self.isIndexable:
      #  self.moveObject()             # Required if we wish that news ids appear instantly
      #if hasattr(aq_base(self), 'recursiveMoveObject'):
      #  self.recursiveMoveObject()    # Required to make sure path of subobjects is updated
      self.activate().updateRelatedContent(previous_relative_url, new_relative_url)
      #self.activate().recursiveImmediateReindexObject() # Required to update path / relative_url of subobjects

  security.declareProtected( Permissions.ModifyPortalContent, 'setId' )
  def setId(self, id, reindex = 1):
    """
        changes id of an object by calling the Zope machine
    """
    self.recursiveFlushActivity(invoke=1) # Do not rename until everything flushed
    previous_relative_url = self.getRelativeUrl()
    self.aq_parent.manage_renameObjects([self.id], [id])
    new_relative_url = self.getRelativeUrl()
    if reindex: self.flushActivity(invoke=1) # Required if we wish that news ids appear instantly
    self.activate().updateRelatedContent(previous_relative_url, new_relative_url)

  security.declareProtected( Permissions.ModifyPortalContent, 'updateRelatedContent' )
  def updateRelatedContent(self, previous_category_url, new_category_url):
    """
        updateRelatedContent is implemented by portal_categories
    """
    self._getCategoryTool().updateRelatedContent(self, previous_category_url, new_category_url)

  security.declareProtected( Permissions.ModifyPortalContent, 'edit' )
  def edit(self, REQUEST=None, force_update = 0, reindex_object=1, **kw):
    return self._edit(REQUEST=REQUEST, force_update=force_update, reindex_object=reindex_object, **kw)

  edit = WorkflowMethod( edit )

  # Accessing object property Ids
  security.declareProtected( Permissions.View, 'getPropertyIdList' )
  def getPropertyIdList(self):
    return propertyIds()
    #return map(lambda p: p['id'], self.__class__._properties)

  # Catalog Related
  security.declareProtected( Permissions.View, 'getObject' )
  def getObject(self, relative_url = None, REQUEST=None):
    """
      Returns self - useful for ListBox when we do not know
      if the getObject is called on a brain object or on the actual object
    """
    return self

  security.declareProtected( Permissions.AccessContentsInformation, 'asParentSqlExpression' )
  def getParentSqlExpression(self, table = 'catalog', strict_membership = 0):
    """
      Builds an SQL expression to search children and subclidren      
    """
    return "%s.parent_uid = %s" % (table, self.getUid())
    
  security.declareProtected( Permissions.AccessContentsInformation, 'getParentUid' )
  def getParentUid(self):
    """
      Returns the UID of the parent of the current object. Used
      for the implementation of the ZSQLCatalog based listing
      of objects.
    """
    parent = self.aq_inner.aq_parent
    uid = getattr(aq_base(parent), 'uid', None)
    if uid is None:
      parent.immediateReindexObject() # Required with deferred indexing
      uid = getattr(aq_base(parent), 'uid', None)
      if uid is None:
        LOG('Failed twice getParentUid', 0, str((self.getPhysicalPath(),parent.getPhysicalPath())))
        raise DeferredCatalogError('Could neither access parent uid nor generate it', self)
    return uid

  security.declareProtected( Permissions.AccessContentsInformation, 'getParentTitleOrId' )
  def getParentTitleOrId(self):
    """
      Returns the title or the id of the parent
    """
    return self.getParent().getTitleOrId()

  security.declareProtected( Permissions.AccessContentsInformation, 'getParentValue' )
  def getParentValue(self):
    """
      Returns the parent of the current object.
    """
    return self.aq_parent

  security.declareProtected( Permissions.AccessContentsInformation, 'getParent' )
  getParent = getParentValue # Compatibility
    
  security.declareProtected( Permissions.AccessContentsInformation, 'getUid' )
  def getUid(self):
    """
      Returns the UID of the object. Eventually reindexes
      the object in order to make sure there is a UID
      (useful for import / export).

      WARNING : must be updates for circular references issues
    """
    #if not hasattr(self, 'uid'):
    #  self.reindexObject()
    uid = getattr(aq_base(self), 'uid', None)
    if uid is None:
      self.uid = self.portal_catalog.newUid()
      uid = getattr(aq_base(self), 'uid', None)
      if uid is None:
        raise DeferredCatalogError('Could neither access uid nor generate it', self)
    return uid

  security.declareProtected(Permissions.AccessContentsInformation, 'getLogicalPath')
  def getLogicalPath(self, REQUEST=None) :
    """
      Returns the absolute path of an object, using titles when available
    """
    pathlist = self.getPhysicalPath()
    objectlist = [self.getPhysicalRoot()]
    for element in pathlist[1:] :
      objectlist.append(objectlist[-1][element])
    return '/' + join([object.getTitle() for object in objectlist[1:]], '/')

  security.declareProtected(Permissions.AccessContentsInformation, 'getPath')
  def getPath(self, REQUEST=None):
    """
      Returns the absolute path of an object
    """
    return join(self.getPhysicalPath(),'/')

  # This should be the new name
  security.declareProtected(Permissions.AccessContentsInformation, 'getUrl')
  getUrl = getPath

  security.declareProtected(Permissions.AccessContentsInformation, 'getRelativeUrl')
  def getRelativeUrl(self):
    """
      Returns the absolute path of an object
    """
    return self.portal_url.getRelativeUrl(self)

  security.declareProtected(Permissions.AccessContentsInformation, 'getPortalObject')
  def getPortalObject(self):
    """
      Returns the portal object
    """
    return self.portal_url.getPortalObject()

  security.declareProtected(Permissions.AccessContentsInformation, 'getWorkflowIds')
  def getWorkflowIds(self):
    """
      Returns the list of workflows
    """
    return self.portal_workflow.getWorkflowIds()

  # Object Database Management
  security.declareProtected( Permissions.ManagePortal, 'upgrade' )
  def upgrade(self, REQUEST=None):
    """
      Upgrade an object and do whatever necessary
      to make sure it is compatible with the latest
      version of a class
    """
    pass

  # For Debugging
  security.declareProtected( Permissions.View, 'showDict' )
  def showDict(self):
    """
      Returns the dictionnary of the object
      Only for debugging
    """
    return self.__dict__

  # Private accessors for the implementation of relations based on
  # categories
  security.declareProtected( Permissions.ModifyPortalContent, '_setValue' )
  def _setValue(self, id, target, spec=(), filter=None, portal_type=()):
    if type(target) is type('a'):
      # We have been provided a string
      path = target
    elif type(target) is type(('a','b')) or type(target) is type(['a','b']):
      # We have been provided a list or tuple
      path_list = []
      for target_item in target:
        if type(target_item) is type('a'):
          path_list += [target_item]
        else:
          path = target_item.getRelativeUrl()
          path_list += [path]
      path = path_list
    else:
      # We have been provided an object
      # Find the object
      path = target.getRelativeUrl()
    self._setCategoryMembership(id, path, spec=spec, filter=filter, portal_type=portal_type)

  security.declareProtected( Permissions.ModifyPortalContent, '_setDefaultValue' )
  _setDefaultValue = _setValue

  security.declareProtected( Permissions.ModifyPortalContent, '_setValueList' )
  _setValueList = _setValue

  security.declareProtected( Permissions.ModifyPortalContent, 'setValue' )
  def setValue(self, id, target, spec=(), filter=None, portal_type=()):
    self._setValue(id, target, spec=spec, filter=filter, portal_type=portal_type)
    self.reindexObject()

  security.declareProtected( Permissions.ModifyPortalContent, 'setDefaultValue' )
  setDefaultValue = setValue

  security.declareProtected( Permissions.ModifyPortalContent, 'setValueList' )
  setValueList = setValue

  security.declareProtected( Permissions.View, '_getDefaultValue' )
  def _getDefaultValue(self, id, spec=(), filter=None, portal_type=()):
    path = self._getDefaultCategoryMembership(id, spec=spec, filter=filter,
                                      portal_type=portal_type,base=1)
    if path is None:
      return None
    else:
      return self._getCategoryTool().resolveCategory(path)

  security.declareProtected( Permissions.View, 'getDefaultValue' )
  getDefaultValue = _getDefaultValue

  security.declareProtected( Permissions.View, '_getValueList' )
  def _getValueList(self, id, spec=(), filter=None, portal_type=()):
    ref_list = []
    for path in self._getCategoryMembershipList(id, spec=spec, filter=filter,
                                                  portal_type=portal_type, base=1):
      # LOG('_getValueList',0,str(path))
      try:
        value = self._getCategoryTool().resolveCategory(path)
        if value is not None: ref_list.append(value)
      except:
        LOG("ERP5Type WARNING",0,"category %s has no object value" % path)
    return ref_list

  security.declareProtected( Permissions.View, 'getValueList' )
  getValueList = _getValueList

  security.declareProtected( Permissions.View, '_getDefaultAcquiredValue' )
  def _getDefaultAcquiredValue(self, id, spec=(), filter=None, portal_type=()):
    path = self._getDefaultAcquiredCategoryMembership(id, spec=spec, filter=filter,
                                                  portal_type=portal_type, base=1)
    # LOG("_getAcquiredDefaultValue",0,str(path))
    if path is None:
      return None
    else:
      return self._getCategoryTool().resolveCategory(path)

  security.declareProtected( Permissions.View, 'getDefaultAcquiredValue' )
  getDefaultAcquiredValue = _getDefaultAcquiredValue

  security.declareProtected( Permissions.View, '_getAcquiredValueList' )
  def _getAcquiredValueList(self, id, spec=(), filter=None, **kw):
    ref_list = []
    for path in self._getAcquiredCategoryMembershipList(id, base=1,
                                                spec=spec,  filter=filter, **kw):
      try:
        value = self._getCategoryTool().resolveCategory(path)
        if value is not None: ref_list.append(value)
      except:
        LOG("ERP5Type WARNING",0,"category %s has no object value" % path)
    return ref_list

  security.declareProtected( Permissions.View, 'getAcquiredValueList' )
  getAcquiredValueList = _getAcquiredValueList

  security.declareProtected( Permissions.View, '_getDefaultRelatedValue' )
  def _getDefaultRelatedValue(self, id, spec=(), filter=None, portal_type=()):
    value_list =self._getRelatedValueList(id, spec=spec, filter=filter, portal_type=portal_type)
    try:
      return value_list[0]
    except:
      return None

  security.declareProtected( Permissions.View, 'getDefaultRelatedValue' )
  getDefaultRelatedValue = _getDefaultRelatedValue

  security.declareProtected( Permissions.View, '_getRelatedValueList' )
  def _getRelatedValueList(self, id, spec=(), filter=None, portal_type=()):
    return self._getCategoryTool().getRelatedValueList(self, id, spec=spec, filter=filter, portal_type=portal_type)

  security.declareProtected( Permissions.View, 'getRelatedValueList' )
  getRelatedValueList = _getRelatedValueList

  security.declareProtected( Permissions.View, 'getValueUids' )
  def getValueUids(self, id, spec=(), filter=None, portal_type=()):
    uid_list = []
    for o in self._getValueList(id, spec=spec, filter=filter, portal_type=portal_type):
      uid_list.append(o.getUid())
    return uid_list

  security.declareProtected( Permissions.ModifyPortalContent, '_setValueUids' )
  def _setValueUids(self, id, uids, spec=(), filter=None, portal_type=()):
    # We must do an ordered list so we can not use the previous method
    # self._setValue(id, self.portal_catalog.getObjectList(uids), spec=spec)
    references = []
    for uid in uids:
      references.append(self.portal_catalog.getObject(uid))
    self._setValue(id, references, spec=spec, filter=filter, portal_type=portal_type)

  security.declareProtected( Permissions.ModifyPortalContent, 'setValueUids' )
  def setValueUids(self, id, uids, spec=(), filter=None, portal_type=()):
    self._setValueUids(id, uids, spec=spec, filter=filter, portal_type=portal_type)
    self.reindexObject()

  security.declareProtected( Permissions.ModifyPortalContent, '_addValue' )
  def _addValue(self, id, value, spec=(), filter=None, portal_type=()):
    pass

  security.declareProtected( Permissions.ModifyPortalContent, '_delValue' )
  def _delValue(self, id, value, spec=(), filter=None, portal_type=()):
    pass

  security.declareProtected( Permissions.ModifyPortalContent, 'updateRelation' )
  def updateRelation(self, key, value, REQUEST):
    return REQUEST

  # Private accessors for the implementation of categories
  security.declareProtected( Permissions.ModifyPortalContent, '_addToCategory' )
  def _addToCategory(self, category, node):
    pass

  security.declareProtected( Permissions.ModifyPortalContent, '_delFomCategory' )
  def _delFomCategory(self, category, node):
    pass

  security.declareProtected( Permissions.ModifyPortalContent, '_setCategoryMembership' )
  def _setCategoryMembership(self, category, node_list, spec=(),
                                             filter=None, portal_type=(), base=0):
    self._getCategoryTool().setCategoryMembership(self, category, node_list,
                       spec=spec, filter=filter, portal_type=portal_type, base=base)
    #self.activate().edit() # Do nothing except call workflow method
    # XXX This is a problem - it is used to circumvent a lack of edit

  security.declareProtected( Permissions.ModifyPortalContent, 'setCategoryMembership' )
  def setCategoryMembership(self, category, node_list, spec=(), base=0):
    self._setCategoryMembership(category,
                      node_list, spec=spec, filter=filter, portal_type=portal_type, base=base)
    self.reindexObject()

  security.declareProtected( Permissions.ModifyPortalContent, '_setDefaultCategoryMembership' )
  def _setDefaultCategoryMembership(self, category, node_list,
                                    spec=(), filter=None, portal_type=(), base=0):
    self._getCategoryTool().setDefaultCategoryMembership(self, category,
                     node_list, spec=spec, filter=filter, portal_type=portal_type, base=base)

  security.declareProtected( Permissions.ModifyPortalContent, 'setDefaultCategoryMembership' )
  def setDefaultCategoryMembership(self, category, node_list,
                                           spec=(), filter=None, portal_type=(), base=0):
    self._setCategoryMembership(category, node_list, spec=spec, filter=filter,
                                                  portal_type=portal_type, base=base)
    self.reindexObject()

  security.declareProtected( Permissions.AccessContentsInformation, '_getCategoryMembershipList' )
  def _getCategoryMembershipList(self, category, spec=(), filter=None, portal_type=(), base=0 ):
    """
      This returns the list of categories for an object
    """
    return self._getCategoryTool().getCategoryMembershipList(self, category, spec=spec,
                                                   filter=filter, portal_type=portal_type, base=base)

  security.declareProtected( Permissions.AccessContentsInformation, 'getCategoryMembershipList' )
  getCategoryMembershipList = _getCategoryMembershipList

  security.declareProtected( Permissions.AccessContentsInformation,
                                               '_getAcquiredCategoryMembershipList' )
  def _getAcquiredCategoryMembershipList(self, category, base=0 , spec=(),
                                              filter=None, **kw ):
    """
      Returns the list of acquired categories
    """
    return self._getCategoryTool().getAcquiredCategoryMembershipList(self,
                             category, base=base, spec=spec, filter=filter, **kw )

  security.declareProtected( Permissions.AccessContentsInformation,
                                           'getAcquiredCategoryMembershipList' )
  getAcquiredCategoryMembershipList = _getAcquiredCategoryMembershipList

  security.declareProtected( Permissions.AccessContentsInformation, '_getCategoryMembershipItemList' )
  def _getCategoryMembershipItemList(self, category, spec=(), filter=None, portal_type=(), base=0):
    membership_list = self._getCategoryMembershipList(category,
                            spec = spec, filter=filter, portal_type=portal_type, base=base)
    return map(lambda x: (x,x), membership_list)

  security.declareProtected( Permissions.AccessContentsInformation,
                                          '_getAcquiredCategoryMembershipItemList' )
  def _getAcquiredCategoryMembershipItemList(self, category, spec=(),
             filter=None, portal_type=(), base=0, method_id=None, sort_id='default'):
    # Standard behaviour - should be OK
    # sort_id should be None for not sort - default behaviour in other methods
    if method_id is None and sort_id in (None, 'default'):
      membership_list = self._getAcquiredCategoryMembershipList(category,
                           spec = spec, filter=filter, portal_type=portal_type, base=base)
      if sort_id == 'default':
        membership_list.sort()
      return map(lambda x: (x,x), membership_list)
    # Advanced behaviour XXX This is new and needs to be checked
    membership_list = self._getAcquiredCategoryMembershipList(category,
                           spec = spec, filter=filter, portal_type=portal_type, base=1)
    for path in membership_list:
      value = self._getCategoryTool().resolveCategory(path)
      if value is not None:
        result += [value]
    result.sort(lambda x, y: cmp(getattr(x,sort_id)(),getattr(y,sort_id)()))
    if method_id is None:
      return map(lambda x: (x,x), membership_list)
    return map(lambda x: (x,getattr(x, method_id)()), membership_list)

  security.declareProtected( Permissions.View, '_getDefaultCategoryMembership' )
  def _getDefaultCategoryMembership(self, category, spec = (), filter=None, portal_type=(), base = 0 ):
    membership = self._getCategoryTool().getCategoryMembershipList(self,
                     category, spec = spec, filter=filter, portal_type=portal_type, base = base)
    if len(membership) > 0:
      return membership[0]
    else:
      return None

  security.declareProtected( Permissions.View, '_getDefaultAcquiredCategoryMembership' )
  def _getDefaultAcquiredCategoryMembership(self, category,
                                        spec=(), filter=None, portal_type=(), base=0):
    membership = self._getAcquiredCategoryMembershipList(category,
                spec=spec, filter=filter, portal_type=portal_type, base=base)
    if len(membership) > 0:
      return membership[0]
    else:
      return None

  security.declareProtected( Permissions.View, 'getDefaultAcquiredCategoryMembership' )
  getDefaultAcquiredCategoryMembership = _getDefaultAcquiredCategoryMembership

  security.declareProtected( Permissions.View, 'getCategoryList' )
  def getCategoryList(self):
    """
      Returns the list of local categories
    """
    return self._getCategoryTool().getCategoryList(self)

  security.declareProtected( Permissions.View, '_getCategoryList' )
  def _getCategoryList(self):
    return self._getCategoryTool()._getCategoryList(self)

  security.declareProtected( Permissions.View, 'getAcquiredCategoryList' )
  def getAcquiredCategoryList(self):
    """
      Returns the list of acquired categories
    """
    return self._getCategoryTool().getAcquiredCategoryList(self)

  security.declareProtected( Permissions.View, '_getAcquiredCategoryList' )
  def _getAcquiredCategoryList(self):
    return self._getCategoryTool()._getAcquiredCategoryList(self)

  security.declareProtected( Permissions.ModifyPortalContent, 'setCategoryList' )
  def setCategoryList(self, path_list):
    self._setCategoryList(path_list)
    self.reindexObject()

  security.declareProtected( Permissions.ModifyPortalContent, '_setCategoryList' )
  def _setCategoryList(self, path_list):
    self.portal_categories._setCategoryList(self, path_list)

  security.declareProtected( Permissions.View, 'getBaseCategoryList' )
  def getBaseCategoryList(self):
    """
      Lists the base_category ids which apply to this instance
    """
    return self._getCategoryTool().getBaseCategoryList(context=self)

  security.declareProtected( Permissions.View, 'getBaseCategoryIds' )
  getBaseCategoryIds = getBaseCategoryList

  security.declareProtected( Permissions.View, 'getBaseCategoryValueList' )
  def getBaseCategoryValueList(self):
    return self._getCategoryTool().getBaseCategoryValues(context=self)

  security.declareProtected( Permissions.View, 'getBaseCategoryValues' )
  getBaseCategoryValues = getBaseCategoryValueList

  security.declareProtected( Permissions.ModifyPortalContent, '_cleanupCategories' )
  def _cleanupCategories(self):
    self._getCategoryTool()._cleanupCategories()

  # Category testing
  security.declareProtected( Permissions.View, 'isMemberOf' )
  def isMemberOf(self, category):
    """
      Tests if an object if member of a given category
    """
    return self._getCategoryTool().isMemberOf(self, category)

  security.declareProtected( Permissions.View, 'isAcquiredMemberOf' )
  def isAcquiredMemberOf(self, category):
    """
      Tests if an object if member of a given category
    """
    return self._getCategoryTool().isAcquiredMemberOf(self, category)

  # Aliases
  security.declareProtected(Permissions.View, 'getTitleOrId')
  def getTitleOrId(self):
    """
      Returns the title or the id if the id is empty
    """
    if self.hasTitle():
      title = str(self.getTitle())
      if title == '' or title is None:
        return self.getId()
      else:
        return title
    return self.getId()

  security.declareProtected( Permissions.View, 'Title' )
  Title = getTitleOrId

  # This method allows to sort objects in list is a more reasonable way
  security.declareProtected(Permissions.View, 'getIntId')
  def getIntId(self):
    try:
      return int(self.getId())
    except:
      return None

  # Default views
  security.declareProtected(Permissions.View, 'list')
  def list(self,reset=0):
        '''
        Returns the default list even if folder_contents is overridden.
        '''
        list_action = _getListFor(self)
        if getattr(aq_base(list_action), 'isDocTemp', 0):
            return apply(list_action, (self, self.REQUEST),reset=reset)
        else:
            return list_action(reset=reset)

  # Proxy methods for security reasons
  security.declareProtected(Permissions.AccessContentsInformation, 'getOwnerInfo')
  def getOwnerInfo(self):
    """
    this returns the Owner Info
    """
    return self.owner_info()

  # Missing attributes
  security.declareProtected(Permissions.AccessContentsInformation, 'getPortalType')
  def getPortalType(self):
    """
    This returns the portal_type
    """
    return self.portal_type

  security.declareProtected(Permissions.ModifyPortalContent, 'setPortalType')
  def setPortalType(self, portal_type = None):
    """
    This allows to set the portal_type
    """
    if portal_type is not None:
      self.portal_type = portal_type


  security.declareProtected(Permissions.AccessContentsInformation, 'getMetaType')
  def getMetaType(self):
    """
    This returns the Meta Type
    """
    return self.meta_type

#   def _recursiveApply(self,f):
#     """
#     """
#     error_list = []
#     for o in self.objectValues():
#       try:
#         error_list += f(o)
#         error_list += o.recursiveApply(f)
#       except:
#         LOG('ERP5Type.Base',0,"error in recursiveApply : %s, %s on %s"
#           % (str(sys.exc_type),str(sys.exc_value),o.getPath()))
#
#     return error_list
#
#   def recursiveApply(self,f):
#     """
#       This allows to apply a function, f, on the current object
#       and all subobjects.
#
#       This function can be created inside a python script on the
#       zope management interface, then we just have to call recursiveApply.
#     """
#     return self._recursiveApply(f)

  # Content consistency implementation
  security.declarePrivate('_checkConsistency')
  def _checkConsistency(self, fixit=0):
    """
    Check the constitency of objects.

    Private method.
    """
    return []

  security.declarePrivate('_fixConsistency')
  def _fixConsistency(self):
    """
    Fix the constitency of objects.

    Private method.
    """
    return self._checkConsistency(fixit=1)

  security.declareProtected(Permissions.AccessContentsInformation, 'checkConsistency')
  def checkConsistency(self, fixit=0):
    """
    Check the constitency of objects.

    For example we can check if every Organisation has at least
    one Address.

    This method looks the constraints defines inside the propertySheets
    then check each of them

    constraint_list -- the list of constraint we have to check
    """
    error_list = self._checkConsistency(fixit = fixit)
    # We are looking inside all instances in constraints, then we check
    # the consistency for all of them

    for constraint_instance in self.constraints:
      if fixit:
        error_list += constraint_instance.fixConsistency(object=self)
      else:
        error_list += constraint_instance.checkConsistency(object=self)

    if len(error_list) > 0 and fixit:
      self.reindexObject()

    return error_list

  security.declareProtected(Permissions.ManagePortal, 'fixConsistency')
  def fixConsistency(self):
    """
    Fix the constitency of objects.
    """
    return self.checkConsistency(fixit=1)

  # Context related methods
  security.declarePublic('asContext')
  def asContext(self, context=None, REQUEST=None, **kw):
    if context is None:
      # Make a copy
      context = self.__class__(self.getId())
      context.__dict__.update(self.__dict__)
      # Copy REQUEST properties to self
      if REQUEST is not None:
        context.__dict__.update(REQUEST)
      # Define local properties
      if kw is not None: context.__dict__.update(kw)
      # Make it a temp content
      temp_object = TempBase(self.getId())
      for k in ('isIndexable', 'reindexObject', 'recursiveReindexObject', 'activate', 'setUid', ):
        setattr(context, k, getattr(temp_object,k))
      # Return result
      return context.__of__(self.aq_parent)
    else:
      return context.asContext(REQUEST=REQUEST, **kw)

  # Workflow Related Method
  security.declarePublic('getWorkflowStateItemList')
  def getWorkflowStateItemList(self):
    """
      Returns a list of tuples {id:workflow_id, state:workflow_state}
    """
    result = []
    for wf in self.portal_workflow.getWorkflowsFor(self):
      result += [(wf.id, wf._getWorkflowStateOf(self, id_only=1))]
    return result

  security.declarePublic('getWorkflowInfo')
  def getWorkflowInfo(self, name='state', wf_id=None):
    """
      Returns a list of tuples {id:workflow_id, state:workflow_state}
    """
    portal_workflow = self.portal_workflow
    return portal_workflow.getInfoFor(self, name, wf_id=wf_id)

  security.declareProtected(Permissions.ManagePortal, 'View')
  def objectCount(self):
    """
      Returns number of objects
    """
    return len(self.objectIds())

  # Hide Acquisition to prevent loops (ex. in cells)
  # Another approach is to use XMLObject everywhere
  # DIRTY TRICK XXX
#   def objectValues(self, *args, **kw):
#     return []
#
#   def contentValues(self, *args, **kw):
#     return []
#
#   def objectIds(self, *args, **kw):
#     return []
#
#   def contentIds(self, *args, **kw):
#     return []


  security.declarePublic('immediateReindexObject')
  def immediateReindexObject(self, *args, **kw):
    """
      Reindexes an object - also useful for testing
    """
    if self.isIndexable:
      #LOG("immediateReindexObject",0,self.getRelativeUrl())
      PortalContent.reindexObject(self, *args, **kw)
    else:
      pass
      #LOG("No reindex now",0,self.getRelativeUrl())

  security.declarePublic('recursiveImmediateReindexObject')
  recursiveImmediateReindexObject = immediateReindexObject

  security.declarePublic('reindexObject')
  def reindexObject(self, *args, **kw):
    """
      Reindexes an object
      args / kw required since we must follow API
    """
    root_indexable = int(getattr(self.getPortalObject(),'isIndexable',1))
    if self.isIndexable and root_indexable:
      self.activate(**kw).immediateReindexObject(*args, **kw)

  def immediateQueueCataloggedObject(self, *args, **kw):
    if self.isIndexable:
      catalog_tool = getToolByName(self, 'portal_catalog', None)
      if catalog_tool is not None:
        catalog_tool.queueCataloggedObject(self, *args, **kw)

  security.declarePublic('queueCataloggedObject')
  def queueCataloggedObject(self, *args, **kw):
    """
      Index an object in a deferred manner.
    """
    if self.isIndexable:
      LOG('queueCataloggedObject', 0, 'activate immediateQueueCataloggedObject on %s' % self.getPath())
      self.activate(**kw).immediateQueueCataloggedObject(*args, **kw)

  security.declarePublic('recursiveQueueCataloggedObject')
  recursiveQueueCataloggedObject = queueCataloggedObject

  security.declareProtected( Permissions.AccessContentsInformation, 'asXML' )
  def asXML(self, ident=0):
    """
        Generate an xml text corresponding to the content of this object
    """
    return Base_asXML(self, ident=ident)

  # Optimized Menu System
  security.declarePublic('allowedContentTypes')
  def allowedContentTypes( self ):
    """
      List portal_types which can be added in this folder / object.
    """
    return []

  security.declareProtected(Permissions.View, 'getBinaryData')
  def getBinaryData(self):
    """
      Return the binary data
    """
    bin = None
    if hasattr(self,'_original'):
      bin = self._original._data()
    elif hasattr(self,'_data'):
      bin = self._data
    elif hasattr(self,'data'):
      bin = self.data
    if bin is not None:
      return StringIO(str(bin))
    return None

  security.declareProtected(Permissions.ModifyPortalContent, 'setBinaryData')
  def setBinaryData(self, data):
    """
      Set the binary data, data must be a cStringIO
    """
    self.edit(file=data)
    #LOG('Base.setBinaryData',0,'data: %s' % str(data))
    #obj=''
    #if hasattr(self,'_original'):
    #  LOG('Base.setBinaryData',0,'_original for : %s' % str(self))
    #  self._original.data = data
    #elif hasattr(self,'_data'):
    #  LOG('Base.setBinaryData',0,'_data for : %s' % str(self))
    #  self._data = data
    #elif hasattr(self,'data'):
    #  LOG('Base.setBinaryData',0,'data for : %s' % str(self))
    #  self.data = data

  #security.declareProtected(Permissions.View, 'getObjectMenu')
  #def getObjectMenu(self, *args, **kw):
  #  absolute_url = self.absolute_url()
  #
  #"  jump_menu = """<select name="jump_select" size="1" tal:attributes="onChange string:submitAction(this.form,'%s/doJump')">
  #            <option selected value="1" disabled>%s</option>
  #            <span tal:repeat="action jump_actions">
  #             <option value="1" tal:content="action/name"
  #                tal:attributes="value action/url">Saut</option>
  #            </span>
  #           </select>""" % (self.gettext('Jump...'), absolute_url, )
  #
  #  pass

  security.declareProtected(Permissions.ModifyPortalContent, 'commitTransaction')
  def commitTransaction(self):
    # Commit a zope transaction (to reduce locks)
    get_transaction().commit()

  security.declareProtected(Permissions.ModifyPortalContent, 'abortTransaction')
  def abortTransaction(self):
    # Abort a zope transaction (to reduce locks)
    get_transaction().abort()

  # Hash method
  def __hash__(self):
    return self.getUid()

  #psyco.bind(getObjectMenu)

  security.declareProtected(Permissions.ModifyPortalContent, 'setGuid')
  def setGuid(self):
    """
    This generate a global and unique id
    It will be defined like this :
     full dns name + portal_name + uid + random
     the guid should be defined only one time for each object
    """
    if not hasattr(self, 'guid'):
      guid = ''
      # Set the dns name
      guid += gethostbyaddr(gethostname())[0]
      guid += '_' + self.portal_url.getPortalPath()
      guid += '_' + str(self.uid)
      guid += '_' + str(random.randrange(1,2147483600))
    setattr(self,'guid',guid)

  security.declareProtected(Permissions.AccessContentsInformation, 'getGuid')
  def getGuid(self):
    """
    Get the global and unique id
    """
    return getattr(self,'guid',None)

  security.declareProtected(Permissions.AccessContentsInformation, 'asPredicate')
  def asPredicate(self):
    """
    Returns a temporary Predicate based on the document properties
    """
    return None

  security.declareProtected(Permissions.View, 'get_local_permissions')
  def get_local_permissions(self):
    """
    This works like get_local_roles. It allows to get all
    permissions defined locally
    """
    local_permission_list = ()
    for permission in self.possible_permissions():
      permission_role = getattr(self,pname(permission),None)
      if permission_role is not None:
        local_permission_list += ((permission,permission_role),)
    return local_permission_list

  security.declareProtected(Permissions.View, 'get_local_permissions')
  def manage_setLocalPermissions(self,permission,local_permission_list=None):
    """
    This works like manage_setLocalRoles. It allows to set all
    permissions defined locally
    """
    permission_name = pname(permission)
    if local_permission_list is None:
      if hasattr(self,permission_name):
        delattr(self,permission_name)
    else:
      if type(local_permission_list) is type('a'):
        local_permission_list = (local_permission_list,)
      setattr(self,permission_name,tuple(local_permission_list))

  ### Content accessor methods
  security.declareProtected(Permissions.View, 'getSearchableText')
  def getSearchableText(self, md=None):
      """\
      Used by the catalog for basic full text indexing
      We should try to do some kind of file conversion here
      """
      searchable_text = "%s %s %s" %  (self.getTitle(), self.getDescription(),
                                    self.getId())
      return searchable_text

  # Compatibility with CMF Catalog / CPS sites
  SearchableText = getSearchableText

  security.declareProtected(Permissions.View, 'newError')
  def newError(self, **kw):
    """
    Create a new Error object
    """
    from Products.ERP5Type.Error import Error
    return Error(**kw)

  
  _temp_isIndexable = 0

  def _temp_reindexObject(self, *args, **kw):
    pass

  def _temp_recursiveReindexObject(self, *args, **kw):
    pass

  def _temp_activate(self):
    return self

  def _temp_setUid(self, value):
    self.uid = value # Required for Listbox so that no casting happens when we use TempBase to create new objects

  def _temp_setTitle(self, value):
    """
    Required so that getProperty('title') will work on tempBase objects
    The dynamic acquisition work very well for a lot of properties, but
    not for title. For example, if we do setProperty('organisation_url'), then
    even if organisation_url is not in a propertySheet, the method getOrganisationUrl
    will be generated. But this does not work for title, because I(seb)'m almost sure
    there is somewhere a method '_setTitle' or 'setTitle' with no method getTitle on Base.
    That why setProperty('title') and getProperty('title') does not work.
    """
    self.title = value

  def _temp_getTitle(self):
    return getattr(self,'title',None)

InitializeClass(Base)

class TempBase(Base):
  """
    If we need Base services (categories, edit, etc) in temporary objects
    we shoud used TempBase
  """
  isIndexable = 0

  def reindexObject(self, *args, **kw):
    pass

  def recursiveReindexObject(self, *args, **kw):
    pass

  def activate(self):
    return self

  def setUid(self, value):
    self.uid = value # Required for Listbox so that no casting happens when we use TempBase to create new objects

  def setTitle(self, value):
    """
    Required so that getProperty('title') will work on tempBase objects
    The dynamic acquisition work very well for a lot of properties, but
    not for title. For example, if we do setProperty('organisation_url'), then
    even if organisation_url is not in a propertySheet, the method getOrganisationUrl
    will be generated. But this does not work for title, because I(seb)'m almost sure
    there is somewhere a method '_setTitle' or 'setTitle' with no method getTitle on Base.
    That why setProperty('title') and getProperty('title') does not work.
    """
    self.title = value

  def getTitle(self):
    return getattr(self,'title',None)
