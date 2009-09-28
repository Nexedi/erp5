# -*- coding: utf-8 -*-
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

from struct import unpack
from copy import copy
import warnings
import types

from Globals import InitializeClass, DTMLFile
from AccessControl import ClassSecurityInfo
from AccessControl.Permission import pname, Permission
from AccessControl.PermissionRole import rolesForPermissionOn
from AccessControl.SecurityManagement import getSecurityManager
from AccessControl.ZopeGuards import guarded_getattr
from Acquisition import aq_base, aq_inner, aq_acquire, aq_chain
import OFS.History
from OFS.SimpleItem import SimpleItem
from OFS.PropertyManager import PropertyManager

from ZopePatch import ERP5PropertyManager

from Products.CMFCore.PortalContent import PortalContent, _getViewFor
from Products.CMFCore.Expression import Expression
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.WorkflowCore import ObjectDeleted, ObjectMoved
from Products.CMFCore.CMFCatalogAware import CMFCatalogAware

from Products.DCWorkflow.Transitions import TRIGGER_WORKFLOW_METHOD, TRIGGER_USER_ACTION

from Products.ERP5Type import _dtmldir
from Products.ERP5Type import PropertySheet
from Products.ERP5Type import interfaces
from Products.ERP5Type import Permissions
from Products.ERP5Type.Utils import UpperCase
from Products.ERP5Type.Utils import convertToUpperCase, convertToMixedCase
from Products.ERP5Type.Utils import createExpressionContext
from Products.ERP5Type.Accessor.Accessor import Accessor
from Products.ERP5Type.Accessor.TypeDefinition import list_types
from Products.ERP5Type.Accessor import Base as BaseAccessor
from Products.ERP5Type.XMLExportImport import Base_asXML
from Products.ERP5Type.Cache import CachingMethod, clearCache, getReadOnlyTransactionCache
from Accessor import WorkflowState
from Products.ERP5Type.Log import log as unrestrictedLog
from Products.ERP5Type.TransactionalVariable import getTransactionalVariable
from Products.ERP5Type.Accessor.TypeDefinition import type_definition

from CopySupport import CopyContainer, CopyError,\
    tryMethodCallWithTemporaryPermission
from Errors import DeferredCatalogError, UnsupportedWorkflowMethod
from Products.CMFActivity.ActiveObject import ActiveObject
from Products.ERP5Type.Accessor.Accessor import Accessor as Method
from Products.ERP5Type.Accessor.TypeDefinition import asDate
from Products.ERP5Type.Message import Message
from Products.ERP5Type.UnrestrictedMethod import UnrestrictedMethod

from string import join
import sys, re
from Products.ERP5Type.PsycoWrapper import psyco

from cStringIO import StringIO
from socket import gethostname, gethostbyaddr
import random

import inspect
from pprint import pformat

import zope.interface

from ZODB.POSException import ConflictError
from zLOG import LOG, INFO, ERROR, WARNING

_MARKER = []

global registered_workflow_method_set
wildcard_interaction_method_id_matcher = re.compile(".*[\+\*].*")
workflow_method_registry = [] # XXX A set() would be better but would require a hash in WorkflowMethod class

def resetRegisteredWorkflowMethod(portal_type=None):
  """
    TODO: unwrap workflow methos which were standard methods initially
  """
  for method in workflow_method_registry:
    method.reset(portal_type=portal_type)

class WorkflowMethod(Method):

  def __init__(self, method, id=None, reindex=1):
    """
      method - a callable object or a method

      id - the workflow transition id. This is useful
           to emulate "old" CMF behaviour but is 
           somehow inconsistent with the new registration based
           approach implemented here.

           We store id as _transition_id and use it
           to register the transition for each portal
           type and each workflow for which it is
           applicable.
    """
    self._m = method
    if id is None:
      self._transition_id = method.__name__
    else:
      self._transition_id = id
    # Only publishable methods can be published as interactions
    # A pure private method (ex. _doNothing) can not be published
    # This is intentional to prevent methods such as submit, share to 
    # be called from a URL. If someone can show that this way
    # is wrong (ex. for remote operation of a site), let us know.
    if not method.__name__.startswith('_'):
      self.__name__ = method.__name__
      for func_id in ['func_code', 'func_defaults', 'func_dict', 'func_doc', 'func_globals', 'func_name']:
        setattr(self, func_id, getattr(method, func_id, None))
    self._invoke_once = {}
    self._invoke_always = {} # Store in a dict all workflow IDs which require to
                                # invoke wrapWorkflowMethod at every call
                                # during the same transaction

  def getTransitionId(self):
    return self._transition_id

  def __call__(self, instance, *args, **kw):
    """
      Invoke the wrapped method, and deal with the results.
    """
    if getattr(self, '__name__', None) in ('getPhysicalPath', 'getId'):
      # To prevent infinite recursion, 2 methods must have special treatment
      # this is clearly not the best way to implement this but it is 
      # already better than what we had. I (JPS) would prefer to use
      # critical sections in this part of the code and a
      # thread variable which tells in which semantic context the code
      # should ne executed. - XXX
      return self._m(instance, *args, **kw)

    # New implementation does not use any longer wrapWorkflowMethod
    # but directly calls the workflow methods
    wf = getToolByName(instance, 'portal_workflow', None)

    if wf is None:
      # XXX instance is unwrapped(no acquisition)
      # XXX I must think that what is a correct behavior.(Yusei)
      return self._m(instance, *args, **kw)

    # Build a list of transitions which may need to be invoked
    instance_path = instance.getPhysicalPath()
    portal_type = instance.portal_type
    transactional_variable = getTransactionalVariable(instance)
    invoke_once_item_list = self._invoke_once.get(portal_type, {}).items()
    valid_invoke_once_item_list = []
    # Only keep those transitions which were never invoked
    for wf_id, transition_list in invoke_once_item_list:
      valid_transition_list = []
      for transition_id in transition_list:
        once_transition_key = ('Products.ERP5Type.Base.WorkflowMethod.__call__',
                                wf_id, transition_id, instance_path)
        try:
          already_called_transition = transactional_variable[once_transition_key]
        except KeyError:
          already_called_transition = 0
          transactional_variable[once_transition_key] = 1
        if not already_called_transition:
          valid_transition_list.append(transition_id)
      if valid_transition_list:
        valid_invoke_once_item_list.append((wf_id, valid_transition_list))
    candidate_transition_item_list = valid_invoke_once_item_list + \
                           self._invoke_always.get(portal_type, {}).items()

    #LOG('candidate_transition_item_list %s' % self.__name__, 0, str(candidate_transition_item_list))

    # Try to return immediately if there are no transition to invoke
    if not candidate_transition_item_list:
      return apply(self.__dict__['_m'], (instance,) + args, kw)

    # Prepare a list of transitions which should be invoked.
    # This list is based on the results of isWorkflowMethodSupported.
    # An interaction is ignored if the guard prevents execution.
    # Otherwise, an exception is raised if the workflow transition does not
    # exist from the current state, or if the guard rejects it.
    valid_transition_item_list = []
    for wf_id, transition_list in candidate_transition_item_list:
      candidate_workflow = wf[wf_id]
      valid_list = []
      for transition_id in transition_list:
        if candidate_workflow.isWorkflowMethodSupported(instance, transition_id):
          valid_list.append(transition_id)
        elif candidate_workflow.__class__.__name__ == 'DCWorkflowDefinition':
          raise UnsupportedWorkflowMethod(instance, wf_id, transition_id)
          # XXX Keep the log for projects that needs to comment out
          #     the previous line.
          LOG("WorkflowMethod.__call__", ERROR,
              "Transition %s/%s on %r is ignored. Current state is %r."
              % (wf_id, transition_id, instance,
                 candidate_workflow._getWorkflowStateOf(instance, id_only=1)))
      if valid_list:
        valid_transition_item_list.append((wf_id, valid_list))

    #LOG('valid_transition_item_list %s' % self.__name__, 0, str(valid_transition_item_list))

    # Call whatever must be called before changing states
    for wf_id, transition_list in valid_transition_item_list:
       wf[wf_id].notifyBefore(instance, transition_list, args=args, kw=kw)

    # Compute expected result
    result = apply(self.__dict__['_m'], (instance,) + args, kw)

    # Change the state of statefull workflows
    for wf_id, transition_list in valid_transition_item_list:
      try:
        wf[wf_id].notifyWorkflowMethod(instance, transition_list, args=args, kw=kw)
      except ObjectDeleted:
        # Re-raise with a different result.
        raise ObjectDeleted(result)
      except ObjectMoved, ex:
        # Re-raise with a different result.
        raise ObjectMoved(ex.getNewObject(), result)

    # Call whatever must be called after changing states
    for wf_id, transition_list in valid_transition_item_list:
      wf[wf_id].notifySuccess(instance, transition_list, result, args=args, kw=kw)

    # Return result finally
    return result

  def registerTransitionAlways(self, portal_type, workflow_id, transition_id):
    """
      Transitions registered as always will be invoked always
    """
    transition_list = self._invoke_always.setdefault(portal_type, {}).setdefault(workflow_id, [])
    if transition_id not in transition_list: transition_list.append(transition_id)
    self.register()

  def registerTransitionOncePerTransaction(self, portal_type, workflow_id, transition_id):
    """
      Transitions registered as one per transactions will be invoked 
      only once per transaction
    """
    transition_list = self._invoke_once.setdefault(portal_type, {}).setdefault(workflow_id, [])
    if transition_id not in transition_list: transition_list.append(transition_id)
    self.register()

  def register(self):
    """
      Registers the method so that _aq_reset may later reset it
    """
    workflow_method_registry.append(self)

  def reset(self, portal_type=None):
    """
      Reset the list of registered interactions or transitions
    """
    if portal_type:
      self._invoke_once[portal_type] = {}
      self._invoke_always[portal_type] = {}
    else:
      self._invoke_once = {}
      self._invoke_always = {}

def _aq_reset():
  Base.aq_method_generated = {}
  Base.aq_portal_type = {}
  Base.aq_related_generated = 0
  Base.aq_preference_generated = 0

  # Some method generations are based on portal methods, and portal methods cache results.
  # So it is safer to invalidate the cache.
  clearCache()

  # Reset workflow methods so that they no longer invoke workflows
  resetRegisteredWorkflowMethod()

global method_registration_cache
method_registration_cache = {}

WORKFLOW_METHOD_MARKER = ('Base._doNothing',)
RESERVED_TUPLE_PROPERTY = set(('_constraints', '_properties', '_categories',
                               '__implements__', 'property_sheets', 
                               '_erp5_properties'))
# It might be necessary to use another type for those reserved properties
# ex. list type

class PropertyHolder:
  isRADContent = 1

  def __init__(self):
    self.__name__ = 'PropertyHolder'
    self.security = ClassSecurityInfo() # We create a new security info object
    self.workflow_method_registry = {}

  def _getItemList(self):
    return [x for x in self.__dict__.items() if x[0] not in
        RESERVED_TUPLE_PROPERTY]

  # Accessor generation
  def createAccessor(self, id):
    """
    Invokes appropriate factory and create an accessor
    """
    fake_accessor = getattr(self, id)
    ptype = self._portal_type
    if fake_accessor is WORKFLOW_METHOD_MARKER:
      # Case 1 : a workflow method only
      accessor = Base._doNothing
    else:
      # Case 2 : a workflow method over an accessor
      (accessor_class, accessor_args, key) = fake_accessor
      accessor = accessor_class(id, key, *accessor_args)
    for wf_id, tr_id, once in self.workflow_method_registry.get(id, ()):
      if not isinstance(accessor, WorkflowMethod):
        accessor = WorkflowMethod(accessor)
        if once:
          accessor.registerTransitionOncePerTransaction(ptype, wf_id, tr_id)
        else:
          accessor.registerTransitionAlways(ptype, wf_id, tr_id)
      else:
        if once:
          accessor.registerTransitionOncePerTransaction(ptype, wf_id, tr_id)
        else:
          accessor.registerTransitionAlways(ptype, wf_id, tr_id)
    setattr(self, id, accessor)
    return accessor

  def registerAccessor(self, id, key, accessor_class, accessor_args):
    """
    Saves in a dictionary all parameters required to create an accessor
    The goal here is to minimize memory occupation. We have found the following:

    - the size of a tuple with simple types and the size 
      of None are the same (a pointer)

    - the size of a pointer to a class is the same as the
      size of None

    - the python caching system for tuples is efficient for tuples
      which contain simple types (string, int, etc.) but innefficient
      for tuples which contain a pointer

    - as a result, it is better to create separate dicts if 
      values contain pointers and single dict if value is 
      a tuple of simple types

    Parameters:

    id  --  The id the accessor (ex. getFirstName)

    key --  The id of the property (ex. first_name) or the id of the
            method for Alias accessors
    """
    #LOG('registerAccessor', 0, "%s %s %s" % (id , self._portal_type, accessor_args))
    # First we try to compress the information required
    # to build a new accessor in such way that
    # if the same information is provided twice, we
    # shall keep it once only
    new_accessor_args = []
    for arg in accessor_args:
      if type(arg) is types.ListType:
        new_accessor_args.append(tuple(arg))
      else:
        new_accessor_args.append(arg)
    accessor_args = tuple(new_accessor_args)
    original_registration_tuple = (accessor_class, accessor_args, key)
    registration_tuple = method_registration_cache.get(original_registration_tuple)
    if registration_tuple is None:
      registration_tuple = original_registration_tuple
      method_registration_cache[registration_tuple] = registration_tuple
    # Use the cached tuple (same value, different pointer)
    setattr(self, id, registration_tuple)

  def registerWorkflowMethod(self, id, wf_id, tr_id, once_per_transaction=0):
    #LOG('registerWorkflowMethod', 0, "%s %s %s %s %s" % (self._portal_type, id, wf_id, tr_id, once_per_transaction))
    signature = (wf_id, tr_id, once_per_transaction)
    signature_list = self.workflow_method_registry.get(id, ())
    if signature not in signature_list:
      self.workflow_method_registry[id] = signature_list + (signature,)
    if getattr(self, id, None) is None:
      setattr(self, id, WORKFLOW_METHOD_MARKER)

  def declareProtected(self, permission, accessor_name):
    """
      It is possible to gain 30% of accessor RAM footprint
      by postponing security declaration.

      WARNING: we optimize size by not setting security if 
      it is the same as the default. This may be a bit
      dangerous if classes use another default
      security.
    """
    if permission not in (Permissions.AccessContentsInformation, Permissions.ModifyPortalContent):
      self.security.declareProtected(permission, accessor_name)

  # Inspection methods
  def getAccessorMethodItemList(self):
    """
    Return a list of tuple (id, method) for every accessor
    """
    accessor_method_item_list = []
    for x, y in self._getItemList():
      if isinstance(y, types.TupleType):
        if y is WORKFLOW_METHOD_MARKER or x == '__ac_permissions__':
          continue
        if len(y) == 0:
          raise ValueError("problem at %s %s" % (self._portal_type, x))
        if not issubclass(y[0], Accessor):
          continue
      elif not isinstance(y, Accessor):
        continue
      accessor_method_item_list.append((x, y))
    return accessor_method_item_list

  def getAccessorMethodIdList(self):
    """
    Return the list of accessor IDs
    """
    return [ x[0] for x in self.getAccessorMethodItemList() ]

  def getWorkflowMethodItemList(self):
    """
    Return a list of tuple (id, method) for every workflow method
    """
    return [x for x in self._getItemList() if isinstance(x[1], WorkflowMethod)
        or (isinstance(x[1], types.TupleType)
            and x[1] is WORKFLOW_METHOD_MARKER)]

  def getWorkflowMethodIdList(self):
    """
    Return the list of workflow method IDs
    """
    return [x[0] for x in self._getItemList() if isinstance(x[1], WorkflowMethod)
        or (isinstance(x[1], types.TupleType)
            and x[1] is WORKFLOW_METHOD_MARKER)]

  def _getClassDict(self, klass, inherited=1, local=1):
    """
    Return a dict for every property of a class
    """
    result = {}
    if inherited:
      base_list = list(klass.__bases__)
      base_list.reverse()
      for klass in base_list:
        result.update(self._getClassDict(klass, inherited=1, local=1))
    if local:
      result.update(klass.__dict__)
    return result

  def _getClassItemList(self, klass, inherited=1, local=1):
    """
    Return a list of tuple (id, method) for every property of a class
    """
    return self._getClassDict(klass, inherited=inherited, local=local).items()

  def getClassMethodItemList(self, klass, inherited=1, local=1):
    """
    Return a list of tuple (id, method, module) for every class method
    """
    return [x for x in self._getClassItemList(klass, inherited=inherited,
      local=local) if callable(x[1]) and not isinstance(x[1], Method)]

  def getClassMethodIdList(self, klass, inherited=1, local=1):
    """
    Return the list of class method IDs
    """
    return [x[0] for x in self._getClassItemList(klass, inherited=inherited,
      local=local) if callable(x[1]) and not isinstance(x[1], Method)]

  def getClassPropertyItemList(self, klass, inherited=1, local=1):
    """
    Return a list of tuple (id, method) for every class method
    """
    return [x for x in self._getClassItemList(klass, inherited=inherited,
      local=local) if not callable(x[1])]

  def getClassPropertyIdList(self, klass, inherited=1, local=1):
    """
    Return the list of class method IDs
    """
    return [x[0] for x in self._getClassItemList(klass, inherited=inherited,
      local=local) if not callable(x[1])]

