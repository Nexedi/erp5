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
import thread, threading

from BTrees.OOBTree import OOBTree
from Products.ERP5Type.Globals import InitializeClass, DTMLFile
from AccessControl import ClassSecurityInfo
from AccessControl.Permission import pname, Permission
from AccessControl.PermissionRole import rolesForPermissionOn
from AccessControl.SecurityManagement import getSecurityManager
from AccessControl.ZopeGuards import guarded_getattr
from Acquisition import aq_base, aq_inner, aq_acquire, aq_chain
from DateTime import DateTime
import OFS.History
from OFS.SimpleItem import SimpleItem
from OFS.PropertyManager import PropertyManager
from persistent import Persistent
from persistent.TimeStamp import TimeStamp
from zExceptions import NotFound, Unauthorized

from ZopePatch import ERP5PropertyManager

from Products.CMFCore.PortalContent import PortalContent
from Products.CMFCore.Expression import Expression
from Products.CMFCore.utils import getToolByName, _checkConditionalGET, _setCacheHeaders, _ViewEmulator
from Products.CMFCore.WorkflowCore import ObjectDeleted, ObjectMoved
from Products.CMFCore.CMFCatalogAware import CMFCatalogAware

from Products.DCWorkflow.Transitions import TRIGGER_WORKFLOW_METHOD, TRIGGER_USER_ACTION

from Products.ERP5Type import _dtmldir
from Products.ERP5Type import PropertySheet
from Products.ERP5Type import interfaces
from Products.ERP5Type import Permissions
from Products.ERP5Type.patches.CMFCoreSkinnable import SKINDATA, skinResolve
from Products.ERP5Type.Utils import UpperCase
from Products.ERP5Type.Utils import convertToUpperCase, convertToMixedCase
from Products.ERP5Type.Utils import createExpressionContext, simple_decorator
from Products.ERP5Type.Accessor.Accessor import Accessor
from Products.ERP5Type.Accessor.Constant import PropertyGetter as ConstantGetter
from Products.ERP5Type.Accessor.TypeDefinition import list_types
from Products.ERP5Type.Accessor import Base as BaseAccessor
from Products.ERP5Type.mixin.property_translatable import PropertyTranslatableBuiltInDictMixIn
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
from Products.ERP5Type.ConsistencyMessage import ConsistencyMessage
from Products.ERP5Type.UnrestrictedMethod import UnrestrictedMethod, super_user
from Products.ERP5Type.mixin.json_representable import JSONRepresentableMixin

from zope.interface import classImplementsOnly, implementedBy

import sys, re

from cStringIO import StringIO
from socket import gethostname, gethostbyaddr
import random

import inspect
from pprint import pformat

import zope.interface

from ZODB.POSException import ConflictError
from zLOG import LOG, INFO, ERROR, WARNING

_MARKER = []

class PersistentContainer(Persistent):
    """
    Hold a value, making it persistent independently from its container, and
    allowing in-place modification (useful for immutable).
    Does not do any magic, so code using this is well aware of what is the
    container and what is its content, and does not risk leaking one when
    intending to provide the other.
    """
    __slots__ = ('value', )
    def __init__(self, value):
        self.value = value

    def __getstate__(self):
        return self.value

    def __setstate__(self, state):
        self.value = state

global registered_workflow_method_set
wildcard_interaction_method_id_match = re.compile(r'[[.?*+{(\\]').search
workflow_method_registry = [] # XXX A set() would be better but would require a hash in WorkflowMethod class

def resetRegisteredWorkflowMethod(portal_type=None):
  """
    TODO: unwrap workflow methos which were standard methods initially
  """
  for method in workflow_method_registry:
    method.reset(portal_type=portal_type)

  del workflow_method_registry[:]

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
    try:
      wf = getattr(instance.getPortalObject(), 'portal_workflow')
    except AttributeError:
      # XXX instance is unwrapped(no acquisition)
      # XXX I must think that what is a correct behavior.(Yusei)
      return self.__dict__['_m'](instance, *args, **kw)

    # Build a list of transitions which may need to be invoked
    instance_path = instance.getPhysicalPath()
    portal_type = instance.portal_type
    transactional_variable = getTransactionalVariable()
    invoke_once_dict = self._invoke_once.get(portal_type, {})
    valid_invoke_once_item_list = []
    # Only keep those transitions which were never invoked
    once_transition_dict = {}
    for wf_id, transition_list in invoke_once_dict.iteritems():
      valid_transition_list = []
      for transition_id in transition_list:
        once_transition_key = ('Products.ERP5Type.Base.WorkflowMethod.__call__',
                                wf_id, transition_id, instance_path)
        once_transition_dict[(wf_id, transition_id)] = once_transition_key
        if once_transition_key not in transactional_variable:
          valid_transition_list.append(transition_id)
      if valid_transition_list:
        valid_invoke_once_item_list.append((wf_id, valid_transition_list))
    candidate_transition_item_list = valid_invoke_once_item_list + \
                           self._invoke_always.get(portal_type, {}).items()

    #LOG('candidate_transition_item_list %s' % self.__name__, 0, str(candidate_transition_item_list))

    # Try to return immediately if there are no transition to invoke
    if not candidate_transition_item_list:
      return self.__dict__['_m'](instance, *args, **kw)

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
          once_transition_key = once_transition_dict.get((wf_id, transition_id))
          if once_transition_key:
            # a run-once transition, prevent it from running again in
            # the same transaction
            transactional_variable[once_transition_key] = 1
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
    result = self.__dict__['_m'](instance, *args, **kw)

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

  # Interactions should not be disabled during normal operation. Only in very
  # rare and specific cases like data migration. That's why it is implemented
  # with temporary monkey-patching, instead of slowing down __call__ with yet
  # another condition.

  _do_interaction = __call__
  _no_interaction_lock = threading.Lock()
  _no_interaction_log = None
  _no_interaction_thread_id = None

  def _no_interaction(self, *args, **kw):
    if WorkflowMethod._no_interaction_thread_id != thread.get_ident():
      return self._do_interaction(*args, **kw)
    log = "skip interactions for %r" % args[0]
    if WorkflowMethod._no_interaction_log != log:
      WorkflowMethod._no_interaction_log = log
      LOG("WorkflowMethod", INFO, log)
    return self.__dict__['_m'](*args, **kw)

  @staticmethod
  @simple_decorator
  def disable(func):
    def wrapper(*args, **kw):
      thread_id = thread.get_ident()
      if WorkflowMethod._no_interaction_thread_id == thread_id:
        return func(*args, **kw)
      WorkflowMethod._no_interaction_lock.acquire()
      try:
        WorkflowMethod._no_interaction_thread_id = thread_id
        WorkflowMethod.__call__ = WorkflowMethod.__dict__['_no_interaction']
        return func(*args, **kw)
      finally:
        WorkflowMethod.__call__ = WorkflowMethod.__dict__['_do_interaction']
        WorkflowMethod._no_interaction_thread_id = None
        WorkflowMethod._no_interaction_lock.release()
    return wrapper

  @staticmethod
  def disabled():
    return WorkflowMethod._no_interaction_lock.locked()

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
  warnings.warn("_aq_reset is deprecated in favor of "\
                "portal_types.resetDynamicDocumentsOnceAtTransactionBoundary, "\
                "calling this method affects greatly performances",
                DeprecationWarning, stacklevel=2)

  # Callers expect to re-generates accessors right now, so call
  # resetDynamicDocuments to maintain backward-compatibility
  from Products.ERP5.ERP5Site import getSite
  getSite().portal_types.resetDynamicDocuments()

