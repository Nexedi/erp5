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
from Acquisition import aq_base, aq_inner

from Products.CMFCore.WorkflowCore import WorkflowMethod
from Products.CMFCore.PortalContent import PortalContent

from Products.CMFActivity.ActiveObject import ActiveObject

from Products.ERP5Type import _dtmldir
from Products.ERP5Type import PropertySheet
from Products.ERP5Type import Permissions
from Products.ERP5Type.Utils import UpperCase
from Products.ERP5Type.Utils import convertToUpperCase
from Products.ERP5Type.Utils2 import _getListFor
from Products.ERP5Type.Accessor.TypeDefinition import list_types

from Products.Base18.Base18 import Base18

from ZopePatch import ERP5PropertyManager

from CopySupport import CopyContainer
from Errors import DeferredCatalogError

from string import join
import sys
import psyco
import pickle

from cStringIO import StringIO
from email.MIMEBase import MIMEBase
from email import Encoders

from zLOG import LOG

class CallbaseError(AttributeError):
    pass

class Base( CopyContainer, PortalContent, Base18, ActiveObject, ERP5PropertyManager ):
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
  isIndexable = 1   # If set to 0, reindexing will not happen (useful for optimization)

  # Declarative security
  security = ClassSecurityInfo()

  # Declarative properties
  property_sheets = ( PropertySheet.Base
                      , )

  # We want to use a default property view
  manage_propertiesForm = DTMLFile( 'dtml/properties', _dtmldir )

  # Constructor
  def __init__(self, id, uid=None, rid=None, sid=None, **kw):
    self.id = id
    if uid is not None :
      self.uid = uid # Else it will be generated when we need it
    self.sid = sid

  # Debug
  def getOid(self):
    """
      Return ODB oid
    """
    return self._p_oid

  # Utils
  def _getCategoryTool(self):
    return aq_inner(self.getPortalObject().portal_categories)

  # Generic accessor
  def _getDefaultAcquiredProperty(self, key, default_value, null_value,
    base_category=None, portal_type=None, copy_value=0, mask_value=0, sync_value=0,
    accessor_id=None, depends=None, storage_id=None, alt_accessor_id=None,
    is_list_type=0):
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
    #LOG("Get Acquired Property key",0,str(key))
    if storage_id is None: storage_id=key
    # LOG("Get Acquired Property storage_id",0,str(storage_id))
    # If we hold an attribute and mask_value is set, return the attribute
    if mask_value and hasattr(self, storage_id):
      if getattr(self, storage_id) != None:
        return getattr(self, storage_id)
    # Retrieve the list of related objects
    #LOG("Get Acquired Property portal_type",0,str(portal_type))
    super_list = self._getValueList(base_category, portal_type=portal_type) # We only do a single jump
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
      if copy_value:
        if not hasattr(self, storage_id):
          # Copy the value if it does not already exist as an attribute of self
          # Like in the case of orders / invoices
          setattr(self, value)
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
                    return result[0]
                else:
                  return result
              else:
                # Result is a simple type
                return result

      if copy_value:
        return getattr(self,storage_id, default_value)
      else:
        # Return the default value defined at the class level XXXXXXXXXXXXXXX
        return default_value

  def _getAcquiredPropertyList(self, key, default_value, null_value,
     base_category, portal_type=None, copy_value=0, mask_value=0, sync_value=0, append_value=0,
     accessor_id=None, depends=None, storage_id=None, alt_accessor_id=None,
     is_list_type=0):
    """
      Default accessor. Implements the default
      attribute accessor.

      portal_type
      copy_value
      depends
    """
    if storage_id is None: storage_id=key
    if mask_value and hasattr(self, storage_id):
      if getattr(self, storage_id) != None:
        return getattr(self, storage_id)
    if type(base_category) == 'a':
      base_category = (base_category, )
    if type(portal_type) == 'a':
      portal_type = (portal_type, )
    super = None
    psuper = []
    for cat in base_category:
      super_list = self._getValueList(cat) # We only do a single jump - no acquisition
      for super in super_list:
        if super is not None:
          # Performance should be increased
          for ptype in portal_type:
            if ptype == super.portal_type:
              psuper.append(super)
    if len(psuper) > 0:
      value = []
      for super in psuper:
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
      return value
    else:
      # ?????
      if copy_value:
        return getattr(self,storage_id, default_value)
      else:
        return default_value

  security.declareProtected( Permissions.AccessContentsInformation, 'getProperty' )
  def getProperty(self, key, d=None):
    """
      Previous Name: getValue

      Generic accessor. Calls the real accessor
    """
    accessor_name = 'get' + UpperCase(key)
    aq_self = aq_base(self)
    if hasattr(aq_self, accessor_name):
      method = getattr(self, accessor_name)
      return method()
    elif hasattr(aq_self, key):
      value = getattr(aq_self, key)
      if callable(value): value = value()
      return value
    else:
      return ERP5PropertyManager.getProperty(self, key, d=d)

  security.declareProtected( Permissions.AccessContentsInformation, 'getPropertyList' )
  def getPropertyList(self, key, d=None):
    """
      Previous Name: getValue

      Generic accessor. Calls the real accessor
    """
    return self.getProperty('%s_list' % key)

  security.declareProtected( Permissions.ModifyPortalContent, 'setProperty' )
  def setProperty(self, key, value, type='string'):
    """
      Previous Name: setValue

      New Name: we use the naming convention of
      /usr/lib/zope/lib/python/OFS/PropertySheets.py

      TODO: check possible conflicts

      Generic accessor. Calls the real accessor
    """
    self._setProperty(key,value,type=type)
    self.reindexObject()

  security.declareProtected( Permissions.ModifyPortalContent, '_setProperty' )
  def _setProperty(self, key, value, type='string'):
    """
      Previous Name: _setValue

      Generic accessor. Calls the real accessor
    """
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
      #LOG("Calling: ",0, '%s %s ' % (accessor_name, kw[key]))
      method = getattr(self, accessor_name)
      return method(value)
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
      #LOG("Calling: ",0, '%s %s ' % (public_accessor_name, kw[key]))
      method = getattr(self, public_accessor_name)
      method(value)
    else:
      #LOG("Changing attr: ",0, key)
      try:
        ERP5PropertyManager._setProperty(self, key, value, type=type)
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
  def _edit(self, REQUEST=None, force_update = 0, **kw):
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
          old_value = method()
          #LOG("Old value: ",0, str(old_value))
          #LOG("New value: ",0, str(kw[key]))
        else:
          old_value = None
        if old_value != kw[key] or force_update:
          self._setProperty(key, kw[key])
      elif self.id != kw['id']:
        self.recursiveFlushActivity(invoke=1) # Do not rename until everything flushed
        previous_relative_url = self.getRelativeUrl()
        self.aq_parent.manage_renameObjects([self.id], [kw['id']])
        new_relative_url = self.getRelativeUrl()
        id_changed = 1
    self.reindexObject()
    if id_changed:
      self.recursiveFlushActivity(invoke=1)  # Required if we wish that news ids appear instantly
      #if self.isIndexable:
      #  self.moveObject()             # Required if we wish that news ids appear instantly
      #if hasattr(aq_base(self), 'recursiveMoveObject'):
      #  self.recursiveMoveObject()    # Required to make sure path of subobjects is updated
      self.activate().updateRelatedContent(previous_relative_url, new_relative_url)
      #self.activate().recursiveImmediateReindexObject() # Required to update path / relative_url of subobjects

  security.declareProtected( Permissions.ModifyPortalContent, 'updateRelatedContent' )
  def updateRelatedContent(self, previous_category_url, new_category_url):
    """

    """
    self._getCategoryTool().updateRelatedContent(self, previous_category_url, new_category_url)

  security.declareProtected( Permissions.ModifyPortalContent, 'getObject' )
  def edit(self, REQUEST=None, force_update = 0, **kw):
    return self._edit(REQUEST=REQUEST, force_update=force_update, **kw)
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

  security.declareProtected( Permissions.AccessContentsInformation, 'getParentUid' )
  def getParentUid(self):
    """
      Returns the UID of the parent of the current object. Used
      for the implementation of the ZSQLCatalog based listing
      of objects.
    """
    parent = self.aq_parent
    uid = getattr(aq_base(parent), 'uid', None)
    if uid is None:
      parent.immediateReindexObject() # Required with deferred indexing
      uid = getattr(aq_base(parent), 'uid', None)
      if uid is None:
        raise DeferredCatalogError('Could neither access parent uid nor generate it', context)
    return uid


  security.declareProtected( Permissions.AccessContentsInformation, 'getParent' )
  def getParent(self):
    """
      Returns the parent of the current object.
    """
    return self.aq_parent

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
      self.immediateReindexObject() # Required with deferred indexing
      uid = getattr(aq_base(self), 'uid', None)
      if uid is None:
        raise DeferredCatalogError('Could neither access uid nor generate it', context)
    return uid

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
  security.declareProtected( Permissions.ManagePortal, 'Upgrade' )
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
    value_list =self._getCategoryTool().getRelatedValueList(self, id, spec=spec, filter=filter, portal_type=portal_type)
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

  security.declareProtected( Permissions.ModifyPortalContent, '_delValue' )
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
  def _getAcquiredCategoryMembershipList(self, category=None, base=0 , spec=(),
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

  security.declareProtected( Permissions.ModifyPortalContent, '_setCategoryList' )
  def _setCategoryList(self, path_list):
    self.categories = tuple(path_list)

  security.declareProtected( Permissions.View, 'getBaseCategoryIdList' )
  def getBaseCategoryIdList(self):
    """
      Lists the base_category ids which apply to this instance
    """
    return self._getCategoryTool().getBaseCategoryIdList(context=self)

  security.declareProtected( Permissions.View, 'getBaseCategoryIds' )
  getBaseCategoryIds = getBaseCategoryIdList

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
  def list(self):
        '''
        Returns the default list even if folder_contents is overridden.
        '''
        list_action = _getListFor(self)
        if getattr(aq_base(list_action), 'isDocTemp', 0):
            return apply(list_action, (self, self.REQUEST))
        else:
            return list_action()

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
    # PERFORMANCE ISSUE
    from Products.ERP5Type.Context import newContext
    if context is None:
      return newContext(context=self, REQUEST=REQUEST, **kw)
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


  security.declareProtected(Permissions.ModifyPortalContent, 'immediateReindexObject')
  def immediateReindexObject(self, *args, **kw):
    """
      Reindexes an object - also useful for testing
    """
    if self.isIndexable:
      #LOG("immediateReindexObject",0,self.getRelativeUrl())
      PortalContent.reindexObject(self)
    else:
      pass
      #LOG("No reindex now",0,self.getRelativeUrl())

  security.declareProtected(Permissions.ModifyPortalContent, 'recursiveImmediateReindexObject')
  recursiveImmediateReindexObject = immediateReindexObject

  security.declareProtected(Permissions.ModifyPortalContent, 'reindexObject')
  def reindexObject(self, *args, **kw):
    """
      Reindexes an object
      args / kw required since we must follow API
    """
    if self.isIndexable:
      self.activate().immediateReindexObject()

  security.declareProtected( Permissions.AccessContentsInformation, 'asXML' )
  def asXML(self, ident=0):
    """
        Generate an xml text corresponding to the content of this object
    """
    xml = ''
    if ident==0:
      xml += '<erp5>'
    LOG('asXML',0,'Working on: %s' % str(self.getPath()))
    ident_string = '' # This is used in order to have the ident incremented
                      # for every sub-object
    for i in range(0,ident):
      ident_string += ' '
    xml += ident_string + '<object id=\"%s\" portal_type=\"%s\">\n' % \
                           (self.getId(),self.portal_type)

    # We have to find every property
    for prop_id in self.propertyIds():
      # In most case, we should not synchronize acquired properties
      prop = ''
      #if not prop.has_key('acquisition_base_category') \
      #   and prop['id'] != 'categories_list' and prop['id'] != 'uid':
      if prop_id not in ('uid','workflow_history'):
        prop_type = self.getPropertyType(prop_id)
        xml_prop_type = 'type="' + prop_type + '"'
        #try:
        value = self.getProperty(prop_id)
        #except AttributeError:
        #  value=None

        xml += ident_string + '  <%s %s>' %(prop_id,xml_prop_type)
        if value is None:
          pass
        elif prop_type in ('image','file','document'):
          LOG('asXML',0,'value: %s' % str(value))
          # This property is binary and should be converted with mime
          msg = MIMEBase('application','octet-stream')
          msg.set_payload(value.getvalue())
          Encoders.encode_base64(msg)
          ascii_data = msg.get_payload()
          ascii_data = ascii_data.replace('\n','@@@\n')
          xml+=ascii_data
        elif prop_type in ('pickle',):
          # We may have very long lines, so we should split
          msg = MIMEBase('application','octet-stream')
          msg.set_payload(value)
          Encoders.encode_base64(msg)
          ascii_data = msg.get_payload()
          ascii_data = ascii_data.replace('\n','@@@\n')
          xml+=ascii_data
        elif self.getPropertyType(prop_id) in ['lines','tokens']:
          i = 1
          for line in value:
            xml += '%s' % line
            if i<len(value):
              xml+='@@@' # XXX very bad hack, must find something better
            i += 1
        elif self.getPropertyType(prop_id) in ('text','string'):
          xml += str(value).replace('\n','@@@')
        else:
          xml+= str(value)
        xml += '</%s>\n' % prop_id

    # We have to describe the workflow history
    if hasattr(self,'workflow_history'):
      workflow_list = self.workflow_history
      workflow_list_keys = workflow_list.keys()
      workflow_list_keys.sort() # Make sure it is sorted

      for workflow_id in workflow_list_keys:
        xml += ident_string + '    <workflow_history id=\"%s\">\n' % workflow_id
        for workflow_action in workflow_list[workflow_id]: # It is already sorted
          xml += ident_string + '      <workflow_action>\n'
          worfklow_variable_list = workflow_action.keys()
          worfklow_variable_list.sort()
          for workflow_variable in worfklow_variable_list: # Make sure it is sorted
            variable_type = "string" # Somewhat bad, should find a better way
            if workflow_variable.find('time')>= 0:
              variable_type = "date"
            xml += ident_string + '        <%s type=\"%s\">%s' % (workflow_variable,
                                variable_type,workflow_action[workflow_variable])
            xml += '</%s>\n' % workflow_variable
          xml += ident_string + '      </workflow_action>\n'
        xml += ident_string + '    </workflow_history>\n'
      #xml += ident_string + '  </workflow_history>\n'

    # We should not describe security settings
    #xml += ident_string + '  <security_info>\n'
    for user_role in self.get_local_roles():
      #xml += ident_string + '    <local_role user=\"%s\">' % user_role[0]
      xml += ident_string + '    <local_role>%s' % user_role[0]
      #i = 0
      for role in user_role[1]:
        #xml += ident_string + '      <element>%s</element>\n' % role
        #if i>0:
        xml += '@@@'
        #i+=1
        xml += '%s' % role
      xml += '</local_role>\n'

    # We have finished to generate the xml
    xml += ident_string + '</object>\n'
    if ident==0:
      xml += '</erp5>'
    # Now convert the string as unicode
    if type(xml) is type(u"a"):
      xml_unicode = xml
    else:
      xml_unicode = unicode(xml,encoding='iso-8859-1')
    return xml_unicode.encode('utf-8')

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

  security.declareProtected(Permissions.View, 'getObjectMenu')
  def getObjectMenu(self, *args, **kw):
    absolute_url = self.absolute_url()

    jump_menu = """<select name="jump_select" size="1" tal:attributes="onChange string:submitAction(this.form,'%s/doJump')">
              <option selected value="1" disabled>%s</option>
              <span tal:repeat="action jump_actions">
               <option value="1" tal:content="action/name"
                  tal:attributes="value action/url">Saut</option>
              </span>
             </select>""" % (self.gettext('Jump...'), absolute_url, )

    pass

  # Hash method
  def __hash__(self):
    return self.getUid()

  psyco.bind(getObjectMenu)

class TempBase(Base):
  """
    If we need Base services (categories, edit, etc) in temporary objects
    we shoud used TempBase
  """
  isIndexable = 0

  def reindexObject(self, *args, **kw):
    pass

  def activate(self):
    return self

InitializeClass(Base)