def getClassPropertyList(klass):
  ps_list = getattr(klass, 'property_sheets', ())
  ps_list = tuple(ps_list)
  for super_klass in klass.__bases__:
    if getattr(super_klass, 'isRADContent', 0):
      ps_list = ps_list + tuple([p for p in getClassPropertyList(super_klass)
        if p not in ps_list])
  return ps_list

def initializeClassDynamicProperties(self, klass):
  if not Base.aq_method_generated.has_key(klass):
    # Recurse to superclasses
    for super_klass in klass.__bases__:
      if getattr(super_klass, 'isRADContent', 0):
        initializeClassDynamicProperties(self, super_klass)
    # Initialize default properties
    from Utils import setDefaultClassProperties
    if not getattr(klass, 'isPortalContent', None):
      if getattr(klass, 'isRADContent', 0):
        setDefaultClassProperties(klass)
      # Mark as generated
      Base.aq_method_generated[klass] = 1

def initializePortalTypeDynamicProperties(self, klass, ptype, aq_key, portal):
  ## Init CachingMethod which implements caching for ERP5
  from Products.ERP5Type.Cache import initializePortalCachingProperties
  initializePortalCachingProperties(portal)

  id = ''
  #LOG('before aq_portal_type %s' % id, 0, str(ptype))
  if aq_key not in Base.aq_portal_type:
    # Mark as generated
    prop_holder = PropertyHolder()
    # Recurse to parent object
    parent_object = self.aq_inner.aq_parent
    parent_klass = parent_object.__class__
    parent_type = parent_object.portal_type
    if getattr(parent_klass, 'isRADContent', 0) and \
       (ptype != parent_type or klass != parent_klass) and \
       not Base.aq_portal_type.has_key(parent_type):
      initializePortalTypeDynamicProperties(parent_object, parent_klass,
                                            parent_type, 
                                            parent_object._aq_key(), portal)
    # Initiatise portal_type properties (XXX)
    ptype_object = getattr(aq_base(portal.portal_types), ptype, None)
    prop_list = list(getattr(klass, '_properties', []))
    cat_list = list(getattr(klass, '_categories', []))
    constraint_list = list(getattr(klass, '_constraints', []))
    if ptype_object is not None:
      # Make sure this is an ERP5Type object
      ps_list = [getattr(PropertySheet, p, None) for p in
          ptype_object.property_sheet_list]
      ps_list = [p for p in ps_list if p is not None]
      # Always append the klass.property_sheets to this list (for compatibility)
      # Because of the order we generate accessors, it is still possible
      # to overload data access for some accessors
      ps_list = tuple(ps_list) + getClassPropertyList(klass)
      #LOG('ps_list',0, str(ps_list))
    else:
      ps_list = getClassPropertyList(klass)
    for base in ps_list:
      property_sheet_definition_dict = {
        '_properties': prop_list,
        '_categories': cat_list,
        '_constraints': constraint_list
      }
      for ps_property_name, current_list in \
                                    property_sheet_definition_dict.items():
        if hasattr(base, ps_property_name):
          ps_property = getattr(base, ps_property_name)
          if isinstance(ps_property, (tuple, list)):
            current_list += ps_property
          else :
            raise ValueError, "%s is not a list for %s" % (ps_property_name,
                                                           base)

    if ptype_object is not None:
      cat_list += ptype_object.base_category_list
    prop_holder._portal_type = ptype
    prop_holder._properties = prop_list
    prop_holder._categories = cat_list
    prop_holder._constraints = constraint_list
    from Utils import setDefaultClassProperties, setDefaultProperties
    setDefaultClassProperties(prop_holder)
    setDefaultProperties(prop_holder, object=self, portal=portal)
    #LOG('initializeDefaultProperties: %s' % ptype, 0, str(prop_holder.__dict__))
    initializePortalTypeDynamicWorkflowMethods(self, klass, ptype, prop_holder,
                                               portal)
    # We can now associate it after initialising security
    InitializeClass(prop_holder)
    prop_holder.__propholder__ = prop_holder
    # For now, this line below is commented, because this breaks
    # _aq_dynamic without JP's patch to Zope for an unknown reason.
    #klass.__ac_permissions__ = prop_holder.__ac_permissions__
    Base.aq_portal_type[aq_key] = prop_holder

def initializePortalTypeDynamicWorkflowMethods(self, klass, ptype, prop_holder,
                                               portal):
  """We should now make sure workflow methods are defined
  and also make sure simulation state is defined."""
  # aq_inner is required to prevent extra name lookups from happening
  # infinitely. For instance, if a workflow is missing, and the acquisition
  # wrapper contains an object with _aq_dynamic defined, the workflow id
  # is looked up with _aq_dynamic, thus causes infinite recursions.

  portal_workflow = aq_inner(getToolByName(portal, 'portal_workflow'))
  for wf in portal_workflow.getWorkflowsFor(self):
    if wf.__class__.__name__ in ('DCWorkflowDefinition', ):
      wf_id = wf.id
      # Create state var accessor
      # and generate methods that support the translation of workflow states
      state_var = wf.variables.getStateVar()
      for method_id, getter in (
          ('get%s' % UpperCase(state_var), WorkflowState.Getter),
          ('get%sTitle' % UpperCase(state_var), WorkflowState.TitleGetter),
          ('getTranslated%s' % UpperCase(state_var),
                                     WorkflowState.TranslatedGetter),
          ('getTranslated%sTitle' % UpperCase(state_var),
                                     WorkflowState.TranslatedTitleGetter)):
        if not hasattr(prop_holder, method_id):
          method = getter(method_id, wf_id)
          # Attach to portal_type
          setattr(prop_holder, method_id, method)
          prop_holder.security.declareProtected(
                                 Permissions.AccessContentsInformation,
                                 method_id )
  for wf in portal_workflow.getWorkflowsFor(self):
    wf_id = wf.id
    if wf.__class__.__name__ in ('DCWorkflowDefinition', ):
      interaction_id_list = wf.transitions.objectIds()
      for tr_id in interaction_id_list:
        tdef = wf.transitions.get(tr_id, None)
        if tdef.trigger_type == TRIGGER_WORKFLOW_METHOD:
          method_id = convertToMixedCase(tr_id)
          if getattr(klass, method_id, _MARKER) is not _MARKER:
            method = getattr(klass, method_id)
            # Wrap method
            if callable(method):
              if not isinstance(method, WorkflowMethod):
                method = WorkflowMethod(method)
                setattr(klass, method_id, method)
              else:
                # We must be sure that we 
                # are going to register class defined
                # workflow methods to the appropriate transition
                transition_id = method.getTransitionId()
                if transition_id in interaction_id_list:
                  method.registerTransitionAlways(ptype, wf_id, transition_id)
              method.registerTransitionAlways(ptype, wf_id, tr_id)
            else:
              LOG('initializePortalTypeDynamicWorkflowMethods', 100,
                  'WARNING! Can not initialize %s on %s' % \
                    (method_id, str(klass)))
          else:
            prop_holder.security.declareProtected(Permissions.AccessContentsInformation,
                                                  method_id)
            prop_holder.registerWorkflowMethod(method_id, wf_id, tr_id)
  # XXX This part is (more or less...) a copy and paste
  # We need to run this part twice in order to handle interactions of interactions
  # ex. an interaction workflow creates a workflow method which matches
  # the regexp of another interaction workflow
  for wf in portal_workflow.getWorkflowsFor(self) * 2: # This is really necesary
    wf_id = wf.id
    if wf.__class__.__name__ in ('InteractionWorkflowDefinition', ):
      interaction_id_list = wf.interactions.objectIds()
      for tr_id in interaction_id_list:
        tdef = wf.interactions.get(tr_id, None)
        if tdef.trigger_type == TRIGGER_WORKFLOW_METHOD:
          # XXX Prefiltering per portal type would be more efficient
          for imethod_id in tdef.method_id:
            if bool(wildcard_interaction_method_id_matcher.match(imethod_id)):
              # Interactions workflows can use regexp based wildcard methods
              method_id_matcher = re.compile(imethod_id) # XXX What happens if exception ?
              method_id_list = prop_holder.getAccessorMethodIdList() + prop_holder.getWorkflowMethodIdList()\
                             + prop_holder.getClassMethodIdList(klass)
                # XXX - class stuff is missing here
              method_id_list = [x for x in method_id_list if method_id_matcher.match(x)]
            else:
              # Single method
              method_id_list = [imethod_id]
            for method_id in method_id_list:
              if getattr(klass, method_id, _MARKER) is not _MARKER:
                method = getattr(klass, method_id)
                # Wrap method
                if callable(method):
                  if not isinstance(method, WorkflowMethod):
                    method = WorkflowMethod(method)
                    setattr(klass, method_id, method)
                  else:
                    # We must be sure that we 
                    # are going to register class defined
                    # workflow methods to the appropriate transition
                    transition_id = method.getTransitionId()
                    if transition_id in interaction_id_list:
                      method.registerTransitionAlways(ptype, wf_id, transition_id)
                  if tdef.once_per_transaction:
                    method.registerTransitionOncePerTransaction(ptype, wf_id, tr_id)
                  else:
                    method.registerTransitionAlways(ptype, wf_id, tr_id)
                else:
                  LOG('initializePortalTypeDynamicWorkflowMethods', 100,
                      'WARNING! Can not initialize %s on %s' % \
                        (method_id, str(klass)))
              else:
                # set a default security, if this method is not already
                # protected.
                if method_id not in prop_holder.security.names:
                  prop_holder.security.declareProtected(
                      Permissions.AccessContentsInformation, method_id)
                prop_holder.registerWorkflowMethod(method_id, wf_id, tr_id,
                                                       tdef.once_per_transaction)