class PropertyHolder(object):
  isRADContent = 1
  WORKFLOW_METHOD_MARKER = ('Base._doNothing',)
  RESERVED_PROPERTY_SET = {'_constraints', '_properties', '_categories',
                           '__implements__', 'property_sheets',
                           '__ac_permissions__', '_erp5_properties'}

  def __init__(self, name='PropertyHolder'):
    self.__name__ = name
    self.security = ClassSecurityInfo() # We create a new security info object
    self.workflow_method_registry = {}

    self._categories = []
    self._properties = []
    self._constraints = []
    self.constraints = []

  def _getPropertyHolderItemList(self):
    return [x for x in self.__dict__.items() if x[0] not in
        PropertyHolder.RESERVED_PROPERTY_SET]

  def registerWorkflowMethod(self, id, wf_id, tr_id, once_per_transaction=0):
    portal_type = self.portal_type

    workflow_method = getattr(self, id, None)
    if workflow_method is None:
      # XXX: We should pass 'tr_id' as second parameter.
      workflow_method = WorkflowMethod(Base._doNothing)
      setattr(self, id, workflow_method)
    if once_per_transaction:
      workflow_method.registerTransitionOncePerTransaction(portal_type,
                                                           wf_id,
                                                           tr_id)
    else:
      workflow_method.registerTransitionAlways(portal_type,
                                               wf_id,
                                               tr_id)

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
    accessor_method_item_list_append = accessor_method_item_list.append
    for x, y in self._getPropertyHolderItemList():
      if isinstance(y, tuple):
        if y is PropertyHolder.WORKFLOW_METHOD_MARKER or x == '__ac_permissions__':
          continue
        if len(y) == 0:
          continue
        if not issubclass(y[0], Accessor):
          continue
      elif not isinstance(y, Accessor):
        continue
      accessor_method_item_list_append((x, y))
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
    return [x for x in self._getPropertyHolderItemList() if isinstance(x[1], WorkflowMethod)
        or (isinstance(x[1], types.TupleType)
            and x[1] is PropertyHolder.WORKFLOW_METHOD_MARKER)]

  def getWorkflowMethodIdList(self):
    """
    Return the list of workflow method IDs
    """
    return [x[0] for x in self.getWorkflowMethodItemList()]

  def _getClassDict(self, klass, inherited=1, local=1):
    """
    Return a dict for every property of a class
    """
    result = {}
    if inherited:
      for parent in reversed(klass.mro()):
        result.update(parent.__dict__)
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
      local=local) if callable(x[1])]

  def getClassMethodIdList(self, klass, inherited=1, local=1):
    """
    Return the list of class method IDs
    """
    return [x[0] for x in self.getClassMethodItemList(klass,
      inherited=inherited, local=local)]

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
    return [x[0] for x in self.getClassPropertyItemList(klass,
      inherited=inherited, local=local)]

def getClassPropertyList(klass):
  ps_list = getattr(klass, 'property_sheets', ())
  ps_list = tuple(ps_list)
  for super_klass in klass.__bases__:
    if getattr(super_klass, 'isRADContent', 0):
      ps_list = ps_list + tuple([p for p in getClassPropertyList(super_klass)
        if p not in ps_list])
  return ps_list

from Products.ERP5Type.Accessor import WorkflowHistory as WorkflowHistoryAccessor
def initializePortalTypeDynamicWorkflowMethods(ptype_klass, portal_workflow):
  """We should now make sure workflow methods are defined
  and also make sure simulation state is defined."""
  # aq_inner is required to prevent extra name lookups from happening
  # infinitely. For instance, if a workflow is missing, and the acquisition
  # wrapper contains an object with _aq_dynamic defined, the workflow id
  # is looked up with _aq_dynamic, thus causes infinite recursions.

  portal_workflow = aq_inner(portal_workflow)
  portal_type = ptype_klass.__name__

  dc_workflow_dict = {}
  interaction_workflow_dict = {}
  for wf in portal_workflow.getWorkflowsFor(portal_type):
    wf_id = wf.id
    wf_type = wf.__class__.__name__
    if wf_type == "DCWorkflowDefinition":
      # Create state var accessor
      # and generate methods that support the translation of workflow states
      state_var = wf.variables.getStateVar()
      for method_id, getter in (
          ('get%s' % UpperCase(state_var), WorkflowState.Getter),
          ('get%sTitle' % UpperCase(state_var), WorkflowState.TitleGetter),
          ('getTranslated%s' % UpperCase(state_var),
                                     WorkflowState.TranslatedGetter),
          ('getTranslated%sTitle' % UpperCase(state_var),
                                     WorkflowState.TranslatedTitleGetter),
          ('serialize%s' % UpperCase(state_var), WorkflowState.SerializeGetter),
          ):
        if not hasattr(ptype_klass, method_id):
          method = getter(method_id, wf_id)
          # Attach to portal_type
          ptype_klass.registerAccessor(method,
                                       Permissions.AccessContentsInformation)

      storage = dc_workflow_dict
      transitions = wf.transitions

      for transition in transitions.objectValues():
        transition_id = transition.getId()
        list_method_id = 'get%sTransitionDateList' % UpperCase(transition_id)
        if not hasattr(ptype_klass, list_method_id):
          method = WorkflowHistoryAccessor.ListGetter(list_method_id, wf_id, transition_id, 'time')
          ptype_klass.registerAccessor(method,
                                       Permissions.AccessContentsInformation)

        method_id = 'get%sTransitionDate' % UpperCase(transition_id)
        if not hasattr(ptype_klass, method_id):
          method = WorkflowHistoryAccessor.Getter(method_id, list_method_id)
          ptype_klass.registerAccessor(method,
                                       Permissions.AccessContentsInformation)

    elif wf_type == "InteractionWorkflowDefinition":
      storage = interaction_workflow_dict
      transitions = wf.interactions
    else:
      continue

    # extract Trigger transitions from workflow definitions for later
    transition_id_set = set(transitions.objectIds())
    trigger_dict = {}
    for tr_id in transition_id_set:
      tdef = transitions[tr_id]
      if tdef.trigger_type == TRIGGER_WORKFLOW_METHOD:
        trigger_dict[tr_id] = tdef

    storage[wf_id] = (transition_id_set, trigger_dict)

  for wf_id, v in dc_workflow_dict.iteritems():
    transition_id_set, trigger_dict = v
    for tr_id, tdef in trigger_dict.iteritems():
      method_id = convertToMixedCase(tr_id)
      try:
        method = getattr(ptype_klass, method_id)
      except AttributeError:
        ptype_klass.security.declareProtected(Permissions.AccessContentsInformation,
                                              method_id)
        ptype_klass.registerWorkflowMethod(method_id, wf_id, tr_id)
        continue

      # Wrap method
      if not callable(method):
        LOG('initializePortalTypeDynamicWorkflowMethods', 100,
            'WARNING! Can not initialize %s on %s' % \
              (method_id, portal_type))
        continue

      if not isinstance(method, WorkflowMethod):
        method = WorkflowMethod(method)
        setattr(ptype_klass, method_id, method)
      else:
        # We must be sure that we
        # are going to register class defined
        # workflow methods to the appropriate transition
        transition_id = method.getTransitionId()
        if transition_id in transition_id_set:
          method.registerTransitionAlways(portal_type, wf_id, transition_id)
      method.registerTransitionAlways(portal_type, wf_id, tr_id)

  if not interaction_workflow_dict:
    return

  # all methods in mro of portal type class: that contains all
  # workflow methods and accessors you could possibly ever need
  class_method_id_list = ptype_klass.getClassMethodIdList(ptype_klass)

  interaction_queue = []
  # XXX This part is (more or less...) a copy and paste
  for wf_id, v in interaction_workflow_dict.iteritems():
    transition_id_set, trigger_dict = v
    for tr_id, tdef in trigger_dict.iteritems():
      # Check portal type filter
      if (tdef.portal_type_filter is not None and \
          portal_type not in tdef.portal_type_filter):
        continue

      # Check portal type group filter
      if tdef.portal_type_group_filter is not None:
        getPortalGroupedTypeSet = portal_workflow.getPortalObject()._getPortalGroupedTypeSet
        if not any(portal_type in getPortalGroupedTypeSet(portal_type_group) for
                   portal_type_group in tdef.portal_type_group_filter):
          continue

      for imethod_id in tdef.method_id:
        if wildcard_interaction_method_id_match(imethod_id):
          # Interactions workflows can use regexp based wildcard methods
          # XXX What happens if exception ?
          method_id_matcher = re.compile(imethod_id).match

          # queue transitions using regexps for later examination
          interaction_queue.append((wf_id,
                                    tr_id,
                                    transition_id_set,
                                    tdef.once_per_transaction,
                                    method_id_matcher))

          # XXX - class stuff is missing here
          method_id_list = filter(method_id_matcher, class_method_id_list)
        else:
          # Single method
          # XXX What if the method does not exist ?
          #     It's not consistent with regexp based filters.
          method_id_list = [imethod_id]
        for method_id in method_id_list:
          method = getattr(ptype_klass, method_id, _MARKER)
          if method is _MARKER:
            # set a default security, if this method is not already
            # protected.
            if method_id not in ptype_klass.security.names:
              ptype_klass.security.declareProtected(
                  Permissions.AccessContentsInformation, method_id)
            ptype_klass.registerWorkflowMethod(method_id, wf_id, tr_id,
                                               tdef.once_per_transaction)
            continue

          # Wrap method
          if not callable(method) or method_id in (
              # To prevent infinite recursion in case of mistake in a worflow,
              # methods that are always used by WorkflowMethod.__call__
              # must be excluded.
              'getPortalObject', 'getPhysicalPath', 'getId'):
            LOG('initializePortalTypeDynamicWorkflowMethods', 100,
                'WARNING! Can not initialize %s on %s' % \
                  (method_id, portal_type))
            continue
          if not isinstance(method, WorkflowMethod):
            method = WorkflowMethod(method)
            setattr(ptype_klass, method_id, method)
          else:
            # We must be sure that we
            # are going to register class defined
            # workflow methods to the appropriate transition
            transition_id = method.getTransitionId()
            if transition_id in transition_id_set:
              method.registerTransitionAlways(portal_type, wf_id, transition_id)
          if tdef.once_per_transaction:
            method.registerTransitionOncePerTransaction(portal_type, wf_id, tr_id)
          else:
            method.registerTransitionAlways(portal_type, wf_id, tr_id)

  if not interaction_queue:
    return

  # the only methods that could have appeared since last check are
  # workflow methods
  # TODO we could just queue the ids of methods that are attached to the
  # portal type class in the previous loop, to improve performance
  new_method_set = set(ptype_klass.getWorkflowMethodIdList())
  added_method_set = new_method_set.difference(class_method_id_list)
  # We need to run this part twice in order to handle interactions of interactions
  # ex. an interaction workflow creates a workflow method which matches
  # the regexp of another interaction workflow
  for wf_id, tr_id, transition_id_set, once, method_id_matcher in interaction_queue:
    for method_id in filter(method_id_matcher, added_method_set):
      # method must already exist and be a workflow method
      method = getattr(ptype_klass, method_id)
      transition_id = method.getTransitionId()
      if transition_id in transition_id_set:
        method.registerTransitionAlways(portal_type, wf_id, transition_id)
      if once:
        method.registerTransitionOncePerTransaction(portal_type, wf_id, tr_id)
      else:
        method.registerTransitionAlways(portal_type, wf_id, tr_id)

class Base( CopyContainer,
            PortalContent,
            ActiveObject,
            OFS.History.Historical,
            ERP5PropertyManager,
            PropertyTranslatableBuiltInDictMixIn,
            JSONRepresentableMixin,
            ):
  """
    This is the base class for all ERP5 Zope objects.
    It defines object attributes which are necessary to implement
    relations and data synchronisation

    id  --  the standard object id
    rid --  the standard object id in the master ODB the object was
        subsribed from
    uid --  a global object id which is unique
    sid --  the id of the subscribtion/syncrhonisation object which
        this object was generated from

    sync_status -- The status of this document in the synchronization
             process (NONE, SENT, ACKNOWLEDGED, SYNCHRONIZED)
             could work as a workflow but CPU expensive

  """
  meta_type = 'ERP5 Base Object'
  portal_type = 'Base Object'
  #_local_properties = () # no need since getattr
  isRADContent = 1    #
  isPortalContent = ConstantGetter('isPortalContent', value=True)
  isCapacity = ConstantGetter('isCapacity', value=False)
  isCategory = ConstantGetter('isCategory', value=False)
  isBaseCategory = ConstantGetter('isBaseCategory', value=False)
  isInventoryMovement = ConstantGetter('isInventoryMovement', value=False)
  isDelivery = ConstantGetter('isDelivery', value=False)
  isInventory = ConstantGetter('isInventory', value=False)
  # If set to 0, reindexing will not happen (useful for optimization)
  isIndexable = ConstantGetter('isIndexable', value=True)
  isPredicate = ConstantGetter('isPredicate', value=False)
  isTemplate = ConstantGetter('isTemplate', value=False)
  isDocument = ConstantGetter('isDocument', value=False)
  isTempDocument = ConstantGetter('isTempDocument', value=False)

  # Dynamic method acquisition system (code generation)
  aq_method_generated = set()
  aq_method_generating = []
  aq_portal_type = {}
  aq_related_generated = 0
  # Only generateIdList may look at this property. Anything else is unsafe.
  _id_generator_state = None

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

  # Place for all is... method
  security.declareProtected(Permissions.AccessContentsInformation, 'isMovement')
  def isMovement(self):
    return 0

  security.declareProtected( Permissions.ModifyPortalContent, 'setTitle' )
  def setTitle(self, value):
    """ sets the title. (and then reindexObject)"""
    self._setTitle(value)
    self.reindexObject()

  security.declarePublic('provides')
  def provides(cls, interface_name):
    """
    Check if the current class provides a particular interface from ERP5Type's
    interfaces registry
    """
    interface = getattr(interfaces, interface_name, None)
    if interface is not None:
      return interface.implementedBy(cls)
    return False
  provides = classmethod(CachingMethod(provides, 'Base.provides',
                                       cache_factory='erp5_ui_long'))

  def _aq_key(self):
    return (self.portal_type, self.__class__)

  def _propertyMap(self, local_properties=False):
    """ Method overload - properties are now defined on the ptype """
    property_list = []
    # Get all the accessor holders for this portal type
    if not local_properties:
      property_list += self.__class__.getAccessorHolderPropertyList()

    property_list += getattr(self, '_local_properties', [])
    return tuple(property_list)

  def manage_historyCompare(self, rev1, rev2, REQUEST,
                            historyComparisonResults=''):
    return Base.inheritedAttribute('manage_historyCompare')(
          self, rev1, rev2, REQUEST,
          historyComparisonResults=OFS.History.html_diff(
              pformat(rev1.__dict__),
              pformat(rev2.__dict__)))

  def _aq_dynamic(self, id):
    # ahah! disabled, thanks to portal type classes
    return None

  # Constructor
  def __init__(self, id, uid=None, rid=None, sid=None, **kw):
    self.id = id
    if uid is not None :
      self.uid = uid # Else it will be generated when we need it
    self.sid = sid

  # XXX This is necessary to override getId which is also defined in SimpleItem.
  security.declareProtected( Permissions.AccessContentsInformation, 'getId' )
  getId = BaseAccessor.Getter('getId', 'id', 'string')

  # Debug
  security.declareProtected(Permissions.AccessContentsInformation,
                            'getOid')
  def getOid(self):
    """
      Return ODB oid
    """
    return self._p_oid

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getOidRepr')
  def getOidRepr(self):
    """
      Return ODB oid, in an 'human' readable form.
    """
    from ZODB.utils import oid_repr
    return oid_repr(self._p_oid)

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getSerial')
  def getSerial(self):
    """Return ODB Serial."""
    return self._p_serial

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getHistorySerial')
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
        copy_value=0, mask_value=0, accessor_id=None, depends=None,
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

      accessor_id   --    the id of the accessor to call on the related filtered objects

      depends       --    a list of parameters to propagate in the look up process

      acquisition_object_id -- List of object Ids where look up properties
                               before looking up on acquired objects
      The purpose of copy_value / mask_value is to solve issues
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
    tv = getTransactionalVariable()
    if isinstance(portal_type, list):
      portal_type = tuple(portal_type)
    elif portal_type is None:
      portal_type = ()
    acquisition_key = ('_getDefaultAcquiredProperty', self.getPath(), key,
                       acquisition_object_id, base_category, portal_type,
                       copy_value, mask_value, accessor_id, depends,
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
      local_value = value
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
      #super_list = self.getValueList(base_category, portal_type=portal_type) # We only do a single jump
      super_list = self.getAcquiredValueList(base_category, portal_type=portal_type,
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
      elif local_value not in null_value:
        # Nothing has been found by looking up
        # through acquisition documents, fallback by returning
        # at least local_value
        return local_value
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
     base_category, portal_type=None, copy_value=0, mask_value=0, append_value=0,
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
    tv = getTransactionalVariable()
    if isinstance(portal_type, list):
      portal_type = tuple(portal_type)
    elif portal_type is None:
      portal_type = ()
    acquisition_key = ('_getAcquiredPropertyList', self.getPath(), key, base_category,
                       portal_type, copy_value, mask_value, accessor_id,
                       depends, storage_id, alt_accessor_id,
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
      super_list += self.getAcquiredValueList(
        base_category,
        portal_type=portal_type,
        checked_permission=checked_permission,
        ) # Full acquisition
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
    """
    __traceback_info__ = (key,)
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
    # Try a mono valued accessor if it is available
    # and return it as a list
    if accessor_name.endswith('List'):
      mono_valued_accessor_name = accessor_name[:-4]
      method = getattr(self.__class__, mono_valued_accessor_name, None)
      if method is not None:
        # We have a monovalued property
        if d is _MARKER:
          result = method(self, **kw)
        else:
          try:
            result = method(self, d, **kw)
          except TypeError:
            result = method(self, **kw)
        if not isinstance(result, (list, tuple)):
          result = [result]
        return result
    if d is not _MARKER:
      return ERP5PropertyManager.getProperty(self, key, d=d,
                local_properties=True, **kw)
    return ERP5PropertyManager.getProperty(self, key,
                local_properties=True, **kw)

  security.declareProtected( Permissions.AccessContentsInformation, 'getPropertyList' )
  def getPropertyList(self, key, d=_MARKER):
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
    # Try a mono valued setter if it is available
    # and call it
    if accessor_name.endswith('List'):
      mono_valued_accessor_name = accessor_name[:-4]
      mono_valued_public_accessor_name = public_accessor_name[:-4]
      method = None
      if hasattr(self, mono_valued_accessor_name):
        method = getattr(self, mono_valued_accessor_name)
      elif hasattr(self, mono_valued_public_accessor_name):
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
    if ERP5PropertyManager.hasProperty(self,key, local_properties=True):
      ERP5PropertyManager._updateProperty(self, key, value,
                          local_properties=True)
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

  security.declareProtected(Permissions.AccessContentsInformation,
                            'hasProperty')
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
    method = getattr(self, 'has' + UpperCase(key), _MARKER)
    if method is _MARKER:
      # Check in local properties (which obviously were defined at some point)
      return key in self.propertyIds()
    try:
      return method()
    except ConflictError:
      raise
    except:
      return 0

  security.declareProtected(Permissions.AccessContentsInformation,
                            'hasCategory')
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
  security.declareProtected(Permissions.AccessContentsInformation,
                            'ping')
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
    if not kw:
      return
    key_list = kw.keys()
    modified_property_dict = self._v_modified_property_dict = {}
    modified_object_dict = {}

    unordered_key_list = [k for k in key_list if k not in edit_order]
    ordered_key_list = [k for k in edit_order if k in key_list]
    if restricted:
      # retrieve list of accessors which doesn't use default permissions
      restricted_method_set = {method
        for ancestor in self.__class__.mro()
        for permissions in getattr(ancestor, '__ac_permissions__', ())
        if permissions[0] not in ('Access contents information',
                                  'Modify portal content')
        for method in permissions[1]
        if method.startswith('set')}
    else:
      restricted_method_set = ()

    getProperty = self.getProperty
    _setProperty = self._setProperty

    def setChangedPropertyList(key_list):
      not_modified_list = []
      for key in key_list:
        # We only change if the value is different
        # This may be very long...
        if force_update:
          old_value = None
        else:
          try:
            old_value = getProperty(key, evaluate=0)
          except TypeError:
            old_value = getProperty(key)
          if old_value == kw[key]:
            not_modified_list.append(key)
            continue

        # If the keep_existing flag is set to 1,
        # we do not update properties which are defined
        if keep_existing and self.hasProperty(key):
          continue
        # We keep in a thread var the previous values
        # this can be useful for interaction workflow to implement lookups
        # XXX If iteraction workflow script is triggered by edit and calls
        # edit itself, this is useless as the dict will be overwritten
        if restricted:
          accessor_name = 'set' + UpperCase(key)
          if accessor_name in restricted_method_set:
            # will raise Unauthorized when not allowed
            guarded_getattr(self, accessor_name)
        modified_property_dict[key] = old_value
        if key != 'id':
          modified_object_list = _setProperty(key, kw[key])
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
  #     Probably not. Even if it should speed up portal_type initialization and
  #     save some memory because edit_workflow is used in many places, I (jm)
  #     think it's negligible compared to the performance loss on all
  #     classes/types that are not bound to edit_workflow.
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
    result = set()
    for parent_class in self.__class__.mro():
      for property in getattr(parent_class, '_properties', []):
        if property['type'] == 'content':
          result.add(property['id'])
    return list(result)

  security.declareProtected( Permissions.View, 'getStandardPropertyIdList' )
  def getStandardPropertyIdList(self):
    """
      Return standard properties of the current instance.
      Unlike getPropertyIdList, properties are not converted or rewritten here.
    """
    result = set()
    for parent_class in self.__class__.mro():
      for property in getattr(parent_class, '_properties', []):
        if property['type'] != 'content':
          result.add(property['id'])
    return list(result)

  # Catalog Related
  security.declareProtected( Permissions.AccessContentsInformation, 'getObject' )
  def getObject(self, relative_url = None, REQUEST=None):
    """
      Returns self - useful for ListBox when we do not know
      if the getObject is called on a brain object or on the actual object
    """
    return self

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getDocumentInstance')
  def getDocumentInstance(self):
    """
      Returns self
      Returns instance if category through document_instance relation
    """
    return self

  security.declareProtected(Permissions.ManagePortal, 'getMountedObject')
  def getMountedObject(self):
      """
      If self is a mount-point, return the mounted object in its own storage
      """
      from Products.ZODBMountPoint.MountedObject import getMountPoint
      mount_point = getMountPoint(self)
      if mount_point is not None:
        connection = self._p_jar
        assert mount_point._getMountedConnection(connection) is connection
        return mount_point._traverseToMountedRoot(connection.root(), None)

  security.declareProtected( Permissions.AccessContentsInformation,
                             'getParentUid' )
  def getParentUid(self):
    """
      Returns the UID of the parent of the current object. Used
      for the implementation of the ZSQLCatalog based listing
      of objects.
    """
    return self.aq_inner.aq_parent.getUid()

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
      self.uid = self.getPortalObject().portal_catalog.newUid()
      uid = getattr(aq_base(self), 'uid', None)
      if uid is None:
        raise DeferredCatalogError('Could neither access uid nor generate it', self)
    return uid

  security.declareProtected(Permissions.AccessContentsInformation, 'getLogicalPath')
  def getLogicalPath(self, REQUEST=None, **kw) :
    """
      Returns the absolute path of an object, using titles when available
    """
    pathlist = self.getPhysicalPath()
    objectlist = [self.getPhysicalRoot()]
    for element in pathlist[1:] :
      objectlist.append(objectlist[-1][element])
    return '/' + '/'.join(object.getTitle() for object in objectlist[1:])

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
    return '/' + '/'.join(object.getCompactTitle() for object in objectlist[1:])

  security.declareProtected(Permissions.AccessContentsInformation, 'getUrl')
  def getUrl(self, REQUEST=None):
    """
      Returns the absolute path of an object
    """
    return '/'.join(self.getPhysicalPath())

  # Old name - for compatibility
  security.declareProtected(Permissions.AccessContentsInformation, 'getPath')
  getPath = getUrl

  security.declareProtected(Permissions.AccessContentsInformation, 'getRelativeUrl')
  def getRelativeUrl(self):
    """
      Returns the url of an object relative to the portal site.
    """
    return self.getPortalObject().portal_url.getRelativeUrl(self)

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getAbsoluteUrl')
  def getAbsoluteUrl(self):
    """
      Returns the absolute url of an object.
    """
    return self.absolute_url()

  security.declarePublic('getPortalObject')
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
    d = copy(self.__dict__)
    klass = self.__class__
    d['__class__'] = '%s.%s' % (klass.__module__, klass.__name__)
    return d

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
    getRelativeUrl = self.getPortalObject().portal_url.getRelativeUrl
        
    def cleanupCategory(path):
      # prevent duplicating base categories and storing "portal_categories/"
      for start_string in ("portal_categories/", "%s/" % id):
        if path.startswith(start_string):
          path = path[len(start_string):]
      return path

    if target is None :
      path = target
    elif isinstance(target, str):
      ## We have been provided a string
      #path = target
      # is Base in obj.__class__.__mro__ ?
      raise TypeError('Only objects should be passed as values')
    elif isinstance(target, (tuple, list, set, frozenset)):
      # We have been provided a list or tuple
      path_list = []
      for target_item in target:
        if isinstance(target_item, str):
          #path = target_item
          raise TypeError('Only objects should be passed as values')
        else:
          path = getRelativeUrl(target_item)
        path_list.append(cleanupCategory(path))
      path = path_list
    else:
      # We have been provided an object
      path = cleanupCategory(getRelativeUrl(target))

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

  # Unrestricted category value getters

  def _getDefaultValue(self, id, spec=(), filter=None, default=_MARKER, **kw):
    path = self._getDefaultCategoryMembership(id, base=1, spec=spec,
                                              filter=filter, **kw)
    if path:
      return self._getCategoryTool()._resolveCategory(path)
    if default is not _MARKER:
      return default

  def _getValueList(self, id, spec=(), filter=None, default=_MARKER, **kw):
    ref_list = self._getCategoryMembershipList(id, base=1, spec=spec,
                                               filter=filter, **kw)
    if ref_list:
      resolveCategory = self._getCategoryTool()._resolveCategory
      value_list = []
      for path in ref_list:
        value = resolveCategory(path)
        if value is not None:
          value_list.append(value)
      return value_list if value_list or default is _MARKER else default
    return ref_list if default is _MARKER else default

  def _getDefaultAcquiredValue(self, id, spec=(), filter=None, portal_type=(),
                               evaluate=1, checked_permission=None,
                               default=None, **kw):
    path = self._getDefaultAcquiredCategoryMembership(
      id, spec=spec, filter=filter, portal_type=portal_type,
      base=1, checked_permission=checked_permission, **kw)
    if path:
      return self._getCategoryTool()._resolveCategory(path)
    if default is not _MARKER:
      return default

  def _getAcquiredValueList(self, id, spec=(), filter=None, default=_MARKER,
                            **kw):
    ref_list = self._getAcquiredCategoryMembershipList(id, base=1, spec=spec,
                                                       filter=filter, **kw)
    if ref_list:
      resolveCategory = self._getCategoryTool()._resolveCategory
      value_list = []
      for path in ref_list:
        value = resolveCategory(path)
        if value is not None:
          value_list.append(value)
      return value_list if value_list or default is _MARKER else default
    return ref_list if default is _MARKER else default

  # Restricted category value getters

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getDefaultValue')
  def getDefaultValue(self, id, spec=(), filter=None, default=_MARKER, **kw):
    path = self._getDefaultCategoryMembership(id, base=1, spec=spec,
                                              filter=filter, **kw)
    if path:
      return self._getCategoryTool().resolveCategory(path)
    if default is not _MARKER:
      return default

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getValueList')
  def getValueList(self, id, spec=(), filter=None, default=_MARKER, **kw):
    ref_list = self._getCategoryMembershipList(id, base=1, spec=spec,
                                               filter=filter, **kw)
    if ref_list:
      resolveCategory = self._getCategoryTool().resolveCategory
      value_list = []
      for path in ref_list:
        value = resolveCategory(path)
        if value is not None:
          value_list.append(value)
      return value_list if value_list or default is _MARKER else default
    return ref_list if default is _MARKER else default

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getDefaultAcquiredValue')
  def getDefaultAcquiredValue(self, id, spec=(), filter=None, portal_type=(),
                              evaluate=1, checked_permission=None,
                              default=None, **kw):
    path = self._getDefaultAcquiredCategoryMembership(
      id, spec=spec, filter=filter, portal_type=portal_type,
      base=1, checked_permission=checked_permission, **kw)
    if path:
      return self._getCategoryTool().resolveCategory(path)
    if default is not _MARKER:
      return default

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getAcquiredValueList')
  def getAcquiredValueList(self, id, spec=(), filter=None, default=_MARKER,
                            **kw):
    ref_list = self._getAcquiredCategoryMembershipList(id, base=1, spec=spec,
                                                       filter=filter, **kw)
    if ref_list:
      resolveCategory = self._getCategoryTool().resolveCategory
      value_list = []
      for path in ref_list:
        value = resolveCategory(path)
        if value is not None:
          value_list.append(value)
      return value_list if value_list or default is _MARKER else default
    return ref_list if default is _MARKER else default

  ###

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

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getDefaultRelatedValue')
  getDefaultRelatedValue = _getDefaultRelatedValue

  def _getRelatedValueList(self, *args, **kw):
    # backward compatibility to keep strict keyword working
    if 'strict' in kw:
      kw['strict_membership'] = kw.pop('strict')
    return self._getCategoryTool().getRelatedValueList(self, *args, **kw)

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getRelatedValueList')
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

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getValueUidList')
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
    references = map(self.getPortalObject().portal_catalog.getObject,
                     (uids,) if isinstance(uids, (int, long)) else uids)
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
      portal_type=(), base=0, keep_default=1, checked_permission=None,
      default=_MARKER, **kw):
    """
      This returns the list of categories for an object
    """
    r = self._getCategoryTool().getCategoryMembershipList(self, category,
        spec=spec, filter=filter, portal_type=portal_type, base=base,
        keep_default=keep_default, checked_permission=checked_permission, **kw)
    return r if r or default is _MARKER else default

  security.declareProtected( Permissions.AccessContentsInformation, 'getCategoryMembershipList' )
  getCategoryMembershipList = _getCategoryMembershipList

  def _getAcquiredCategoryMembershipList(self, category, spec=(), filter=None,
      portal_type=(), base=0, keep_default=1, checked_permission=None,
      default=_MARKER, **kw):
    """
      Returns the list of acquired categories
    """
    r = self._getCategoryTool().getAcquiredCategoryMembershipList(self,
                             category, spec=spec, filter=filter,
                             portal_type=portal_type, base=base,
                             keep_default=keep_default,
                             checked_permission=checked_permission, **kw )
    return r if r or default is _MARKER else default

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
             checked_permission=None, default=_MARKER):
    if method_id or sort_id not in (None, 'default'):
      raise NotImplementedError
    membership_list = self._getAcquiredCategoryMembershipList(category,
                           spec = spec, filter=filter, portal_type=portal_type, base=base,
                           checked_permission=checked_permission)
    if membership_list or default is _MARKER:
      if sort_id == 'default':
        membership_list.sort()
      return [(x, x) for x in membership_list]
    return [] if default is _MARKER else default

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

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getDefaultAcquiredCategoryMembership')
  getDefaultAcquiredCategoryMembership = _getDefaultAcquiredCategoryMembership

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getCategoryList')
  def getCategoryList(self):
    """
      Returns the list of local categories
    """
    return self._getCategoryTool().getCategoryList(self)

  def _getCategoryList(self):
    return self._getCategoryTool()._getCategoryList(self)

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getAcquiredCategoryList')
  def getAcquiredCategoryList(self):
    """
      Returns the list of acquired categories
    """
    return self._getCategoryTool().getAcquiredCategoryList(self)

  security.declareProtected( Permissions.ModifyPortalContent, 'setCategoryList' )
  def setCategoryList(self, path_list):
    self.portal_categories.setCategoryList(self, path_list)

  def _setCategoryList(self, path_list):
    self.portal_categories._setCategoryList(self, path_list)

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getBaseCategoryList')
  def getBaseCategoryList(self):
    """
      Lists the base_category ids which apply to this instance
    """
    return self._getCategoryTool().getBaseCategoryList(context=self)

  security.declareProtected( Permissions.View, 'getBaseCategoryIds' )
  getBaseCategoryIds = getBaseCategoryList

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getBaseCategoryValueList')
  def getBaseCategoryValueList(self):
    return self._getCategoryTool().getBaseCategoryValues(context=self)

  security.declareProtected( Permissions.View, 'getBaseCategoryValues' )
  getBaseCategoryValues = getBaseCategoryValueList

  # Category testing
  security.declareProtected( Permissions.AccessContentsInformation, 'isMemberOf' )
  def isMemberOf(self, category, **kw):
    """
      Tests if an object if member of a given category
    """
    return self._getCategoryTool().isMemberOf(self, category, **kw)

  security.declareProtected( Permissions.AccessContentsInformation, 'isAcquiredMemberOf' )
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
    Returns the translated title or the id if the title is empty
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
        'Internal Supply Line': dict(internal_supply_line=
                                     'Default Internal Supply Line'),
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
    - title
    - reference
    - id
    """
    method = self._getTypeBasedMethod('getCompactTitle')
    if method is not None:
      r = method()
      if r: return r
    if self.hasShortTitle():
      r = self.getShortTitle()
      if r: return r
    return (getattr(self, '_baseGetTitle', str)() or
            self.getProperty('reference') or
            self.getId())

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getCompactTranslatedTitle')
  def getCompactTranslatedTitle(self):
    """
    Returns the first non-null value from the following:
    - "getCompactTranslatedTitle" type based method
    - "getCompactTitle" type based method
    - translated short title
    - short title
    - translated title
    - title
    - reference
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
    return (# No need to test existence since all Base instances have this method
            # Also useful whenever title is calculated
            self._baseGetTranslatedTitle() or
            self.getProperty('reference') or
            self.getId())

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

  def _renderDefaultView(self, view, **kw):
    ti = self.getTypeInfo()
    if ti is None:
      raise NotFound('Cannot find default %s for %r' % (view, self.getPath()))
    method = ti.getDefaultViewFor(self, view)
    if getattr(aq_base(method), 'isDocTemp', 0):
        return method(self, self.REQUEST, self.REQUEST['RESPONSE'], **kw)
    else:
        return method(**kw)

  security.declareProtected(Permissions.View, 'view')
  def view(self):
    """Returns the default view even if index_html is overridden"""
    result = self._renderDefaultView('view')
    view = _ViewEmulator().__of__(self)
    # If we have a conditional get, set status 304 and return
    # no content
    if _checkConditionalGET(view, extra_context={}):
      return ''
    # call caching policy manager.
    _setCacheHeaders(view, {})
    return result

  # Default views - the default security in CMFCore
  # is View - however, security was not defined on
  # __call__ -  to be consistent, between view and
  # __call__ we have to define permission here to View
  security.declareProtected(Permissions.View, '__call__')
  __call__ = view

  # This special value informs ZPublisher to use __call__. We define it here
  # since Products.CMFCore.PortalContent.PortalContent stopped defining it on
  # CMF 2.x. They use aliases and Zope3 style views now and make pretty sure
  # not to let zpublisher reach this value.
  index_html = None
  # By the Way, Products.ERP5.Document.File and .Image define their own
  # index_html to make sure this value here is not used so that they're
  # downloadable by their naked URL.

  security.declareProtected(Permissions.View, 'list')
  def list(self, reset=0):
    """Returns the default list even if folder_contents is overridden"""
    return self._renderDefaultView('list', reset=reset)

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
    localizer = self.getPortalObject().Localizer
    return localizer.erp5_ui.gettext(self.portal_type).encode('utf8')

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
  def _checkConsistency(self, fixit=False):
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
    return self._checkConsistency(fixit=True)

  security.declareProtected(Permissions.AccessContentsInformation, 'checkConsistency')
  def checkConsistency(self, fixit=False, filter=None, **kw):
    """
    Check the constitency of objects.

    For example we can check if every Organisation has at least one Address.

    This method looks the constraints defined inside the propertySheets then
    check each of them

    Here, we try to check consistency without security, because
    consistency should not depend on the user. But if the user does not
    have enough permission, the detail of the error should be hidden.
    """
    def getUnauthorizedErrorMessage(constraint):
      return ConsistencyMessage(constraint,
                                object_relative_url=self.getRelativeUrl(),
                                message='There is something wrong.')
    error_list = UnrestrictedMethod(self._checkConsistency)(fixit=fixit)
    if len(error_list) > 0:
      try:
        self._checkConsistency()
      except Unauthorized:
        error_list = [getUnauthorizedErrorMessage(self)]

    # We are looking inside all instances in constraints, then we check
    # the consistency for all of them

    for constraint_instance in self._filteredConstraintList(filter):
      if fixit:
        extra_error_list = UnrestrictedMethod(
          constraint_instance.fixConsistency)(self, **kw)
      else:
        extra_error_list = UnrestrictedMethod(
          constraint_instance.checkConsistency)(self, **kw)
      if len(extra_error_list) > 0:
        try:
          if not fixit:
            extra_error_list = constraint_instance.checkConsistency(self, **kw)
          else:
            constraint_instance.checkConsistency(self, **kw)
        except Unauthorized:
          error_list.append(getUnauthorizedErrorMessage(constraint_instance))
        else:
          error_list += extra_error_list

    if fixit and len(error_list) > 0:
      self.reindexObject()

    return error_list

  security.declareProtected(Permissions.ManagePortal, 'fixConsistency')
  def fixConsistency(self, filter=None, **kw):
    """
    Fix the constitency of objects.
    """
    return self.checkConsistency(fixit=True, filter=filter, **kw)

  def _filteredConstraintList(self, filt):
    """
    Returns a list of constraints filtered by filt argument.
    """
    # currently only 'id' and 'reference', 'constraint_type' are supported.
    constraints = self.constraints
    if filt is not None:
      if 'id' in filt:
        id_list = filt.get('id', None)
        if not isinstance(id_list, (list, tuple)):
          id_list = [id_list]
        constraints = filter(lambda x:x.id in id_list, constraints)
      # New ZODB based constraint uses reference for identity
      if 'reference' in filt:
        reference_list = filt.get('reference', None)
        if not isinstance(reference_list, (list, tuple)):
          reference_list = [reference_list]
        constraints = filter(lambda x:x.getProperty('reference') in \
            reference_list, constraints)
      if 'constraint_type' in filt:
        constraint_type_list = filt.get('constraint_type', None)
        if not isinstance(constraint_type_list, (list, tuple)):
          constraint_type_list = [constraint_type_list]
        constraints = filter(lambda x:x.__of__(self).getProperty('constraint_type') in \
                constraint_type_list, constraints)

    return constraints

  # Context related methods
  security.declarePublic('asContext')
  def asContext(self, context=None, REQUEST=None, **kw):
    """
    The purpose of asContext is to allow users overloading easily the properties and categories of
    an existing persistent object. (Use the same data and create a different portal type instance)

    Pay attention, to use asContext to create a temp object is wrong usage.

    ex : joe_person = person_module.bob_person.asContext(first_name='Joe')
    """
    if context is None:
      pt = self._getTypesTool()
      portal_type = self.getPortalType()
      type_info = pt.getTypeInfo(portal_type)
      if type_info is None:
        raise ValueError('No such content type: %s' % portal_type)

      context = type_info.constructInstance(
              container=self.getParentValue(),
              id=self.getId(),
              temp_object=True,
              notify_workflow=False,
              is_indexable=False)

      # Pass all internal data to new instance. Do not copy, but
      # pass the same data. This is on purpose.
      context.__dict__.update(self.__dict__)

      # Copy REQUEST properties to self
      if REQUEST is not None:
        # Avoid copying a SESSION object, because it is newly created
        # implicitly when not present, thus it may induce conflict errors.
        # As ERP5 does not use Zope sessions, it is better to skip SESSION.
        for k in REQUEST.keys():
          if k != 'SESSION':
            setattr(context, k, REQUEST[k])
      # Set the original document
      kw['_original'] = self
      # Define local properties
      context.__dict__.update(kw)
      return context
    else:
      return context.asContext(REQUEST=REQUEST, **kw)

  security.declarePublic('getOriginalDocument')
  def getOriginalDocument(self, context=None, REQUEST=None, **kw):
    """
    This method returns:
    * the original document for an asContext() result document.
    * self for a real document.
    * None for a temporary document.
    """
    if not self.isTempObject():
      return self
    else:
      original = getattr(self, '_original', None)
      if original is not None:
        original = aq_inner(original)
        if original.isTempObject():
          return original.getOriginalDocument()
        else:
          return original
      else:
        return None

  security.declarePublic('isTempObject')
  def isTempObject(self):
    """Return true if self is an instance of a temporary document class.
    """
    isTempDocument = getattr(self.__class__, 'isTempDocument', None)
    if isTempDocument is not None:
      return isTempDocument()
    else:
      return False

  security.declareProtected(Permissions.AccessContentsInformation,
                            'isDeletable')
  def isDeletable(self, check_relation=True):
    """Test if object can be delete"""
    container = self.getParentValue()
    portal = container.getPortalObject()
    return (portal.portal_workflow.isTransitionPossible(self, 'delete')
      if container.portal_type != 'Preference' and
        any(wf_id != 'edit_workflow'
            for wf_id in getattr(aq_base(self), "workflow_history", ()))
      else portal.portal_membership.checkPermission(
        'Delete objects', container)
      ) and not (check_relation and self.getRelationCountForDeletion())

  security.declareProtected(Permissions.AccessContentsInformation,
                            'isDeleted')
  def isDeleted(self):
    """Test if the context is in 'deleted' state"""
    for wf in self.getPortalObject().portal_workflow.getWorkflowsFor(self):
      state = wf._getWorkflowStateOf(self)
      if state is not None and state.getId() == 'deleted':
        return True
    return False

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getRelationCountForDeletion')
  def getRelationCountForDeletion(self):
    """Count number of related objects preventing deletion"""
    portal = self.getPortalObject()
    getRelatedValueList = portal.portal_categories.getRelatedValueList
    ignore_list = [x.getPhysicalPath() for x in (
      portal.portal_simulation,
      portal.portal_trash,
      self)]
    related_list = [(related.getPhysicalPath(), related)
      for o in self.getIndexableChildValueList()
      for related in getRelatedValueList(o)]
    related_list.sort()
    ignored = None
    related_count = 0
    for related_path, related in related_list:
      if ignored is None or related_path[:len(ignored)] != ignored:
        for ignored in ignore_list:
          if related_path[:len(ignored)] == ignored:
            break
        else:
          if related.isDeleted():
            ignored = related_path
          else:
            ignored = None
            related_count += 1
    return related_count

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

  security.declarePrivate('isSubtreeIndexable')
  def isSubtreeIndexable(self):
    """
    Allow a container to preempt indexability of its content, without having
    to set "isIndexable = False" on (at minimum) its immediate children.

    The meaning of calling this method on an instance where
    isAncestryIndexable returns False is undefined.
    """
    return self.isIndexable

  security.declarePrivate('isAncestryIndexable')
  def isAncestryIndexable(self):
    """
    Tells whether this document is indexable, taking into account its entire
    ancestry: a document may only be indexed if its parent is indexable, and
    it's parent's parent, etc until ERP5Site object (inclusive).
    """
    node = self.aq_inner
    portal = aq_base(self.getPortalObject())
    is_indexable = self.isIndexable
    while is_indexable and aq_base(node) is not portal:
      node = node.aq_parent
      is_indexable = node.isSubtreeIndexable()
    return is_indexable

  security.declarePrivate('immediateReindexObject')
  def immediateReindexObject(self, *args, **kw):
    if self.isAncestryIndexable():
      with super_user():
        PortalContent.reindexObject(self, *args, **kw)
  _reindexOnCreation = immediateReindexObject

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
    if self.isAncestryIndexable():
      kw, activate_kw = self._getReindexAndActivateParameterDict(
        kw,
        activate_kw,
      )
      activate_kw['serialization_tag'] = self.getRootDocumentPath()
      self.activate(**activate_kw).immediateReindexObject(**kw)

  def _getReindexAndActivateParameterDict(self, kw, activate_kw):
    # Lowest activate_kw priority: default activate parameter dict
    full_activate_kw = self.getDefaultActivateParameterDict(
      # It is the responsibility of activity spawning to pull placeless
      # activate parameters. Skip them here.
      inherit_placeless=False,
    )
    reindex_kw = self.getDefaultReindexParameterDict()
    if reindex_kw is not None:
      reindex_kw = reindex_kw.copy()
      # Next activate_kw priority: default reindex parameter dict's
      # "activate_kw" entry, if any.
      full_activate_kw.update(reindex_kw.pop('activate_kw', None) or ())
      # kw is not expected to contain an "activate_kw" entry.
      reindex_kw.update(kw)
      kw = reindex_kw
    # And top activate_kw priority: the direct parameter.
    full_activate_kw.update(activate_kw or ())
    full_activate_kw['group_id'] = ' '.join(group_id for group_id in (
        kw.pop("group_id", None),
        kw.get("sql_catalog_id"),
        full_activate_kw.get('group_id'),
      ) if group_id)
    full_activate_kw['group_method_id'] = 'portal_catalog/catalogObjectList'
    full_activate_kw['alternate_method_id'] = 'alternateReindexObject'
    full_activate_kw['activity'] = 'SQLDict'
    return kw, full_activate_kw

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
    if self.isAncestryIndexable():
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

  security.declareProtected(Permissions.AccessContentsInformation,
          'getRedirectParameterDictAfterAdd')
  def getRedirectParameterDictAfterAdd(self, container, **kw):
    """Return a dict of parameters to specify where the user is redirected
    to after a new object is added in the UI."""
    method = self._getTypeBasedMethod('getRedirectParameterDictAfterAdd')
    return method(container, **kw)

  security.declareProtected(Permissions.ModifyPortalContent, 'setGuid')
  def setGuid(self):
    """
    This generate a global and unique id
    It will be defined like this :
     full dns name + portal_name + uid + random
     the guid should be defined only one time for each object
    """
    if self.getGuid() is None:
      guid = ''
      # Set the dns name
      guid += gethostbyaddr(gethostname())[0]
      guid += '_' + self.portal_url.getPortalPath()
      guid += '_' + str(self.uid)
      guid += '_' + str(random.randrange(1,2147483600))
      setattr(self, 'guid', guid)

  security.declareProtected(Permissions.AccessContentsInformation, 'getGuid')
  def getGuid(self):
    """
    Get the global and unique id
    """
    return getattr(aq_base(self), 'guid', None)

  security.declareProtected(Permissions.AccessContentsInformation, 'getTypeBasedMethod')
  def getTypeBasedMethod(self, *args, **kw):
    return self._getTypeBasedMethod(*args, **kw)

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
    # script_id should not be used any more, keep compatibility
    if script_id is not None:
      LOG('ERP5Type/Base.getTypeBaseMethod',0,
           'DEPRECATED script_id parameter is used')
      fallback_script_id=script_id

    # use a transactional variable to cache results within the same
    # transaction
    portal_type = self.getPortalType()
    tv = getTransactionalVariable()
    type_base_cache = tv.setdefault('Base.type_based_cache', {})

    cache_key = (portal_type, method_id)
    try:
      script = type_base_cache[cache_key]
    except KeyError:
      script_name_end = '_' + method_id
      for base_class in self.__class__.mro():
        if issubclass(base_class, Base):
          script_id = base_class.__name__.replace(' ','') + script_name_end
          script = getattr(self, script_id, None)
          if script is not None:
            type_base_cache[cache_key] = aq_inner(script)
            return script
      type_base_cache[cache_key] = None

    if script is not None:
      return script.__of__(self)
    if fallback_script_id is not None:
      return getattr(self, fallback_script_id)

  security.declareProtected(Permissions.AccessContentsInformation, 'skinSuper')
  def skinSuper(self, skin, id):
    if id[:1] != '_' and id[:3] != 'aq_':
      skin_info = SKINDATA.get(thread.get_ident())
      if skin_info is not None:
        portal = self.getPortalObject()
        _, skin_selection_name, _, _ = skin_info
        object = skinResolve(portal, (skin_selection_name, skin), id)
        if object is not None:
          # First wrap at the portal to set the owner of the executing script.
          # This mimics the usual way to get an object from skin folders,
          # and it's required when 'object' is an script with proxy roles.
          return object.__of__(portal).__of__(self)
    raise AttributeError(id)

  security.declareProtected(Permissions.AccessContentsInformation,
                            'get_local_permissions')
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
      """
      Used by the catalog for basic full text indexing.
      """
      searchable_text_list = []
      portal_type = self.portal_types.getTypeInfo(self)
      if portal_type is None:
        # it can be a temp object or a tool (i.e. Activity Tool) for which we have no portal_type definition
        # so use definition of 'Base Type' for searchable methods & properties
        portal_type = self.portal_types.getTypeInfo('Base Type')
      searchable_text_method_id_list = []

      # generated from properties methods and add explicitly defined method_ids as well
      for searchable_text_property_id in portal_type.getSearchableTextPropertyIdList():
        # this "hasProperty" prevents acquisition. But also it prevents retrieving properties
        # of relations (ie: source_section_title). This is not bad, as anyway if the property
        # of the relation changes, the indexed searchableText property will become wrong.
        # Also, we don't want to trigger the indexation of hundreds of documents if the
        # title of a Person changes (which means we don't want an interaction workflow
        # for reindexation of related documents)
        if self.hasProperty(searchable_text_property_id):
          method_id = convertToUpperCase(searchable_text_property_id)
          searchable_text_method_id_list.extend(['get%s' %method_id])

      searchable_text_method_id_list.extend(portal_type.getSearchableTextMethodIdList())
      for method_id in searchable_text_method_id_list:
        # XXX: how to exclude exclude acquisition (not working)
        #if getattr(aq_base(self), method_id, None) is not None:
        #  method = getattr(self, method_id, None)
        # should we do it as ZSQLCatalog should care for calling this method on proper context?
        method = getattr(self, method_id, None)
        if method is not None:
          method_value = method()
          if method_value is not None:
            if isinstance(method_value, (list, tuple)):
              searchable_text_list.extend(method_value)
            else:
              searchable_text_list.append(method_value)
      searchable_text = ' '.join([str(x) for x in searchable_text_list])
      return searchable_text.strip()

  # Compatibility with CMF Catalog / CPS sites
  SearchableText = getSearchableText

  security.declareProtected(Permissions.View, 'newError')
  def newError(self, **kw):
    """
    Create a new Error object
    """
    from Products.ERP5Type.Error import Error
    return Error(**kw)

  security.declarePublic('log')
  def log(self, *args, **kw):
    """Put a log message

    See the warning in Products.ERP5Type.Log.log
    Catchall parameters also make this method not publishable to avoid DoS.
    """
    warnings.warn("The usage of Base.log is deprecated.\n"
                  "Please use Products.ERP5Type.Log.log instead.",
                  DeprecationWarning)
    unrestrictedLog(*args, **kw)

  # Dublin Core Emulation for CMF interoperatibility
  # CMF Dublin Core Compatibility
  def Subject(self):
    return self.getSubjectList()

  def Description(self):
    return self.getDescription('')

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
    portal_workflow = self.getPortalObject().portal_workflow
    wf = portal_workflow.getWorkflowById('edit_workflow')
    wf_list = portal_workflow.getWorkflowsFor(self)
    if wf is not None:
      wf_list = [wf] + wf_list
    for wf in wf_list:
      try:
        history = wf.getInfoFor(self, 'history', None)
      except KeyError:
        history = None
      if history is not None and len(history):
        # Then get the first line of edit_workflow
        return history[0].get('time', None)
    if getattr(aq_base(self), 'CreationDate', None) is not None:
      return asDate(self.CreationDate())
    return None # JPS-XXX - try to find a way to return a creation date instead of None

  security.declareProtected(Permissions.AccessContentsInformation, 'getModificationDate')
  def getModificationDate(self):
    """
      Returns the modification date of the document based on workflow information

      NOTE: this method is not generic enough. Suggestion: define a modification_date
      variable on the workflow which is an alias to time.

      XXX: Should we return the ZODB date if it's after the last history entry ?
    """
    try:
      history_list = aq_base(self).workflow_history
    except AttributeError:
      pass
    else:
      max_date = None
      for history in history_list.itervalues():
        try:
          date = history[-1]['time']
        except (IndexError, KeyError, TypeError):
          continue
        if date > max_date:
          max_date = date
      if max_date:
        # Return a copy of history time, to prevent modification
        return DateTime(max_date)
    if self._p_serial:
      return DateTime(TimeStamp(self._p_serial).timeTime())

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
    """
      return True if we are in web mode
    """
    if self.getApplicableLayout() is None:
      return False
    if getattr(self.REQUEST, 'ignore_layout', 0):
      return False
    return True

  security.declarePublic('isEditableWebMode')
  def isEditableWebMode(self):
    """
      return True if we are in editable mode
    """
    return getattr(self.REQUEST, 'editable_mode', 0)

  security.declarePublic('isEditableMode')
  isEditableMode = isEditableWebMode # for backwards compatability


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
    self.isTemplate = ConstantGetter('isTemplate', value=True)
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
    self._p_changed = 1

  # Helpers
  security.declareProtected(Permissions.AccessContentsInformation,
                            'getQuantityPrecisionFromResource')
  def getQuantityPrecisionFromResource(self, resource, d=2):
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
      return None

    cached_getQuantityPrecisionFromResource = CachingMethod(
                                    cached_getQuantityPrecisionFromResource,
                                    id='Base_getQuantityPrecisionFromResource',
                                    cache_factory='erp5_content_short')

    precision = cached_getQuantityPrecisionFromResource(resource)
    if precision is None:
      precision = d
    return precision

  security.declareProtected(Permissions.ModifyPortalContent, 'setDefaultReindexParameters' )
  def setDefaultReindexParameters(self, **kw):
    warnings.warn('setDefaultReindexParameters is deprecated in favour of '
      'setDefaultReindexParameterDict.', DeprecationWarning)
    self.setDefaultReindexParameterDict(kw)

  security.declareProtected(Permissions.ModifyPortalContent, 'setDefaultReindexParameterDict' )
  def setDefaultReindexParameterDict(self, kw):
    # This method sets the default keyword parameters to reindex. This is useful
    # when you need to specify special parameters implicitly (e.g. to reindexObject).
    tv = getTransactionalVariable()
    key = ('default_reindex_parameter', id(aq_base(self)))
    tv[key] = kw

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getDefaultReindexParameterDict')
  def getDefaultReindexParameterDict(self, inherit_placeless=True):
    # This method returns default reindex parameters to self.
    # The result can be either a dict object or None.
    tv = getTransactionalVariable()
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

  security.declareProtected(Permissions.AccessContentsInformation, 'isItem')
  def isItem(self):
    return self.portal_type in self.getPortalItemTypeList()

  security.declareProtected(Permissions.DeletePortalContent,
                            'migratePortalType')
  def migratePortalType(self, portal_type):
    """
    Recreate document by recomputing inputted parameters with help of
    contribution tool.

    Use an Unrestricted method to edit related relations on other objects.
    """
    if self.getPortalType() == portal_type:
      raise TypeError, 'Can not migrate a document to same portal_type'
    if not portal_type:
      raise TypeError, 'Missing portal_type value'

    # Reingestion requested with portal_type.
    input_kw = {}
    input_kw['portal_type'] = portal_type
    for property_id in self.propertyIds():
      if property_id not in ('portal_type', 'uid', 'id',) \
            and self.hasProperty(property_id):
        input_kw[property_id] = self.getProperty(property_id)
    if getattr(self, 'hasUrlString', None) is not None and self.hasUrlString():
      # try to reingest from url if data and/or filename is missing.
      if not 'data' in input_kw or not 'filename' in input_kw:
        # URL is not stored on document
        # pass required properties for portal_contributions.newContent
        input_kw['url'] = self.asURL()

    # Use meta transition to jump from one state to another
    # without existing transitions.
    from Products.ERP5.InteractionWorkflow import InteractionWorkflowDefinition
    portal = self.getPortalObject()
    workflow_tool = portal.portal_workflow
    worflow_variable_list = []
    for workflow in workflow_tool.getWorkflowsFor(self):
      if not isinstance(workflow, InteractionWorkflowDefinition):
        worflow_variable_list.append(self.getProperty(workflow.state_var))

    # then restart ingestion with new portal_type
    # XXX Contribution Tool accept only document which are containing
    # at least the couple data and filename or one url
    portal_contributions = portal.portal_contributions
    new_document = portal_contributions.newContent(**input_kw)

    # Meta transitions
    for state in worflow_variable_list:
      if workflow_tool._isJumpToStatePossibleFor(new_document, state):
        workflow_tool._jumpToStateFor(new_document, state)

    # Update relations
    UnrestrictedMethod(self.updateRelatedContent)(self.getRelativeUrl(),
                                                  new_document.getRelativeUrl())

    # Delete actual content
    self.getParentValue()._delObject(self.getId())

    return new_document

  def _postCopy(self, container, op=0):
    super(Base, self)._postCopy(container, op=op)
    if op == 0: # copy (not cut)
      # We are the copy of another document (either cloned or copy/pasted),
      # forget id generator state.
      try:
        del self._id_generator_state
      except AttributeError:
        pass

  security.declareProtected(Permissions.AccessContentsInformation, 'generateIdList')
  def generateIdList(self, group, count=1, default=1, onMissing=None, poison=False):
    """
    Manages multiple independent sequences of unique numbers.
    Each sequence guarantees the unicity of each produced value within that
    sequence and for <self> instance, and is monotonously increasing by 1 for
    each generated id.

    group (string):
      Identifies the sequence to use.
    count (int):
      How many identifiers to generate.
    default (int):
      If the sequence for given <group> did not already exist, initialise it at
      this for the first generated value.
    onMissing (callable):
      If provided, called when requested sequence is missing, "default" is
      ignored and the value returned by this function is used instead.
      Allows seamless migration from another id generator *if* that id
      generator is able to "poison the land" (see next option).
    poison (bool):
      If True, return the next id in requested sequence, and permanently break
      that sequence's state, so that no new id may be successfuly generated
      from it. Useful to ensure seamless migration away from this generator,
      without risking a (few) late generation from happening after migration
      code already moved sequence's state elsewhere.
      Once a sequence has been poisoned, attempting to generate a new value
      from it will raise an exception (exception type may vary).
      "count" must be 1, otherwise a ValueError is raised.

    Conflicts & guarantees:
    - If multiple transactions modify the same sequence, ALL BUT ONE get a
      ConflictError. This is by design, to achieve per-sequence unicity.
    - If multiple transactions modify different sequences, NONE will get a
      ConflictError (each sequence state is a separate persistent object).
    - If multiple transactions create new sequences, SOME may get a
      ConflictError. This is a limitation of the chosen data structure.
      It is expected that group creation is a rare event, very unlikely to
      happen concurrently in multiple transactions on the same object.
    """
    if not isinstance(group, basestring):
      raise TypeError('group must be a string')
    if not isinstance(default, (int, long)):
      raise TypeError('default must be an integer')
    if not isinstance(count, (int, long)):
      raise TypeError('count must be an integer')
    if count < 0:
      raise ValueError('count cannot be negative')
    if poison and count != 1:
      raise ValueError('sequence generator poisoning requires count=1')
    if count == 0:
      return []
    id_generator_state = self._id_generator_state
    if id_generator_state is None:
      id_generator_state = self._id_generator_state = OOBTree()
    try:
      next_id = id_generator_state[group].value
    except KeyError:
      if onMissing is not None:
        default = onMissing()
        if not isinstance(default, (int, long)):
          raise TypeError('onMissing must return an integer')
      id_generator_state[group] = PersistentContainer(default)
      next_id = default
    new_next_id = None if poison else next_id + count
    id_generator_state[group].value = new_next_id
    return range(next_id, new_next_id)

InitializeClass(Base)

from Products.CMFCore.interfaces import IContentish
# suppress CMFCore event machinery from trying to reindex us through events
# by removing Products.CMFCore.interfaces.IContentish interface.
# We reindex ourselves in manage_afterAdd thank you very much.
def removeIContentishInterface(cls):
  classImplementsOnly(cls, implementedBy(cls) - IContentish)

removeIContentishInterface(Base)

class TempBase(Base):
  """
    If we need Base services (categories, edit, etc) in temporary objects
    we shoud used TempBase
  """
  isIndexable = ConstantGetter('isIndexable', value=False)
  isTempDocument = ConstantGetter('isTempDocument', value=True)

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
  security.declarePublic('getProperty')

  security.declarePublic('edit')

# Persistence.Persistent is one of the superclasses of TempBase, and on Zope2.8
# its __class_init__ method is InitializeClass. This is not the case on
# Zope2.12 which requires us to call InitializeClass manually, otherwise
# allow_class(TempBase) in ERP5Type/Document/__init__.py will trample our
# ClassSecurityInfo with one that doesn't declare our public methods
InitializeClass(TempBase)