class Base( CopyContainer,
            PortalContent,
            ActiveObject,
            OFS.History.Historical,
            ERP5PropertyManager ):
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
  isInventoryMovement = 0      #
  isMovement = 0      #
  isDelivery = 0      #
  isInventory = 0     #
  isIndexable = 1     # If set to 0, reindexing will not happen (useful for optimization)
  isPredicate = 0     #
  isTemplate = 0      #
  isDocument = 0      #
  isTempDocument = 0  # If set to 0, instances are temporary.

  # Dynamic method acquisition system (code generation)
  aq_method_generated = {}
  aq_portal_type = {}
  aq_related_generated = 0

  aq_preference_generated = 0
  # FIXME: Preference should not be included in ERP5Type

  # Declarative security - in ERP5 we use AccessContentsInformation to
  # define the right of accessing content properties as opposed
  # to view which is the right to view the object with a form
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Declarative properties
  property_sheets = ( PropertySheet.Base, )

  # Declarative interfaces
  zope.interface.implements(interfaces.ICategoryAccessProvider,
                            interfaces.IValueAccessProvider,
                            )

  # We want to use a default property view
  manage_main = manage_propertiesForm = DTMLFile( 'properties', _dtmldir )
  manage_main._setName('manage_main')

  manage_options = ( PropertyManager.manage_options +
                     SimpleItem.manage_options +
                     OFS.History.Historical.manage_options +
                     CMFCatalogAware.manage_options
                   )

  security.declareProtected( Permissions.ModifyPortalContent, 'setTitle' )
  def setTitle(self, value):
    """ sets the title. (and then reindexObject)"""
    self._setTitle(value)
    self.reindexObject()

  security.declareProtected( Permissions.ModifyPortalContent, 'setDescription' )
  def setDescription(self, value):
    """
      Set the description and reindex.
      Overrides CMFCore/PortalFolder.py implementation, which does not reindex
      and is guarded by inappropriate security check.
    """
    self._setDescription(value)
    self.reindexObject()

  security.declareProtected( Permissions.AccessContentsInformation, 'test_dyn' )
  def test_dyn(self):
    """
    """
    initializeClassDynamicProperties(self, self.__class__)

  def _aq_key(self):
    return (self.portal_type, self.__class__)

  def _propertyMap(self):
    """ Method overload - properties are now defined on the ptype """
    aq_key = self._aq_key()
    self._aq_dynamic('id') # Make sure aq_dynamic has been called once
    if Base.aq_portal_type.has_key(aq_key):
      return tuple(list(getattr(Base.aq_portal_type[aq_key], '_properties', ())) +
                   list(getattr(self, '_local_properties', ())))
    return ERP5PropertyManager._propertyMap(self)

  def _aq_dynamic_pmethod(self, id):
    ptype = self.portal_type
    klass = self.__class__
    aq_key = (ptype, klass) # We do not use _aq_key() here for speed

    #LOG("In _aq_dynamic_pmethod", 0, str((id, ptype, self)))

    if Base.aq_portal_type.has_key(aq_key):
      return getattr(Base.aq_portal_type[aq_key], id, None).__of__(self)

    return None

  def manage_historyCompare(self, rev1, rev2, REQUEST,
                            historyComparisonResults=''):
    return Base.inheritedAttribute('manage_historyCompare')(
          self, rev1, rev2, REQUEST,
          historyComparisonResults=OFS.History.html_diff(
              pformat(rev1.__dict__),
              pformat(rev2.__dict__)))

  def initializePortalTypeDynamicProperties(self):
    """
      Test purpose
    """
    ptype = self.portal_type
    klass = self.__class__
    aq_key = (ptype, klass) # We do not use _aq_key() here for speed
    initializePortalTypeDynamicProperties(self, klass, ptype, aq_key, \
        self.getPortalObject())
    from Products.ERP5Form.PreferenceTool import createPreferenceToolAccessorList
    createPreferenceToolAccessorList(self.getPortalObject())

  def _aq_dynamic(self, id):
    # _aq_dynamic has been created so that callable objects
    # and default properties can be associated per portal type
    # and per class. Other uses are possible (ex. WebSection).
    ptype = self.portal_type
    klass = self.__class__
    aq_key = (ptype, klass) # We do not use _aq_key() here for speed

    # If this is a portal_type property and everything is already defined
    # for that portal_type, try to return a value ASAP
    try:
      property_holder = Base.aq_portal_type[aq_key]
      accessor = getattr(property_holder, id, None)
      if type(accessor) is tuple and id not in RESERVED_TUPLE_PROPERTY:
        accessor = property_holder.createAccessor(id)
      return accessor
    except KeyError:
      property_holder = None

    if id in ('portal_types', 'portal_url', 'portal_workflow'):
      # This is required to precent infinite loop (we need to access portal_types tool)
      return None

    # Proceed with property generation
    if self.isTempObject():
      # If self is a temporary object, generate methods for the base
      # document class rather than for the temporary document class.
      # Otherwise, instances of the base document class would fail
      # in calling such methods, because they are not instances of
      # the temporary document class.
      klass = klass.__bases__[0]
    generated = 0 # Prevent infinite loops

    # Generate class methods
    if not Base.aq_method_generated.has_key(klass):
      initializeClassDynamicProperties(self, klass)
      generated = 1

    # Iterate until an ERP5 Site is obtained.
    portal = self.getPortalObject()
    while portal.portal_type != 'ERP5 Site':
      portal = portal.aq_parent.aq_inner.getPortalObject()

    # Generate portal_type methods
    if not Base.aq_portal_type.has_key(aq_key):
      if ptype == 'Preference':
        # XXX-JPS this should be moved to Preference class
        from Products.ERP5Form.PreferenceTool import updatePreferenceClassPropertySheetList
        updatePreferenceClassPropertySheetList()
      initializePortalTypeDynamicProperties(self, klass, ptype, aq_key, portal)
      generated = 1

    # Generate Related Accessors
    if not Base.aq_related_generated:
      from Utils import createRelatedValueAccessors
      generated = 1
      portal_types = getToolByName(portal, 'portal_types', None)
      generated_bid = {}
      econtext = createExpressionContext(object=self, portal=portal)
      for pid, ps in PropertySheet.__dict__.iteritems():
        if pid[0] != '_':
          base_category_list = []
          for cat in getattr(ps, '_categories', ()):
            if isinstance(cat, Expression):
              result = cat(econtext)
              if isinstance(result, (list, tuple)):
                base_category_list.extend(result)
              else:
                base_category_list.append(result)
            else:
              base_category_list.append(cat)
          for bid in base_category_list:
            if bid not in generated_bid:
              #LOG( "Create createRelatedValueAccessors %s" % bid,0,'')
              createRelatedValueAccessors(property_holder, bid)
              generated_bid[bid] = 1
      for ptype in portal_types.objectValues():
        for bid in ptype.getTypeBaseCategoryList():
          if bid not in generated_bid :
            createRelatedValueAccessors(property_holder, bid)
            generated_bid[bid] = 1

      Base.aq_related_generated = 1

    # Generate preference methods (since side effect is to reset Preference accessors)
    # XXX-JPS - This should be moved to PreferenceTool
    if not Base.aq_preference_generated:
      try :
        from Products.ERP5Form.PreferenceTool import createPreferenceToolAccessorList
        from Products.ERP5Form.PreferenceTool import updatePreferenceClassPropertySheetList
        updatePreferenceClassPropertySheetList()
        createPreferenceToolAccessorList(portal)
      except ImportError, e :
        LOG('Base._aq_dynamic', WARNING,
            'unable to create methods for PreferenceTool', e)
        raise
      Base.aq_preference_generated = 1

    # Always try to return something after generation
    if generated:
      # We suppose that if we reach this point
      # then it means that all code generation has succeeded
      # (no except should hide that). We can safely return None
      # if id does not exist as a dynamic property
      # Baseline: accessor generation failures should always
      #           raise an exception up to the user
      #LOG('_aq_dynamic', 0, 'getattr self = %r, id = %r' % (self, id))
      return getattr(self, id, None)

    # Proceed with standard acquisition
    #LOG('_aq_dynamic', 0, 'not generated; return None for id = %r, self = %r' % (id, self))
    return None

  psyco.bind(_aq_dynamic)

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
                                  default = prop.get('default'), storage_id = prop.get('storage_id'))
      break

  # Debug
  def getOid(self):
    """
      Return ODB oid
    """
    return self._p_oid

  def getOidRepr(self):
    """
      Return ODB oid, in an 'human' readable form.
    """
    from ZODB.utils import oid_repr
    return oid_repr(self._p_oid)

  def getSerial(self):
    """Return ODB Serial."""
    return self._p_serial

  def getHistorySerial(self):
    """Return ODB Serial, in the same format used for history keys"""
    return '.'.join([str(x) for x in unpack('>HHHH', self._p_serial)])

  # Utils
  def _getCategoryTool(self):
    return aq_inner(self.getPortalObject().portal_categories)

  def _getTypesTool(self):
    return aq_inner(self.getPortalObject().portal_types)

  def _doNothing(self, *args, **kw):
    # A method which does nothing (and can be used to build WorkflowMethods which trigger worklow transitions)
    pass

  # Generic accessor
  def _getDefaultAcquiredProperty(self, key, default_value, null_value,
        acquisition_object_id=None, base_category=None, portal_type=None,
        copy_value=0, mask_value=0, sync_value=0, accessor_id=None, depends=None,
        storage_id=None, alt_accessor_id=None, is_list_type=0, is_tales_type=0,
        checked_permission=None):
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

      acquisition_object_id -- List of object Ids where look up properties
                               before looking up on acquired objects
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
    tv = getTransactionalVariable(self)
    if isinstance(portal_type, list):
      portal_type = tuple(portal_type)
    acquisition_key = ('_getDefaultAcquiredProperty', self.getPath(), key,
                       acquisition_object_id, base_category, portal_type,
                       copy_value, mask_value, sync_value, accessor_id, depends,
                       storage_id, alt_accessor_id, is_list_type, is_tales_type,
                       checked_permission)
    if acquisition_key in tv:
      return null_value[0]

    tv[acquisition_key] = 1

    try:
      if storage_id is None: storage_id=key
      #LOG("Get Acquired Property storage_id",0,str(storage_id))
      # Test presence of attribute without acquisition
      # if present, get it in its context, thus we keep acquisition if
      # returned value is an object
      d = getattr(aq_base(self), storage_id, _MARKER)
      if d is not _MARKER:
        value = getattr(self, storage_id, None)
      else:
        value = None
      # If we hold an attribute and mask_value is set, return the attribute
      if mask_value and value not in null_value:
        # Pop context
        if is_tales_type:
          expression = Expression(value)
          econtext = createExpressionContext(self)
          return expression(econtext)
        else:
          if is_list_type:
            # We must provide the first element of the acquired list
            if value in null_value:
              result = None
            else:
              if isinstance(value, (list, tuple)):
                if len(value) is 0:
                  result = None
                else:
                  result = value[0]
              else:
                result = value
          else:
            # Value is a simple type
            result = value
          return result

      #Look at acquisition object before call acquisition
      if acquisition_object_id is not None:
        value = None
        if isinstance(acquisition_object_id, str):
          acquisition_object_id = tuple(acquisition_object_id)
        for object_id in acquisition_object_id:
          try:
            value = self[object_id]
            if value not in null_value:
              break
          except (KeyError, AttributeError):
            pass
        if copy_value:
          if getattr(self, storage_id, None) is None:
            # Copy the value if it does not already exist as an attribute of self
            # Like in the case of orders / invoices
            setattr(self, storage_id, value)
        if is_list_type:
          # We must provide the first element of the acquired list
          if value in null_value:
            result = None
          else:
            if isinstance(value, (list, tuple)):
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
      if result not in null_value:
        return result

      # Retrieve the list of related objects
      #LOG("Get Acquired Property self",0,str(self))
      #LOG("Get Acquired Property portal_type",0,str(portal_type))
      #LOG("Get Acquired Property base_category",0,str(base_category))
      #super_list = self._getValueList(base_category, portal_type=portal_type) # We only do a single jump
      super_list = self._getAcquiredValueList(base_category, portal_type=portal_type,
                                              checked_permission=checked_permission) # Full acquisition
      super_list = [o for o in super_list if o.getPhysicalPath() != self.getPhysicalPath()] # Make sure we do not create stupid loop here
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
          if value in null_value:
            result = None
          else:
            if isinstance(value, (list, tuple)):
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
      if result not in null_value:
        return result
      else:
        #LOG("alt_accessor_id",0,str(alt_accessor_id))
        if alt_accessor_id is not None:
          for id in alt_accessor_id:
            #LOG("method",0,str(id))
            method = getattr(self, id, None)
            if callable(method):
              try:
                result = method(checked_permission=checked_permission)
              except TypeError:
                result = method()
              if result not in null_value:
                if is_list_type:
                  if isinstance(result, (list, tuple)):
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
    finally:
      # Pop the acquisition context.
      try:
        del tv[acquisition_key]
      except KeyError:
        pass

  def _getAcquiredPropertyList(self, key, default_value, null_value,
     base_category, portal_type=None, copy_value=0, mask_value=0, sync_value=0, append_value=0,
     accessor_id=None, depends=None, storage_id=None, alt_accessor_id=None,
     acquisition_object_id=None,
     is_list_type=0, is_tales_type=0, checked_permission=None):
    """
      Default accessor. Implements the default
      attribute accessor.

      portal_type
      copy_value
      depends

    """
    # Push context to prevent loop
    tv = getTransactionalVariable(self)
    if isinstance(portal_type, list):
      portal_type = tuple(portal_type)
    acquisition_key = ('_getAcquiredPropertyList', self.getPath(), key, base_category,
                       portal_type, copy_value, mask_value, sync_value,
                       accessor_id, depends, storage_id, alt_accessor_id,
                       acquisition_object_id, is_list_type, is_tales_type,
                       checked_permission)
    if acquisition_key in tv:
      return null_value

    tv[acquisition_key] = 1

    try:
      if storage_id is None: storage_id=key
      value = getattr(self, storage_id, None)
      if mask_value and value is not None:
        if is_tales_type:
          expression = Expression(value)
          econtext = createExpressionContext(self)
          return expression(econtext)
        else:
          return value
      super_list = []
      if acquisition_object_id is not None:
        if isinstance(acquisition_object_id, str):
          acquisition_object_id = tuple(acquisition_object_id)
        for object_id in acquisition_object_id:
          try:
            acquisition_object = self[object_id]
            super_list.append(acquisition_object)
          except (KeyError, AttributeError):
            pass
      super_list.extend(self._getAcquiredValueList(
                                          base_category,
                                          portal_type=portal_type,
                                          checked_permission=checked_permission))
                                          # Full acquisition
      super_list = [o for o in super_list if o.getPhysicalPath() != self.getPhysicalPath()] # Make sure we do not create stupid loop here
      if len(super_list) > 0:
        value = []
        for super in super_list:
          if accessor_id is None:
            if is_list_type:
              result = super.getPropertyList(key)
              if isinstance(result, (list, tuple)):
                value += result
              else:
                value += [result]
            else:
              value += [super.getProperty(key)]
          else:
            method = getattr(super, accessor_id)
            if is_list_type:
              result = method() # We should add depends here
              if isinstance(result, (list, tuple)):
                value += result
              else:
                value += [result]
            else:
              value += [method()] # We should add depends here
        if copy_value:
          if not hasattr(self, storage_id):
            setattr(self, storage_id, value)
        return value
      else:
        # ?????
        if copy_value:
          return getattr(self,storage_id, default_value)
        else:
          return default_value
    finally:
      # Pop the acquisition context.
      try:
        del tv[acquisition_key]
      except KeyError:
        pass

  security.declareProtected( Permissions.AccessContentsInformation, 'getProperty' )
  def getProperty(self, key, d=_MARKER, **kw):
    """getProperty is the generic accessor to all properties and categories
    defined on this object.
    If an accessor exists for this property, the accessor will be called,
    default value will be passed to the accessor as first positional argument.

    XXX Usage of getProperty is BAD. It should either be removed
    or reused
    """
    accessor_name = 'get' + UpperCase(key)
    aq_self = aq_base(self)
    if getattr(aq_self, accessor_name, None) is not None:
      method = getattr(self, accessor_name)
      if d is not _MARKER:
        try:
          # here method is a method defined on the class, we don't know if the
          # method supports default argument or not, so we'll try and if the
          # method doesn't accepts it, we ignore default argument.
          return method(d, **kw)
        except TypeError:
          pass
      return method(**kw)
    # Try to get a portal_type property (Implementation Dependent)
    aq_key = self._aq_key()
    aq_portal_type = Base.aq_portal_type
    if aq_key not in aq_portal_type:
      try:
        self._aq_dynamic(accessor_name)
      except AttributeError:
        pass
    if hasattr(aq_portal_type[aq_key], accessor_name):
      method = getattr(self, accessor_name)
      if d is not _MARKER:
        try:
          return method(d, **kw)
        except TypeError:
          pass
      return method(**kw)
    # Try a mono valued accessor if it is available
    # and return it as a list
    if accessor_name.endswith('List'):
      mono_valued_accessor_name = accessor_name[:-4]
      if hasattr(aq_portal_type[aq_key], mono_valued_accessor_name):
        method = getattr(self, mono_valued_accessor_name)
        # We have a monovalued property
        if d is _MARKER:
          result = method(**kw)
        else:
          try:
            result = method(d, **kw)
          except TypeError:
            result = method(**kw)
        if not isinstance(result, (list, tuple)):
          result = [result]
        return result
    if d is not _MARKER:
      return ERP5PropertyManager.getProperty(self, key, d=d, **kw)
    return ERP5PropertyManager.getProperty(self, key, **kw)

  security.declareProtected( Permissions.AccessContentsInformation, 'getPropertyList' )
  def getPropertyList(self, key, d=None):
    """Same as getProperty, but for list properties.
    """
    return self.getProperty('%s_list' % key, d=d)

  security.declareProtected( Permissions.ModifyPortalContent, 'setPropertyList' )
  def setPropertyList(self, key, value, **kw):
    """Same as setProperty, but for list properties.
    """
    return self.setProperty('%s_list' % key, value, **kw)

  security.declareProtected( Permissions.ModifyPortalContent, 'setProperty' )
  def setProperty(self, key, value, type='string', **kw):
    """
      Previous Name: setValue

      New Name: we use the naming convention of
      /usr/lib/zope/lib/python/OFS/PropertySheets.py

      TODO: check possible conflicts

      Generic accessor. Calls the real accessor
    """
    self._setProperty(key, value, type=type, **kw)
    self.reindexObject()

  def _setProperty(self, key, value, type=None, **kw):
    """
      Previous Name: _setValue

      Generic accessor. Calls the real accessor

      **kw allows to call setProperty as a generic setter (ex. setProperty(value_uid, portal_type=))
    """
    if type is not None: # Speed
      if type in list_types: # Patch for OFS PropertyManager
        key += '_list'
    accessor_name = '_set' + UpperCase(key)
    aq_self = aq_base(self)
    # We must use aq_self
    # since we will change the value on self
    # rather than through implicit aquisition
    if getattr(aq_self, accessor_name, None) is not None:
      method = getattr(self, accessor_name)
      return method(value, **kw)
    public_accessor_name = 'set' + UpperCase(key)
    if getattr(aq_self, public_accessor_name, None) is not None:
      method = getattr(self, public_accessor_name)
      return method(value, **kw)
    # Try to get a portal_type property (Implementation Dependent)
    aq_key = self._aq_key()
    aq_portal_type = Base.aq_portal_type
    if not aq_portal_type.has_key(aq_key):
      self._aq_dynamic('id') # Make sure _aq_dynamic has been called once
    if getattr(aq_portal_type[aq_key], accessor_name, None) is not None:
      method = getattr(self, accessor_name)
      # LOG("Base.py", 0, "method = %s, name = %s" %(method, accessor_name))
      return method(value, **kw)
    if getattr(aq_portal_type[aq_key], public_accessor_name, None) is not None:
      method = getattr(self, public_accessor_name)
      return method(value, **kw)
    # Try a mono valued setter if it is available
    # and call it
    if accessor_name.endswith('List'):
      mono_valued_accessor_name = accessor_name[:-4]
      mono_valued_public_accessor_name = public_accessor_name[:-4]
      method = None
      if hasattr(aq_portal_type[aq_key], mono_valued_accessor_name):
        method = getattr(self, mono_valued_accessor_name)
      elif hasattr(aq_portal_type[aq_key], mono_valued_public_accessor_name):
        method = getattr(self, mono_valued_public_accessor_name)
      if method is not None:
        if isinstance(value, (list, tuple)):
          value_len = len(value)
          if value_len == 1:
            mono_value = value[0]
            return method(mono_value, **kw)
        raise TypeError, \
           "A mono valued property must be set with a list of len 1"
    # Finaly use standard PropertyManager
    #LOG("Changing attr: ",0, key)
    # If we are here, this means we do not use a property that
    # comes from an ERP5 PropertySheet, we should use the
    # PropertyManager
    if ERP5PropertyManager.hasProperty(self,key):
      ERP5PropertyManager._updateProperty(self, key, value)
    else:
      ERP5PropertyManager._setProperty(self, key, value, type=type)
    # This should not be there, because this ignore all checks made by
    # the PropertyManager. If there is problems, please complain to
    # seb@nexedi.com
    #except:
    #  # This should be removed if we want strict property checking
    #  setattr(self, key, value)
    return (self,)

  def _setPropValue(self, key, value, **kw):
    self._wrapperCheck(value)
    if isinstance(value, list):
      value = tuple(value)
    accessor_name = '_set' + UpperCase(key)
    aq_self = aq_base(self)
    # We must use aq_self
    # since we will change the value on self
    # rather than through implicit aquisition
    if hasattr(aq_self, accessor_name):
      method = getattr(self, accessor_name)
      method(value, **kw)
      return
    public_accessor_name = 'set' + UpperCase(key)
    if hasattr(aq_self, public_accessor_name):
      method = getattr(self, public_accessor_name)
      method(value, **kw)
      return
    # Try to get a portal_type property (Implementation Dependent)
    aq_key = self._aq_key()
    if not Base.aq_portal_type.has_key(aq_key):
      self._aq_dynamic('id') # Make sure _aq_dynamic has been called once
    if hasattr(Base.aq_portal_type[aq_key], accessor_name):
      method = getattr(self, accessor_name)
      method(value, **kw)
      return
    if hasattr(Base.aq_portal_type[aq_key], public_accessor_name):
      method = getattr(self, public_accessor_name)
      method(value, **kw)
      return
    # Finaly use standard PropertyManager
    #LOG("Changing attr: ",0, key)
    #try:
    ERP5PropertyManager._setPropValue(self, key, value)
    #except ConflictError:
    #  raise
    # This should not be there, because this ignore all checks made by
    # the PropertyManager. If there is problems, please complain to
    # seb@nexedi.com
    #except:
    #  # This should be removed if we want strict property checking
    #  setattr(self, key, value)

  security.declareProtected( Permissions.View, 'hasProperty' )
  def hasProperty(self, key):
    """
      Previous Name: hasValue

      Generic accessor. Calls the real accessor
      and returns 0 if it fails.

      The idea of hasProperty is to call the tester methods.
      It will return True only if a property was defined on the object.
      (either by calling a Tester accessor or by checking if a local
      property was added).

      It will return False if the property is not part of the list
      of valid properties (ie. the list of properties defined in
      PropertySheets) or if the property has never been updated.

      NOTE - One possible issue in the current implementation is that a
      property which is set to its default value will be considered
      as not being defined.

      Ex. self.hasProperty('first_name') on a Person object
      returns False if the first name was never defined and
      even if self.getProperty('first_name') returns ''
    """
    accessor_name = 'has' + UpperCase(key)
    if hasattr(self, accessor_name):
      method = getattr(self, accessor_name)
      try:
        return method()
      except ConflictError:
        raise
      except:
        return 0
    else:
      # Check in local properties (which obviously were defined at some point)
      for p_id in self.propertyIds():
        if key == p_id:
          return 1
      return 0

  security.declareProtected( Permissions.View, 'hasCategory' )
  def hasCategory(self, key):
    """
      Previous Name: hasValue

      Generic accessor. Calls the real accessor
      and returns 0 if it fails
    """
    return key in self.getCategoryList()

  # Accessors are not workflow methods by default
  # Ping provides a dummy method to trigger automatic methods
  # XXX : maybe an empty edit is enough (self.edit())
  def ping(self):
    pass

  ping = WorkflowMethod(ping)

  # Object attributes update method
  def _edit(self, REQUEST=None, force_update=0, reindex_object=0, 
            keep_existing=0, activate_kw=None, edit_order=[], restricted=0, **kw):
    """
      Generic edit Method for all ERP5 object
      The purpose of this method is to update attributed, eventually do
      some kind of type checking according to the property sheet and index
      the object.

      Each time attributes of an object are updated, they should
      be updated through this generic edit method

      Modification date is supported by edit_workflow in ERP5
      There is no need to change it here.

      keep_existing -- if set to 1 or True, only those properties for which
      hasProperty is False will be updated.
    """
    modified_property_dict = self._v_modified_property_dict = {}
    modified_object_dict = {}

    key_list = kw.keys()
    unordered_key_list = [k for k in key_list if k not in edit_order]
    ordered_key_list = [k for k in edit_order if k in key_list]
    second_try_key_list = []
    restricted_method = []    
    if restricted:
      # retrieve list of accessors which doesn't use default permissions
      aq_key = self._aq_key()
      aq_portal_type = Base.aq_portal_type
      if aq_key not in aq_portal_type:
        try:
          self._aq_dynamic("")
        except AttributeError:
          pass
      prop_holder = aq_portal_type[aq_key]
      for permissions in prop_holder.__ac_permissions__:
        if permissions[0] not in ('Access contents information', 'Modify portal content'):
          for method in permissions[1]:
            restricted_method.append(method)

    def setChangedPropertyList(key_list):
      not_modified_list = []
      for key in key_list:
        # We only change if the value is different
        # This may be very long...
        old_value = None
        if not force_update:
          try:
            old_value = self.getProperty(key, evaluate=0)
          except TypeError:
            old_value = self.getProperty(key)

        if old_value != kw[key] or force_update:
          # We keep in a thread var the previous values
          # this can be useful for interaction workflow to implement lookups
          # XXX If iteraction workflow script is triggered by edit and calls
          # edit itself, this is useless as the dict will be overwritten
          # If the keep_existing flag is set to 1, we do not update properties which are defined
          if not keep_existing or not self.hasProperty(key):
            if restricted:
              accessor_name = 'set' + UpperCase(key)
              if accessor_name in restricted_method:
                # will raise Unauthorized when not allowed
                guarded_getattr(self, accessor_name)
            modified_property_dict[key] = old_value
            if key != 'id':
              modified_object_list = self._setProperty(key, kw[key])
              # BBB: if the setter does not return anything, assume
              # that self has been modified.
              if modified_object_list is None:
                modified_object_list = (self,)
              for o in modified_object_list:
                # XXX using id is not quite nice, but getUID causes a
                # problem at the bootstrap of an ERP5 site. Therefore,
                # objects themselves cannot be used as keys.
                modified_object_dict[id(o)] = o
            else:
              self.setId(kw['id'], reindex=reindex_object)
        else:
          not_modified_list.append(key)
      return not_modified_list

    unmodified_key_list = setChangedPropertyList(unordered_key_list)
    setChangedPropertyList(unmodified_key_list)
    # edit_order MUST be enforced, and done at the complete end
    setChangedPropertyList(ordered_key_list)

    if reindex_object:
      for o in modified_object_dict.itervalues():
        o.reindexObject(activate_kw=activate_kw)

  security.declareProtected( Permissions.ModifyPortalContent, 'setId' )
  def setId(self, id, reindex = 1):
    """
        changes id of an object by calling the Zope machine
    """
    tryMethodCallWithTemporaryPermission(self, 'Copy or Move',
        self.aq_inner.aq_parent.manage_renameObject, (self.id, id), {}, CopyError)
    # Do not flush any more, because it generates locks

  security.declareProtected( Permissions.ModifyPortalContent,
                             'updateRelatedContent' )
  def updateRelatedContent(self, previous_category_url, new_category_url):
    """
        updateRelatedContent is implemented by portal_categories
    """
    self._getCategoryTool().updateRelatedContent(self,
                                previous_category_url, new_category_url)

  security.declareProtected(Permissions.ModifyPortalContent, 'edit')
  def edit(self, REQUEST=None, force_update=0, reindex_object=1, **kw):
    """
      Generic edit Method for all ERP5 object
    """
    return self._edit(REQUEST=REQUEST, force_update=force_update,
                      reindex_object=reindex_object, restricted=1, **kw)

  # XXX Is this useful ? (Romain)
  edit = WorkflowMethod(edit)

  # Accessing object property through ERP5ish interface
  security.declareProtected( Permissions.View, 'getPropertyIdList' )
  def getPropertyIdList(self):
    return self.propertyIds()

  security.declareProtected( Permissions.View, 'getPropertyValueList' )
  def getPropertyValueList(self):
    return self.propertyValues()

  security.declareProtected( Permissions.View, 'getPropertyItemList' )
  def getPropertyItemList(self):
    return self.propertyItems()

  security.declareProtected( Permissions.View, 'getPropertyMap' )
  def getPropertyMap(self):
    return self.propertyMap()

  # ERP5 content properties interface
  security.declareProtected( Permissions.View, 'getContentPropertyIdList' )
  def getContentPropertyIdList(self):
    """
      Return content properties of the current instance.
      Content properties are filtered out in getPropertyIdList so 
      that rendering in ZMI is compatible with Zope standard properties
    """
    return [property['id'] for property in self._erp5_properties if property['type'] == 'content']

  security.declareProtected( Permissions.View, 'getStandardPropertyIdList' )
  def getStandardPropertyIdList(self):
    """
      Return standard properties of the current instance.
      Unlike getPropertyIdList, properties are not converted or rewritten here.
    """
    return [property['id'] for property in self._erp5_properties if property['type'] != 'content']

  # Catalog Related
  security.declareProtected( Permissions.View, 'getObject' )
  def getObject(self, relative_url = None, REQUEST=None):
    """
      Returns self - useful for ListBox when we do not know
      if the getObject is called on a brain object or on the actual object
    """
    return self

  def getDocumentInstance(self):
    """
      Returns self
      Returns instance if category through document_instance relation
    """
    return self

  def asSQLExpression(self, strict_membership=0, table='category', base_category = None):
    """
      Any document can be used as a Category. It can therefore
      serve in a Predicate and must be rendered as an sql expression. This
      can be useful to create reporting trees based on the
      ZSQLCatalog whenever documents are used rather than categories

      TODO:
        - strict_membership is not implemented
    """
    if isinstance(base_category, str):
      base_category = self.portal_categories[base_category]
    if base_category is None:
      sql_text = '(%s.category_uid = %s)' % \
          (table, self.getUid())
    else:
      sql_text = '(%s.category_uid = %s AND %s.base_category_uid = %s)' % \
          (table, self.getUid(), table, base_category.getBaseCategoryUid())
    return sql_text

  security.declareProtected( Permissions.AccessContentsInformation,
                             'getParentSQLExpression' )
  def getParentSQLExpression(self, table = 'catalog', strict_membership = 0):
    """
      Builds an SQL expression to search children and subclidren
    """
    return "%s.parent_uid = %s" % (table, self.getUid())

  security.declareProtected( Permissions.AccessContentsInformation,
                             'getParentUid' )
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

  security.declareProtected( Permissions.AccessContentsInformation,
                             'getParentTitleOrId' )
  def getParentTitleOrId(self):
    """
      Returns the title or the id of the parent
    """
    return self.aq_inner.aq_parent.getTitleOrId()

  security.declareProtected( Permissions.AccessContentsInformation,
                             'getParentRelativeUrl' )
  def getParentRelativeUrl(self):
    """
      Returns the title or the id of the parent
    """
    return self.aq_inner.aq_parent.getRelativeUrl()

  security.declareProtected( Permissions.AccessContentsInformation,
                             'getParentId' )
  def getParentId(self):
    """
      Returns the id of the parent
    """
    return self.aq_inner.aq_parent.getId()

  security.declareProtected( Permissions.AccessContentsInformation,
                             'getParentTitle' )
  def getParentTitle(self):
    """
      Returns the title or of the parent
    """
    return self.aq_inner.aq_parent.getTitle()

  security.declareProtected( Permissions.AccessContentsInformation,
                             'getParentValue' )
  def getParentValue(self):
    """
      Returns the parent of the current object.
    """
    return self.aq_inner.aq_parent

  security.declareProtected( Permissions.AccessContentsInformation, 'getParent' )
  def getParent(self):
    """Returns the parent of the current object (whereas it should return the
    relative_url of the parent for consistency with CMFCategory.

    This method still uses this behaviour, because some part of the code still
    uses getParent instead of getParentValue. This may change in the future.
    """
    warnings.warn("getParent implementation still returns the parent object, "\
                  "which is inconsistant with CMFCategory API. "\
                  "Use getParentValue instead", FutureWarning)
    return self.getParentValue() # Compatibility

  security.declareProtected( Permissions.AccessContentsInformation, 'getUid' )
  def getUid(self):
    """
      Returns the UID of the object. Eventually reindexes
      the object in order to make sure there is a UID
      (useful for import / export).

      WARNING : must be updated for circular references issues
    """
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

  security.declareProtected(Permissions.AccessContentsInformation, 'getCompactLogicalPath')
  def getCompactLogicalPath(self, REQUEST=None) :
    """
      Returns a compact representation of the absolute path of an object
      using compact titles when available
    """
    pathlist = self.getPhysicalPath()
    objectlist = [self.getPhysicalRoot()]
    for element in pathlist[1:] :
      objectlist.append(objectlist[-1][element])
    return '/' + join([object.getCompactTitle() for object in objectlist[1:]], '/')

  security.declareProtected(Permissions.AccessContentsInformation, 'getUrl')
  def getUrl(self, REQUEST=None):
    """
      Returns the absolute path of an object
    """
    return join(self.getPhysicalPath(),'/')

  # Old name - for compatibility
  security.declareProtected(Permissions.AccessContentsInformation, 'getPath')
  getPath = getUrl

  security.declareProtected(Permissions.AccessContentsInformation, 'getRelativeUrl')
  def getRelativeUrl(self):
    """
      Returns the url of an object relative to the portal site.
    """
    return self.portal_url.getRelativeUrl(self)

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getAbsoluteUrl')
  def getAbsoluteUrl(self):
    """
      Returns the absolute url of an object.
    """
    return self.absolute_url()

  security.declareProtected(Permissions.AccessContentsInformation, 'getPortalObject')
  def getPortalObject(self):
    """
      Returns the portal object
    """
    return self.aq_inner.aq_parent.getPortalObject()

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
  security.declareProtected( Permissions.ManagePortal, 'showDict' )
  def showDict(self):
    """
      Returns the dictionnary of the object
      Only for debugging
    """
    return copy(self.__dict__)

  security.declareProtected( Permissions.ManagePortal, 'showPermissions' )
  def showPermissions(self, all=1):
    """
      Return the tuple of permissions
      Only for debugging
    """
    permission_list = []
    for permission in self.ac_inherited_permissions(all=all):
      name, value = permission[:2]
      role_list = Permission(name, value, self).getRoles(default=[])
      permission_list.append((name, role_list))

    return tuple(permission_list)

  security.declareProtected( Permissions.AccessContentsInformation, 'getViewPermissionOwner' )
  def getViewPermissionOwner(self):
    """Returns the user ID of the user with 'Owner' local role on this
    document, if the Owner role has View permission.

    If there is more than one Owner local role, the result is undefined.
    """
    if 'Owner' in rolesForPermissionOn(Permissions.View, self):
      owner_list = self.users_with_local_role('Owner')
      if owner_list:
        return owner_list[0]

  # Private accessors for the implementation of relations based on
  # categories
  def _setValue(self, id, target, spec=(), filter=None, portal_type=(), keep_default=1,
                                  checked_permission=None):
    start_string = "%s/" % id
    start_string_len = len(start_string)
    if target is None :
      path = target
    elif isinstance(target, str):
      # We have been provided a string
      path = target
      if path.startswith(start_string): path = path[start_string_len:] # Prevent duplicating base category
    elif isinstance(target, (tuple, list)):
      # We have been provided a list or tuple
      path_list = []
      for target_item in target:
        if isinstance(target_item, str):
          path = target_item
        else:
          path = target_item.getRelativeUrl()
        if path.startswith(start_string): path = path[start_string_len:] # Prevent duplicating base category
        path_list += [path]
      path = path_list
    else:
      # We have been provided an object
      # Find the object
      path = target.getRelativeUrl()
      if path.startswith(start_string): path = path[start_string_len:] # Prevent duplicating base category
    self._setCategoryMembership(id, path, spec=spec, filter=filter, portal_type=portal_type,
                                base=0, keep_default=keep_default,
                                checked_permission=checked_permission)

  security.declareProtected( Permissions.ModifyPortalContent, '_setValueList' )
  _setValueList = _setValue

  security.declareProtected( Permissions.ModifyPortalContent, 'setValue' )
  def setValue(self, id, target, spec=(), filter=None, portal_type=(), keep_default=1, checked_permission=None):
    self._setValue(id, target, spec=spec, filter=filter, portal_type=portal_type, keep_default=keep_default,
                       checked_permission=checked_permission)
    self.reindexObject()

  security.declareProtected( Permissions.ModifyPortalContent, 'setValueList' )
  setValueList = setValue

  def _setDefaultValue(self, id, target, spec=(), filter=None, portal_type=(), checked_permission=None):
    start_string = "%s/" % id
    start_string_len = len(start_string)
    if target is None :
      path = target
    elif isinstance(target, str):
      # We have been provided a string
      path = target
      if path.startswith(start_string): path = path[start_string_len:] # Prevent duplicating base category
    else:
      # We have been provided an object
      # Find the object
      path = target.getRelativeUrl()
      if path.startswith(start_string): path = path[start_string_len:] # Prevent duplicating base category
    self._setDefaultCategoryMembership(id, path, spec=spec, filter=filter,
                                       portal_type=portal_type, base=0,
                                       checked_permission=checked_permission)

  security.declareProtected(Permissions.ModifyPortalContent, 'setDefaultValue' )
  def setDefaultValue(self, id, target, spec=(), filter=None, portal_type=()):
    self._setDefaultValue(id, target, spec=spec, filter=filter, portal_type=portal_type,
                              checked_permission=None)
    self.reindexObject()

  def _getDefaultValue(self, id, spec=(), filter=None, portal_type=(), checked_permission=None):
    path = self._getDefaultCategoryMembership(id, spec=spec, filter=filter,
                                      portal_type=portal_type,base=1,
                                      checked_permission=checked_permission)
    if path is None:
      return None
    else:
      return self._getCategoryTool().resolveCategory(path)

  security.declareProtected( Permissions.View, 'getDefaultValue' )
  getDefaultValue = _getDefaultValue

  def _getValueList(self, id, spec=(), filter=None, portal_type=(), checked_permission=None):
    ref_list = []
    for path in self._getCategoryMembershipList(id, spec=spec, filter=filter,
                                                  portal_type=portal_type, base=1,
                                                  checked_permission=checked_permission):
      # LOG('_getValueList',0,str(path))
      try:
        value = self._getCategoryTool().resolveCategory(path)
        if value is not None: ref_list.append(value)
      except ConflictError:
        raise
      except:
        LOG("ERP5Type WARNING",0,"category %s has no object value" % path, error=sys.exc_info())
    return ref_list

  security.declareProtected(Permissions.AccessContentsInformation, 
                            'getValueList')
  getValueList = _getValueList

  def _getDefaultAcquiredValue(self, id, spec=(), filter=None, portal_type=(),
                               evaluate=1, checked_permission=None, **kw):
    path = self._getDefaultAcquiredCategoryMembership(id, spec=spec, filter=filter,
                                                  portal_type=portal_type, base=1,
                                                  checked_permission=checked_permission,
                                                  **kw)
    if path is None:
      return None
    else:
      return self._getCategoryTool().resolveCategory(path)

  security.declareProtected(Permissions.AccessContentsInformation, 
                            'getDefaultAcquiredValue')
  getDefaultAcquiredValue = _getDefaultAcquiredValue

  def _getAcquiredValueList(self, id, spec=(), filter=None, **kw):
    ref_list = []
    for path in self._getAcquiredCategoryMembershipList(id, base=1,
                                                spec=spec,  filter=filter, **kw):
      category = self._getCategoryTool().resolveCategory(path)
      if category is not None:
        ref_list.append(category)
    return ref_list

  security.declareProtected(Permissions.AccessContentsInformation, 
                            'getAcquiredValueList')
  getAcquiredValueList = _getAcquiredValueList

  def _getDefaultRelatedValue(self, id, spec=(), filter=None, portal_type=(),
                              strict_membership=0, strict="deprecated",
                              checked_permission=None):
    # backward compatibility to keep strict keyword working
    if strict != "deprecated" : 
      strict_membership = strict
    value_list = self._getRelatedValueList(
                                id, spec=spec, filter=filter,
                                portal_type=portal_type,
                                strict_membership=strict_membership,
                                checked_permission=checked_permission)
    try:
      return value_list[0]
    except IndexError:
      return None

  security.declareProtected(Permissions.View, 'getDefaultRelatedValue')
  getDefaultRelatedValue = _getDefaultRelatedValue

  def _getRelatedValueList(self, *args, **kw):
    # backward compatibility to keep strict keyword working
    if 'strict' in kw:
      kw['strict_membership'] = kw.pop('strict')
    return self._getCategoryTool().getRelatedValueList(self, *args, **kw)

  security.declareProtected(Permissions.View, 'getRelatedValueList')
  getRelatedValueList = _getRelatedValueList

  def _getDefaultRelatedProperty(self, id, property_name, spec=(), filter=None,
                                 portal_type=(), strict_membership=0,
                                 checked_permission=None):
    property_list = self._getCategoryTool().getRelatedPropertyList(self, id,
                          property_name=property_name,
                          spec=spec, filter=filter,
                          portal_type=portal_type,
                          strict_membership=strict_membership,
                          checked_permission=checked_permission)
    try:
      return property_list[0]
    except IndexError:
      return None

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getDefaultRelatedProperty')
  getDefaultRelatedProperty = _getDefaultRelatedProperty


  def _getRelatedPropertyList(self, id, property_name, spec=(), filter=None,
                              portal_type=(), strict_membership=0,
                              checked_permission=None):
    return self._getCategoryTool().getRelatedPropertyList(self, id,
                          property_name=property_name,
                          spec=spec, filter=filter,
                          portal_type=portal_type,
                          strict_membership=strict_membership,
                          checked_permission=checked_permission)

  security.declareProtected( Permissions.AccessContentsInformation,
                             'getRelatedPropertyList' )
  getRelatedPropertyList = _getRelatedPropertyList

  security.declareProtected( Permissions.View, 'getValueUidList' )
  def getValueUidList(self, id, spec=(), filter=None, portal_type=(), checked_permission=None):
    uid_list = []
    for o in self._getValueList(id, spec=spec, filter=filter, portal_type=portal_type,
                                    checked_permission=checked_permission):
      uid_list.append(o.getUid())
    return uid_list

  security.declareProtected( Permissions.View, 'getValueUids' )
  getValueUids = getValueUidList # DEPRECATED

  def _setValueUidList(self, id, uids, spec=(), filter=None, portal_type=(), keep_default=1,
                                       checked_permission=None):
    # We must do an ordered list so we can not use the previous method
    # self._setValue(id, self.portal_catalog.getObjectList(uids), spec=spec)
    references = []
    if type(uids) not in (type(()), type([])):
      uids = [uids]
    for uid in uids:
      references.append(self.portal_catalog.getObject(uid))
    self._setValue(id, references, spec=spec, filter=filter, portal_type=portal_type,
                                   keep_default=keep_default, checked_permission=checked_permission)

  security.declareProtected( Permissions.ModifyPortalContent, '_setValueUidList' )
  _setValueUids = _setValueUidList # DEPRECATED

  security.declareProtected( Permissions.ModifyPortalContent, 'setValueUidList' )
  def setValueUidList(self, id, uids, spec=(), filter=None, portal_type=(), keep_default=1, checked_permission=None):
    self._setValueUids(id, uids, spec=spec, filter=filter, portal_type=portal_type, 
                                 keep_default=keep_default, checked_permission=checked_permission)
    self.reindexObject()

  security.declareProtected( Permissions.ModifyPortalContent, 'setValueUidList' )
  setValueUids = setValueUidList # DEPRECATED

  def _setDefaultValueUid(self, id, uid, spec=(), filter=None, portal_type=(),
                                         checked_permission=None):
    # We must do an ordered list so we can not use the previous method
    # self._setValue(id, self.portal_catalog.getObjectList(uids), spec=spec)
    references = self.portal_catalog.getObject(uid)
    self._setDefaultValue(id, references, spec=spec, filter=filter, portal_type=portal_type,
                                          checked_permission=checked_permission)

  security.declareProtected( Permissions.ModifyPortalContent, 'setDefaultValueUid' )
  def setDefaultValueUid(self, id, uid, spec=(), filter=None, portal_type=(), checked_permission=None):
    self._setDefaultValueUid(id, uid, spec=spec, filter=filter, portal_type=portal_type,
                                      checked_permission=checked_permission)
    self.reindexObject()

  # Private accessors for the implementation of categories
  def _setCategoryMembership(self, *args, **kw):
    self._getCategoryTool()._setCategoryMembership(self, *args, **kw)
    #self.activate().edit() # Do nothing except call workflow method
    # XXX This is a problem - it is used to circumvent a lack of edit

  security.declareProtected( Permissions.ModifyPortalContent, 'setCategoryMembership' )
  def setCategoryMembership(self, *args, **kw):
    self._setCategoryMembership(*args, **kw)
    self.reindexObject()

  def _setDefaultCategoryMembership(self, category, node_list,
                                    spec=(), filter=None, portal_type=(), base=0,
                                    checked_permission=None):
    self._getCategoryTool().setDefaultCategoryMembership(self, category,
                     node_list, spec=spec, filter=filter, portal_type=portal_type, base=base,
                                checked_permission=checked_permission)

  security.declareProtected( Permissions.ModifyPortalContent, 'setDefaultCategoryMembership' )
  def setDefaultCategoryMembership(self, category, node_list,
                                           spec=(), filter=None, portal_type=(), base=0,
                                           checked_permission=None):
    self._setDefaultCategoryMembership(category, node_list, spec=spec, filter=filter,
                                       portal_type=portal_type, base=base,
                                       checked_permission=checked_permission)
    self.reindexObject()

  def _getCategoryMembershipList(self, category, spec=(), filter=None,
      portal_type=(), base=0, keep_default=1, checked_permission=None, **kw):
    """
      This returns the list of categories for an object
    """
    return self._getCategoryTool().getCategoryMembershipList(self, category,
        spec=spec, filter=filter, portal_type=portal_type, base=base,
        keep_default=keep_default, checked_permission=checked_permission, **kw)

  security.declareProtected( Permissions.AccessContentsInformation, 'getCategoryMembershipList' )
  getCategoryMembershipList = _getCategoryMembershipList

  def _getAcquiredCategoryMembershipList(self, category, spec=(), filter=None,
      portal_type=(), base=0, keep_default=1, checked_permission=None, **kw):
    """
      Returns the list of acquired categories
    """
    return self._getCategoryTool().getAcquiredCategoryMembershipList(self,
                             category, spec=spec, filter=filter,
                             portal_type=portal_type, base=base,
                             keep_default=keep_default,
                             checked_permission=checked_permission, **kw )

  security.declareProtected( Permissions.AccessContentsInformation,
                                           'getAcquiredCategoryMembershipList' )
  getAcquiredCategoryMembershipList = _getAcquiredCategoryMembershipList

  def _getCategoryMembershipItemList(self, category, spec=(), filter=None, portal_type=(), base=0,
                                                     checked_permission=None):
    membership_list = self._getCategoryMembershipList(category,
                            spec=spec, filter=filter, portal_type=portal_type, base=base,
                            checked_permission=checked_permission)
    return [(x, x) for x in membership_list]

  def _getAcquiredCategoryMembershipItemList(self, category, spec=(),
             filter=None, portal_type=(), base=0, method_id=None, sort_id='default',
             checked_permission=None):
    # Standard behaviour - should be OK
    # sort_id should be None for not sort - default behaviour in other methods
    if method_id is None and sort_id in (None, 'default'):
      membership_list = self._getAcquiredCategoryMembershipList(category,
                           spec = spec, filter=filter, portal_type=portal_type, base=base,
                           checked_permission=checked_permission)
      if sort_id == 'default':
        membership_list.sort()
      return [(x, x) for x in membership_list]
    # Advanced behaviour XXX This is new and needs to be checked
    membership_list = self._getAcquiredCategoryMembershipList(category,
                           spec = spec, filter=filter, portal_type=portal_type, base=1,
                           checked_permission=checked_permission)
    result = []
    for path in membership_list:
      value = self._getCategoryTool().resolveCategory(path)
      if value is not None:
        result += [value]
    result.sort(key=lambda x: getattr(x,sort_id)())
    if method_id is None:
      return [(x, x) for x in membership_list]
    return [(x,getattr(x, method_id)()) for x in membership_list]

  def _getDefaultCategoryMembership(self, category, spec=(), filter=None,
      portal_type=(), base=0, default=None, checked_permission=None, **kw):
    membership = self._getCategoryMembershipList(category,
                spec=spec, filter=filter, portal_type=portal_type, base=base,
                checked_permission=checked_permission, **kw)
    if len(membership) > 0:
      return membership[0]
    else:
      return default

  def _getDefaultAcquiredCategoryMembership(self, category, spec=(),
      filter=None, portal_type=(), base=0, default=None,
      checked_permission=None, **kw):
    membership = self._getAcquiredCategoryMembershipList(category,
                spec=spec, filter=filter, portal_type=portal_type, base=base,
                checked_permission=checked_permission, **kw)
    if len(membership) > 0:
      return membership[0]
    else:
      return default

  security.declareProtected( Permissions.View, 'getDefaultAcquiredCategoryMembership' )
  getDefaultAcquiredCategoryMembership = _getDefaultAcquiredCategoryMembership

  security.declareProtected( Permissions.View, 'getCategoryList' )
  def getCategoryList(self):
    """
      Returns the list of local categories
    """
    return self._getCategoryTool().getCategoryList(self)

  def _getCategoryList(self):
    return self._getCategoryTool()._getCategoryList(self)

  security.declareProtected( Permissions.View, 'getAcquiredCategoryList' )
  def getAcquiredCategoryList(self):
    """
      Returns the list of acquired categories
    """
    return self._getCategoryTool().getAcquiredCategoryList(self)

  def _getAcquiredCategoryList(self):
    return self._getCategoryTool()._getAcquiredCategoryList(self)

  security.declareProtected( Permissions.ModifyPortalContent, 'setCategoryList' )
  def setCategoryList(self, path_list):
    self.portal_categories.setCategoryList(self, path_list)

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

  def _cleanupCategories(self):
    self._getCategoryTool()._cleanupCategories()

  # Category testing
  security.declareProtected( Permissions.View, 'isMemberOf' )
  def isMemberOf(self, category, **kw):
    """
      Tests if an object if member of a given category
    """
    return self._getCategoryTool().isMemberOf(self, category, **kw)

  security.declareProtected( Permissions.View, 'isAcquiredMemberOf' )
  def isAcquiredMemberOf(self, category):
    """
      Tests if an object if member of a given category
    """
    return self._getCategoryTool().isAcquiredMemberOf(self, category)

  # Aliases
  security.declareProtected(Permissions.AccessContentsInformation,
                            'getTitleOrId')
  def getTitleOrId(self):
    """
      Returns the title or the id if the id is empty
    """
    title = self.getTitle()
    if title is not None:
      title = str(title)
      if title == '' or title is None:
        return self.getId()
      else:
        return title
    return self.getId()

  security.declareProtected(Permissions.AccessContentsInformation, 'Title' )
  Title = getTitleOrId # Why ???

  # CMF Compatibility
  security.declareProtected(Permissions.AccessContentsInformation, 'title_or_id' )
  title_or_id = getTitleOrId

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getTitleAndId')
  def getTitleAndId(self):
    """
      Returns the title and the id in parenthesis
    """
    return self.title_and_id()

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getTranslatedShortTitleOrId')
  def getTranslatedShortTitleOrId(self):
    """
    Returns the translated short title or the id if the id is empty
    """
    title = self.getTranslatedShortTitle()
    if title is not None:
      title = str(title)
      if title == '' or title is None:
        return self.getId()
      else:
        return title
    return self.getId()

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getTranslatedTitleOrId')
  def getTranslatedTitleOrId(self):
    """
    Returns the translated title or the id if the id is empty
    """
    title = self.getTranslatedTitle()
    if title is not None:
      title = str(title)
      if title == '' or title is None:
        return self.getId()
      else:
        return title
    return self.getId()

  security.declarePublic('getIdTranslationDict')
  def getIdTranslationDict(self):
    """Returns the mapping which is used to translate IDs.
    """
    property_dict = {
        'Address': dict(default_address='Default Address'),
        'Telephone': dict(default_telephone='Default Telephone',
                          mobile_telephone='Mobile Telephone',),
        'Fax': dict(default_fax='Default Fax'),
        'Email': dict(default_email='Default Email',
                      alternate_email='Alternate Email'),
        'Career': dict(default_career='Default Career'),
        'Payment Condition': dict(default_payment_condition=
                                    'Default Payment Condition'),
        'Annotation Line': dict(
          work_time_annotation_line='Work Time Annotation Line',
          social_insurance_annotation_line='Social Insurance Annotation Line',
          overtime_annotation_line='Overtime Annotation Line'),
        'Image': dict(default_image='Default Image'),
        'Purchase Supply Line': dict(purchase_supply_line=
                                    'Default Purchase Supply Line'),
        'Sale Supply Line': dict(sale_supply_line=
                                 'Default Sale Supply Line'),
        'Accounting Transaction Line': dict(bank='Bank',
                                            payable='Payable',
                                            receivable='Receivable'),
        'Purchase Invoice Transaction Line': dict(expense='Expense',
                                                  payable='Payable',
                                                  refundable_vat='Refundable VAT'),
        'Sale Invoice Transaction Line': dict(income='Income',
                                              collected_vat='Collected VAT',
                                              receivable='Receivable'),
    }
    method = self._getTypeBasedMethod('getIdTranslationDict')
    if method is not None:
      user_dict = method()
      for k in user_dict.keys():
        if property_dict.get(k, None) is not None:
          property_dict[k].update(user_dict[k])
        else:
          property_dict[k] = user_dict[k]
    return property_dict


  security.declareProtected(Permissions.AccessContentsInformation,
                            'getTranslatedId')
  def getTranslatedId(self):
    """Returns the translated ID, if the ID of the current document has a
    special meaning, otherwise returns None.
    """
    global_translation_dict = self.getIdTranslationDict()
    ptype_translation_dict = global_translation_dict.get(
                                  self.portal_type, None)
    if ptype_translation_dict is not None:
      id_ = self.getId()
      if id_ in ptype_translation_dict:
        return str(Message('erp5_ui', ptype_translation_dict[id_]))


  security.declareProtected(Permissions.AccessContentsInformation,
                            'getCompactTitle')
  def getCompactTitle(self):
    """
    Returns the first non-null value from the following:
    - "getCompactTitle" type based method
    - short title
    - reference
    - title
    - id
    """
    method = self._getTypeBasedMethod('getCompactTitle')
    if method is not None:
      r = method()
      if r: return r
    if self.hasShortTitle():
      r = self.getShortTitle()
      if r: return r
    if self.getProperty('reference'):
      r = self.getProperty('reference') 
      if r: return r
    r = self._baseGetTitle() # No need to test existence since all Base instances have this method
    if r: return r      # Also useful whenever title is calculated
    return self.getId()

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getCompactTranslatedTitle')
  def getCompactTranslatedTitle(self):
    """
    Returns the first non-null value from the following:
    - "getCompactTranslatedTitle" type based method
    - "getCompactTitle" type based method
    - translated short title
    - short title
    - reference
    - translated title
    - title
    - id
    """
    method = self._getTypeBasedMethod('getCompactTranslatedTitle')
    if method is not None:
      r = method()
      if r: return r
    method = self._getTypeBasedMethod('getCompactTitle')
    if method is not None:
      r = method()
      if r: return r
    if self.hasShortTitle():
      r = self.getTranslatedShortTitle()
      if r: return r
      r = self.getShortTitle()
      if r: return r
    if self.getProperty('reference'):
      r = self.getReference()
      if r: return r
    r = self._baseGetTranslatedTitle() # No need to test existence since all Base instances have this method
    if r: return r                # Also useful whenever title is calculated
    return self.getId()
  
  # This method allows to sort objects in list is a more reasonable way
  security.declareProtected(Permissions.AccessContentsInformation, 'getIntId')
  def getIntId(self):
    try:
      id_string = self.getId()
      return int(id_string)
    except (ValueError, TypeError):
      try:
        return int(id_string, 16)
      except (ValueError, TypeError):
        return None

  # Default views - the default security in CMFCore
  # is View - however, security was not defined on
  # __call__ -  to be consistent, between view and
  # __call__ we have to define permission here to View
  security.declareProtected(Permissions.View, '__call__')

  security.declareProtected(Permissions.View, 'list')
  def list(self, reset=0):
    """
    Returns the default list even if folder_contents is overridden.
    """
    list_action = _getViewFor(self, view='list')
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

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getTranslatedPortalType')
  def getTranslatedPortalType(self):
    """
      This returns the translated portal_type
    """
    portal_type = self.portal_type
    localizer = getToolByName(self, 'Localizer')
    return localizer.erp5_ui.gettext(portal_type).encode('utf8')

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
  def _checkConsistency(self, fixit=0):
    """
    Check the constitency of objects.

    Private method.
    """
    return []

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

    For example we can check if every Organisation has at least one Address.

    This method looks the constraints defined inside the propertySheets then
    check each of them

    """
    error_list = self._checkConsistency(fixit = fixit)
    # We are looking inside all instances in constraints, then we check
    # the consistency for all of them

    for constraint_instance in self.constraints:
      if fixit:
        error_list += constraint_instance.fixConsistency(self)
      else:
        error_list += constraint_instance.checkConsistency(self)

    if fixit and len(error_list) > 0:
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
      klass = self.__class__
      try:
        context = klass(self.getId())
      except TypeError:
        # If __init__ does not take the id argument, the class is probably
        # a tool, and the id is predifined and immutable.
        context = klass()
      context.__dict__.update(self.__dict__)
      # Copy REQUEST properties to self
      if REQUEST is not None:
        # Avoid copying a SESSION object, because it is newly created
        # implicitly when not present, thus it may induce conflict errors.
        # As ERP5 does not use Zope sessions, it is better to skip SESSION.
        for k in REQUEST.keys():
          if k != 'SESSION':
            setattr(context, k, REQUEST[k])
      # Define local properties
      if kw is not None: context.__dict__.update(kw)
      # Make it a temp content
      temp_object = TempBase(self.getId())
      for k in ('isIndexable', 'reindexObject', 'recursiveReindexObject', 'activate', 'setUid', ):
        setattr(context, k, getattr(temp_object, k))
      # Return result
      return context.__of__(self.aq_parent)
    else:
      return context.asContext(REQUEST=REQUEST, **kw)

  security.declarePublic('isTempObject')
  def isTempObject(self):
    """Return true if self is an instance of a temporary document class.
    """
    return getattr(self.__class__, 'isTempDocument', 0)

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

  security.declarePublic('immediateReindexObject')
  def immediateReindexObject(self, *args, **kw):
    """
      Reindexes an object - also useful for testing
    """
    root_indexable = int(getattr(self.getPortalObject(),'isIndexable',1))
    if self.isIndexable and root_indexable:
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
    self._reindexObject(*args, **kw)

  def _reindexObject(self, activate_kw=None, **kw):
    # When the activity supports group methods, portal_catalog/catalogObjectList is called instead of
    # immediateReindexObject.
    # Do not check if root is indexable, it is done into catalogObjectList,
    # so we will save time
    if self.isIndexable:
      if activate_kw is None:
        activate_kw = {}

      reindex_kw = self.getDefaultReindexParameterDict()
      if reindex_kw is not None:
        reindex_activate_kw = reindex_kw.pop('activate_kw', None)
        if reindex_activate_kw is not None:
          reindex_activate_kw = reindex_activate_kw.copy()
          if activate_kw is not None:
            # activate_kw parameter takes precedence
            reindex_activate_kw.update(activate_kw)
          activate_kw = reindex_activate_kw
        kw.update(reindex_kw)
      
      group_id_list  = []
      if kw.get("group_id", "") not in ('', None):
        group_id_list.append(kw.get("group_id", ""))
      if kw.get("sql_catalog_id", "") not in ('', None):
        group_id_list.append(kw.get("sql_catalog_id", ""))
      group_id = ' '.join(group_id_list)

      self.activate(group_method_id='portal_catalog/catalogObjectList', 
                    alternate_method_id='alternateReindexObject',
                    group_id=group_id,
                    serialization_tag=self.getRootDocumentPath(),
                    **activate_kw).immediateReindexObject(**kw)

  security.declarePublic('recursiveReindexObject')
  recursiveReindexObject = reindexObject

  def getRootDocumentPath(self):
    # Return the path of its root document, or itself if no root document.
    self_path_list = self.getPhysicalPath()
    portal_depth = len(self.getPortalObject().getPhysicalPath())
    return '/'.join(self_path_list[:portal_depth+2])

  security.declareProtected( Permissions.AccessContentsInformation, 'getIndexableChildValueList' )
  def getIndexableChildValueList(self):
    """
      Get indexable childen recursively.
    """
    if self.isIndexable:
      return [self]
    return []

  security.declareProtected(Permissions.ModifyPortalContent, 'reindexObjectSecurity')
  def reindexObjectSecurity(self, *args, **kw):
    """
        Reindex security-related indexes on the object
        (and its descendants).
    """
    # In ERP5, simply reindex all objects.
    #LOG('reindexObjectSecurity', 0, 'self = %r, self.getPath() = %r' % (self, self.getPath()))
    self.reindexObject(*args, **kw)

  security.declareProtected( Permissions.AccessContentsInformation, 'asXML' )
  def asXML(self, root=None):
    """
        Generate an xml text corresponding to the content of this object
    """
    return Base_asXML(self, root=root)

  # Optimized Menu System
  security.declarePublic('allowedContentTypes')
  def allowedContentTypes( self ):
    """
      List portal_types which can be added in this folder / object.
    """
    return []

  security.declarePublic('getVisibleAllowedContentTypeList')
  def getVisibleAllowedContentTypeList(self):
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

  # Hash method
  def __hash__(self):
    return hash(self.getUid())

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

  # Type Casting
  def _getTypeBasedMethod(self, method_id, fallback_script_id=None,
                                script_id=None,**kw):
    """
      Looks up for a zodb script wich ends with what is given as method_id
      and starts with the name of the portal type or meta type.

      For example, method_id can be "asPredicate" and we will on a sale
      packing list line:
      SalePackingListLine_asPredicate
      DeliveryLine_asPredicate

      fallback_script_id : the script to use if nothing is found
    """
    def getScriptName(portal_type, method_id):
      from Products.ERP5Type.Base import Base
      class_name_list = [base_class.__name__ for base_class in self.__class__.mro() if issubclass(base_class, Base)]
      script_name_end = '_%s' % method_id
      for script_name_begin in [portal_type, self.getMetaType()] + class_name_list:
        name = ''.join([script_name_begin.replace(' ',''), script_name_end])
        script = getattr(self, name, None)
        if script is not None:
          return name

    # script_id should not be used any more, keep compatibility
    if script_id is not None:
      LOG('ERP5Type/Base.getTypeBaseMethod',0,
           'DEPRECATED script_id parameter is used')
      fallback_script_id=script_id

    # use a transactional variable to cache results within the same
    # transaction
    portal_type = self.getPortalType()
    tv = getTransactionalVariable(self)
    type_base_cache = tv.setdefault(
        'Base.type_based_cache', {})

    cache_key = (portal_type, method_id)
    try:
      name = type_base_cache[cache_key]
    except KeyError:
      name = getScriptName(portal_type, method_id)
      type_base_cache[cache_key] = name

    if name is not None:
      return getattr(self, name)
    if fallback_script_id is not None:
      return getattr(self, fallback_script_id)

  # Predicate handling
  security.declareProtected(Permissions.AccessContentsInformation, 'asPredicate')
  def asPredicate(self, script_id=None):
    """
      This method tries to convert the current Document into a predicate
      looking up methods named Class_asPredictae, MetaType_asPredicate, PortalType_asPredicate
    """
    script = self._getTypeBasedMethod('asPredicate', script_id=script_id)
    if script is not None:
      return script()
    return None

  def _getAcquireLocalRoles(self):
    """This method returns the value of acquire_local_roles of the object's
    portal_type.
      - True means local roles are acquired, which is the standard behavior of
      Zope objects.
      - False means that the role acquisition chain is cut.

    The code to support this is on the user class, see
    ERP5Security.ERP5UserFactory.ERP5User
    """
    def cached_getAcquireLocalRoles(portal_type):
      ti = self._getTypesTool().getTypeInfo(self)
      return getattr(ti, 'acquire_local_roles', True)

    cached_getAcquireLocalRoles = CachingMethod(cached_getAcquireLocalRoles,
                                                id='Base__getAcquireLocalRoles',
                                                cache_factory='erp5_content_short')
    return cached_getAcquireLocalRoles(portal_type=self.getPortalType())

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

  security.declareProtected(Permissions.ManagePortal, 'manage_setLocalPermissions')
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
      if isinstance(local_permission_list, str):
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

  def _temp_activate(self, *args, **kw):
    return self

  def _temp_setUid(self, value):
    self.uid = value # Required for Listbox so that no casting happens when we use TempBase to create new objects

  def _temp_getUid(self):
    try:
      return getattr(aq_base(self), 'uid')
    except AttributeError:
      value = self.getId()
      self.setUid(value)
      return value

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

  security.declarePublic('log')
  def log(self, description, content='', level=INFO):
    """Put a log message """
    warnings.warn("The usage of Base.log is deprecated.\n"
                  "Please use Products.ERP5Type.Log.log instead.",
                  DeprecationWarning)
    unrestrictedLog(description, content = content, level = level)

  # Dublin Core Emulation for CMF interoperatibility
  # CMF Dublin Core Compatibility
  def Subject(self):
    return self.getSubjectList()

  def Description(self):
    return self.getDescription('')

  def Contributors(self):
    return self.getContributorList('')

  def EffectiveDate(self):
    return self.getEffectiveDate('None')

  def ExpirationDate(self):
    return self.getExpirationDate('None')

  def Contributors(self):
    return self.getContributorList()

  def Format(self):
    return self.getFormat('')

  def Language(self):
    return self.getLanguage('')

  def Rights(self):
    return self.getRight('')

  # Creation and modification date support through workflow
  security.declareProtected(Permissions.AccessContentsInformation, 'getCreationDate')
  def getCreationDate(self):
    """
      Returns the creation date of the document based on workflow information
    """
    # Check if edit_workflow defined
    portal_workflow = getToolByName(self, 'portal_workflow')
    wf = portal_workflow.getWorkflowById('edit_workflow')
    wf_list = list(portal_workflow.getWorkflowsFor(self))
    if wf is not None: wf_list = [wf] + wf_list
    for wf in wf_list:
      try:
        history = wf.getInfoFor(self, 'history', None)
      except KeyError:
        history = None
      if history is not None:
        if len(history):
          # Then get the first line of edit_workflow
          return history[0].get('time', None)
    if getattr(aq_base(self), 'CreationDate', None) is not None:
      return asDate(self.CreationDate())
    return None

  security.declareProtected(Permissions.AccessContentsInformation, 'getModificationDate')
  def getModificationDate(self):
    """
      Returns the modification date of the document based on workflow information

      NOTE: this method is not generic enough. Suggestion: define a modification_date
      variable on the workflow which is an alias to time.
    """
    # Check if edit_workflow defined
    portal_workflow = getToolByName(self, 'portal_workflow')
    wf = portal_workflow.getWorkflowById('edit_workflow')
    wf_list = list(portal_workflow.getWorkflowsFor(self))
    if wf is not None:
      wf_list = [wf] + wf_list
    max_date = None
    for wf in wf_list:
      try:
        history = wf.getInfoFor(self, 'history', None)
      except KeyError:
        history = None
      if history is not None and len(history):
        date = history[-1].get('time', None)
        # Then get the last line of edit_workflow
        if date > max_date:
          max_date = date
    return max_date

  # Layout management
  security.declareProtected(Permissions.AccessContentsInformation, 'getApplicableLayout')
  def getApplicableLayout(self):
    """
      The applicable layout of a standard document in the content layout.

      However, if we are displaying a Web Section as its default document,
      we should use the container layout.
    """
    try:
      # Default documents should be displayed in the layout of the container
      if self.REQUEST.get('is_web_section_default_document', None):
        return self.REQUEST.get('current_web_section').getContainerLayout()
      # ERP5 Modules should be displayed as containers
      # XXX - this shows that what is probably needed is a more sophisticated
      # mapping system between contents and layouts.
      if self.getParentValue().meta_type == 'ERP5 Site':
        return self.getContainerLayout()
      return self.getContentLayout() or self.getContainerLayout()
    except AttributeError:
      return None

  security.declarePublic('isWebMode')
  def isWebMode(self):
    if self.getApplicableLayout() is None:
      return False
    if getattr(self.REQUEST, 'ignore_layout', 0):
      return False
    if getattr(self.REQUEST, 'editable_mode', 0):
      return False
    return True

  security.declareProtected(Permissions.ChangeLocalRoles,
                            'updateLocalRolesOnSecurityGroups')
  def updateLocalRolesOnSecurityGroups(self, **kw):
    """Assign Local Roles to Groups on self, based on Portal Type Role
    Definitions and "ERP5 Role Definition" objects contained inside self.
    """
    self._getTypesTool().getTypeInfo(self) \
    .updateLocalRolesOnDocument(self, **kw)

  security.declareProtected(Permissions.ModifyPortalContent,
                            'assignRoleToSecurityGroup')
  def assignRoleToSecurityGroup(self, **kw):
    """DEPRECATED. This is basically the same as
    `updateLocalRolesOnSecurityGroups`, but with a different permission.
    """
    warnings.warn('assignRoleToSecurityGroup is a deprecated alias to '
                  'updateLocalRolesOnSecurityGroups. Please note that the '
                  'permission changed to "Change Local Roles".',
                  DeprecationWarning)
    self.updateLocalRolesOnSecurityGroups(**kw)

  security.declareProtected(Permissions.ManagePortal,
                            'updateRoleMappingsFor')
  def updateRoleMappingsFor(self, wf_id, **kw):
    """
    Update security policy according to workflow settings given by wf_id
      
    There's no check that the document is actually chained to the workflow,
    it's caller responsability to perform this check.
    """
    workflow = self.portal_workflow.getWorkflowById(wf_id)
    if workflow is not None:
      changed = workflow.updateRoleMappingsFor(self)
      if changed:
        self.reindexObjectSecurity(activate_kw={'priority':4})

  # Template Management
  security.declareProtected(Permissions.View, 'getDocumentTemplateList')
  def getDocumentTemplateList(self) :
    """
      Returns an empty list of allowed templates
      (this is not a folder)
    """
    return []

  security.declareProtected(Permissions.ModifyPortalContent,'makeTemplate')
  def makeTemplate(self):
    """
      Make document behave as a template.
      A template is no longer indexable

      TODO:
         - make template read only, acquired local roles, etc.
         - stronger security model
         - prevent from changing templates or invoking workflows
    """
    parent = self.getParentValue()
    if parent.getPortalType() != "Preference" and not parent.isTemplate:
      raise ValueError, "Template documents can not be created outside Preferences"
    # Make sure this object is not in the catalog
    catalog = getToolByName(self, 'portal_catalog', None)
    if catalog is not None:
       catalog.unindexObject(self, uid=self.getUid())
    self.isIndexable = 0
    self.isTemplate = 1
    # XXX reset security here

  security.declareProtected(Permissions.ModifyPortalContent,'makeTemplateInstance')
  def makeTemplateInstance(self):
    """
      Make document behave as standard document (indexable)
    """
    if self.getParentValue().getPortalType() == "Preference":
      raise ValueError, "Template instances can not be created within Preferences"
    # We remove attributes from the instance
    # We do this rather than self.isIndexable = 0 because we want to
    # go back to previous situation (class based definition)
    if self.__dict__.has_key('isIndexable'): delattr(self, 'isIndexable')
    if self.__dict__.has_key('isTemplate'): delattr(self, 'isTemplate')

    # Add to catalog
    self.reindexObject()

  # ZODB Transaction Management
  security.declarePublic('serialize')
  def serialize(self):
    """Make the transaction accessing to this object atomic
    """
    self.id = self.id

  # Helpers
  def getQuantityPrecisionFromResource(self, resource):
    """
      Provides a quick access to precision without accessing the resource
      value in ZODB. Here resource is the relative_url of the resource, such as
      the result of self.getResource().
    """
    def cached_getQuantityPrecisionFromResource(resource):
      if resource:
        resource_value = self.portal_categories.resolveCategory(resource)
        if resource_value is not None:
          return resource_value.getQuantityPrecision()
      return 0

    cached_getQuantityPrecisionFromResource = CachingMethod(
                                    cached_getQuantityPrecisionFromResource,
                                    id='Base_getQuantityPrecisionFromResource',
                                    cache_factory='erp5_content_short')

    return cached_getQuantityPrecisionFromResource(resource)


  # Documentation Helpers
  security.declareProtected( Permissions.ManagePortal, 'asDocumentationHelper' )
  def asDocumentationHelper(self, item_id=None, REQUEST=None):
    """
      Fills and return a DocHelper object from context.
      Overload this in any object the has to fill the DocHelper in its own way.

      item_id : If specified, the documented item will be
                getattr(self, item_title) if it exists, otherwise None will
                be returned.

      TODO:
       - Check that filtering is correct : display only and every things
         defined on the class itself.
       - Add a list of all accessible things in the documented item context
         (heritated methods & attributes) in a light way that still allows to
         link directly to the corresponding documentation.
       - Rewrite accessor generation system so that it can generate accessor
         names when given a property/category.

       KEEPMEs:
         There are pieces of code in this function that can have interesting
         results, but who are also very verbose. They are disabled (commented
         out) by default, but they should be kept.
         Explanation of the interest :
         The accessors are gathered from 2 sources : the ones defined on the
         PortalType, and systematically generated names, and tested for
         presence on the documented item.
         There are 4 cases then :
         -Accessor whose name was generated exists both on the PortalType and
          on the documented item. That's normal.
         -Accessor whose name was generated exists neither on the PortalType
          nor on the documented item. That's normal, but could mean that the
          accessor name generator isn't optimal.
         -Accessor whose name was generated is found on the object but not on
          the PortalType. This is a problem.
         -Accessors gathered from PortalType aren't all found by guessing
          systematically the names. That means that the accessor name
          generation is not perfect and requires improvement.

         nb: the accessors are gathered from 2 sources, the first is somehow
         accidental when searching for workflow methods defined on the
         PortalType, and are browsed a second time to be able to group them
         by property or category.
    """
    # New implementation of DocumentationHelper (ongoing work)
    if 0:
      from DocumentationHelper import PortalTypeInstanceDocumentationHelper
      helper = PortalTypeInstanceDocumentationHelper(self.getRelativeUrl()).__of__(self)
      if REQUEST is not None:
        return helper.view()
      return helper

    if item_id is None:
      documented_item = self
      item_id = documented_item.getTitle()
    elif getattr(self, item_id, None) is not None:
      documented_item = getattr(self, item_id)
    else:
      return None

    # The documented object is an instance (or not) of this class.
    item_class = getattr(documented_item, '__bases__', None) is None \
                 and documented_item.__class__ \
                 or documented_item

    static_method_list = []    # Class methods
    static_property_list = []  # Class attributes
    dynamic_method_list = []   # Workflow methods
    dynamic_property_list = [] # Document properties
    dynamic_category_list = [] # Categories
    dynamic_accessor_list = [] # Accessors
    found_accessors = {}       # Accessor names : filled by PortalType-level
                               # scan, and used in PropertySheet-level scan.
    dochelper = newTempDocumentationHelper(self.getParentValue(), self.getId(),
                  title=item_id, type=item_class.__name__,
                  description=inspect.getdoc(documented_item),
                )
    dochelper.setInheritanceList([x.__name__ for x in item_class.__bases__])
    try:
      dochelper.setSourcePath(inspect.getsourcefile(item_class))
    except (IOError, TypeError):
      pass
    # dochelper.setSecurity() # (maybe) TODO: Add class instance security gthering.

    # Class-level method & properties
    # We exclude some properites about interface definition because they
    # need specific handling
    excluded_property_set = set(['__provides__'])
    for k, v in item_class.__dict__.items():
      if k in excluded_property_set:
        continue
      subdochelper = newTempDocumentationHelper(dochelper, k,
                  title=k, description=inspect.getdoc(v),
                  security=repr(getattr(documented_item, '%s__roles__' % (k,),None)))
      try:
        subdochelper.setType(v.__class__.__name__)
      except AttributeError:
        pass
      try:
        subdochelper.setSourcePath(inspect.getsourcefile(v))
      except (IOError, TypeError), err:
        pass
      try:
        subdochelper.setSourceCode(inspect.getsource(v))
      except (IOError, TypeError), err:
        pass
      try:
        subdochelper.setArgumentList(inspect.getargspec(v))
      except (IOError, TypeError), err:
        pass
      if subdochelper.getType() in ('function',): # This is a method
        static_method_list.append(subdochelper)
      elif subdochelper.getType() in ('int', 'float', 'long', 'str', 'tuple', 'dict', 'list') \
           and not subdochelper.getTitle().startswith('__'): # This is a property
        subdochelper.setContent(pformat(v))
        static_property_list.append(subdochelper)
      # FIXME: Is there any other interesting type ?

    # PortalType-level methods
    # XXX: accessing portal_type directly because accessors are not generated on instances
    if getattr(documented_item, 'portal_type', None) is not None:
      aq_key = documented_item._aq_key()
      for k, v in Base.aq_portal_type[aq_key].__dict__.items():
        if callable(v) and not (k.startswith('_base') or k.startswith('_category')):
          subdochelper = newTempDocumentationHelper(dochelper, k,
                    title=k, description=inspect.getdoc(v),
                    security=repr(getattr(documented_item, '%s__roles__' % (k,),None)))
          try:
            my_type = v.__class__.__name__
            subdochelper.setType(my_type)
          except AttributeError:
            pass
          if 'Setter' not in my_type and \
             'Getter' not in my_type and \
             'Tester' not in my_type: # Accessors are handled separatelly.
            dynamic_method_list.append(subdochelper)
# KEEPME: usefull to track the differences between accessors defined on
# PortalType and the one detected on the documented item.
#          else:
#            found_accessors[k] = v

    def generatePropertyAccessorNameList(property):
      """
        Generates the possible accessor names for given property.

        FIXME: Should not exist here, but as accessor generation system.
      """
      from Products.ERP5Type.Utils import UpperCase
      res=[]
      cased_id = UpperCase(property['id'])
      for hidden in ('', '_'):
        for getset in ('get', 'set', 'has'): # 'is',
          for default in ('', 'Default', 'Translated'):
            for value in ('', 'Value', 'TranslationDomain'):
              for multivalued in ('', 'List', 'Set'):
                res.append('%s%s%s%s%s%s' % (hidden, getset, default, cased_id, value, multivalued))
      if property.has_key('acquired_property_id') and \
         property['type'] == 'content':
        for aq_property_id in property['acquired_property_id']:
          cased_id = UpperCase('%s_%s' % (property['id'], aq_property_id))
          for hidden in ('', '_'):
            for getset in ('get', 'set'):
              for default in ('', 'Default'):
                for multivalued in ('', 'List'):
                  res.append('%s%s%s%s%s' % (hidden, getset, default, cased_id, multivalued))
      return res

    def generateCategoryAccessorNameList(category):
      """
        Generates the possible accessor names for given category.

        FIXME: Should not exist here, but as accessor generation system.
      """
      from Products.ERP5Type.Utils import UpperCase
      cased_id=UpperCase(category)
      res=['%s%sIds' % (cased_id[0].lower(), cased_id[1:]),
           '%s%sValues' % (cased_id[0].lower(), cased_id[1:])]
      for hidden in ('', '_'):
        for default in ('', 'Default'):
          for multivalued in ('', 'List', 'Set'):
            for attribute in ('', 'TranslatedTitle', 'Uid', 'LogicalPath', 'Id', 'TitleOrId', 'Reference', 'Title'):
              res.append('%sget%s%s%s%s' % (hidden, default, cased_id, attribute, multivalued))
            for attribute in ('', 'Value', 'Uid'):
              res.append('%sset%s%s%s%s' % (hidden, default, cased_id, attribute, multivalued))
      return res

    def accessorAsDocumentationHelper(accessor):
      """
        Generates a documentation helper about a given accessor.
      """
      accessor_dochelper = newTempDocumentationHelper(subdochelper, accessor_name,
                                                      title=accessor_name,
                                                      description=inspect.getdoc(accessor))
      try:
        accessor_dochelper.setSourcePath(inspect.getsourcefile(accessor))
      except (IOError, TypeError), err:
        pass
      try:
        accessor_dochelper.setSourceCode(inspect.getsource(accessor))
      except (IOError, TypeError), err:
        pass
# KEEPME: usefull to track the differences between accessors defined on
# PortalType and the one detected on the documented item.
#      if found_accessors.has_key(accessor_name):
#        del(found_accessors[accessor_name])
#      else:
#        LOG('asDocumentationHelper', 0,
#            'Found but not in the accessor list : %s of type %s' % \
#            (accessor_name, accessor.__class__.__name__))
      return accessor_dochelper

    # PropertySheet-level properties & categories
    # Also handles accessors.
    seen_properties=[]
    seen_categories=[]
    if getattr(documented_item, 'property_sheets', None) is not None:
      for property_sheet in documented_item.property_sheets:
        if getattr(property_sheet, '_properties', None) is not None:
          for property in property_sheet._properties:
            if property in seen_properties:
              continue
            seen_properties.append(property)
            subdochelper = newTempDocumentationHelper(dochelper, k,
                      title=property['id'], description=property['description'],
                      type=property['type'], security=property['mode'],
                      content=pformat(documented_item.getProperty(property['id'])))
            subdochelper_dynamic_accessor_list = []
            for accessor_name in generatePropertyAccessorNameList(property):
              accessor = getattr(item_class, accessor_name, getattr(documented_item, accessor_name, None))
              # First get it on the class, and if not on the instance, thereby among dynamic accessors.
              if accessor is not None:
                subdochelper_dynamic_accessor_list.append(accessorAsDocumentationHelper(accessor))
            subdochelper_dynamic_accessor_list.sort()
            subdochelper.setDynamicAccessorList(subdochelper_dynamic_accessor_list)
            dynamic_accessor_list.append(subdochelper)
            if getattr(documented_item, property['id'], None) is not None:
              dynamic_property_list.append(subdochelper)
        
        def visitCategory(category):
          if category in seen_categories:
            return
          seen_categories.append(category)
          subdochelper = newTempDocumentationHelper(dochelper, category, title=category,
                    content=pformat(documented_item.getCategoryMembershipList(category)))
          subdochelper_dynamic_accessor_list = []
          for accessor_name in generateCategoryAccessorNameList(category):
            accessor = getattr(item_class, accessor_name, getattr(documented_item, accessor_name, None))
            # First get it on the class, and if not on the instance, thereby among dynamic accessors.
            if accessor is not None:
              subdochelper_dynamic_accessor_list.append(accessorAsDocumentationHelper(accessor))
          subdochelper_dynamic_accessor_list.sort()
          subdochelper.setDynamicAccessorList(subdochelper_dynamic_accessor_list)
          dynamic_accessor_list.append(subdochelper)
          dynamic_category_list.append(subdochelper)

        category_list = getattr(property_sheet, '_categories', [])
        # some categories are defined by expressions, so we have to do 2
        # passes, a first one to treat regular category list and collect
        # categories defined by expression, a second one to treat thoses
        # new categories from expressions.
        expression_category_list = []
        for category in category_list:
          if isinstance(category, Expression):
            econtext = createExpressionContext(self)
            expression_category_list.extend(category(econtext))
            continue
          visitCategory(category)
        
        for category in expression_category_list:
          visitCategory(category)

# KEEPME: usefull to track the differences between accessors defined on
# PortalType and the one detected on the documented item.
#    LOG('asDocumentationHelper', 0, found_accessors)
    static_method_list.sort()
    dochelper.setStaticMethodList(static_method_list)
    static_property_list.sort()
    dochelper.setStaticPropertyList(static_property_list)
    dynamic_method_list.sort()
    dochelper.setDynamicMethodList(dynamic_method_list)
    dynamic_accessor_list.sort()
    dochelper.setDynamicAccessorList(dynamic_accessor_list)
    dynamic_category_list.sort()
    dochelper.setDynamicCategoryList(dynamic_category_list)
    dynamic_property_list.sort()
    dochelper.setDynamicPropertyList(dynamic_property_list)
    return dochelper


  security.declareProtected(Permissions.ModifyPortalContent, 'setDefaultReindexParameters' )
  def setDefaultReindexParameters(self, **kw):
    # This method sets the default keyword parameters to reindex. This is useful
    # when you need to specify special parameters implicitly (e.g. to reindexObject).
    tv = getTransactionalVariable(self)
    key = ('default_reindex_parameter', id(aq_base(self)))
    tv[key] = kw

  security.declareProtected(Permissions.View, 'getDefaultReindexParameterDict' )
  def getDefaultReindexParameterDict(self, inherit_placeless=True):
    # This method returns default reindex parameters to self.
    # The result can be either a dict object or None.
    tv = getTransactionalVariable(self)
    if inherit_placeless:
      placeless = tv.get(('default_reindex_parameter', ))
      if placeless is not None:
        placeless = placeless.copy()
    else:
      placeless = None
    local = tv.get(('default_reindex_parameter', id(aq_base(self))))
    if local is None:
      result = placeless
    else:
      if placeless is None:
        result = local.copy()
      else:
        # local defaults takes precedence over placeless defaults.
        result = {}
        result.update(placeless)
        result.update(local)
    return result

  security.declareProtected(Permissions.View, 'isItem' )
  def isItem(self):
    return self.portal_type in self.getPortalItemTypeList()

InitializeClass(Base)

class TempBase(Base):
  """
    If we need Base services (categories, edit, etc) in temporary objects
    we shoud used TempBase
  """
  isIndexable = 0
  isTempDocument = 1

  # Declarative security
  security = ClassSecurityInfo()

  def reindexObject(self, *args, **kw):
    pass

  def recursiveReindexObject(self, *args, **kw):
    pass

  def activate(self, *args, **kw):
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
    """
      Returns the title of this document
    """
    return getattr(aq_base(self), 'title', None)

  security.declarePublic('setProperty')

  security.declarePublic('edit')


def newTempDocumentationHelper(folder, id, REQUEST=None, **kw):
  o = TempDocumentationHelper(id)
  o = o.__of__(folder)
  if kw is not None:
    o._edit(force_update=1, **kw)
  return o


class DocumentationHelper(Base):
  """
    Contains information about a documentable item.
    Documentable item can be any python type, instanciated or not.
  """

  meta_type = "ERP5 Documentation Helper"
  portal_type = "Documentation Helper"

  property_sheets = ( PropertySheet.Base
                    , PropertySheet.DublinCore
                    , PropertySheet.DocumentationHelper
                    , )
  
  def _funcname_cmp_prepare(self, funcname):
    for pos in range(len(funcname)):
      if funcname[pos] != '_':
        break
    return '%s%s' % (funcname[pos:], funcname[:pos])

  def __cmp__(self, documentationhelper):
    if not isinstance(documentationhelper, DocumentationHelper):
      return -1
    my_title = self._funcname_cmp_prepare(self.getTitle())
    his_title = self._funcname_cmp_prepare(documentationhelper.getTitle())
    if my_title < his_title:
      return -1
    if my_title > his_title:
      return 1
    return 0
  

class TempDocumentationHelper(DocumentationHelper, TempBase):
  """Temporary version of Documentation Helper.

  Actually we only use temporary instances of DocumentationHelper, but
  as _aq_dynamic initialize methods on the base class for temp objects, it's
  required that all temp objects have a corresponding "real" class as
  klass.__bases__[0]
  """
  # inheritence fixes
  reindexObject = TempBase.reindexObject
  recursiveReindexObject = TempBase.recursiveReindexObject


