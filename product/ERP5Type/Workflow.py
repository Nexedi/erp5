# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2002 Nexedi SA and Contributors. All Rights Reserved.
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

from six.moves import map
from App.special_dtml import HTMLFile
from Acquisition import aq_inner
from AccessControl.requestmethod import postonly
from DateTime import DateTime
from Products.DCWorkflow.DCWorkflow import DCWorkflowDefinition
from . import Permissions
from .ConflictFree import DoublyLinkList

# ERP5 workflow factory definitions
_workflow_factories = {}

def addWorkflowFactory(factory, id, title):
    """addWorkflowFactory replacement

    addWorkflowFactory has been removed from CMFCore 2.x.
    DCWorkflow, which now handles this job, consults the GenericSetup tool,
    at runtime, to determine all valid workflows.

    Instead of providing xml files in GenericSetup profiles for our,
    workflows we prepare our own Zope2 style factories for registration
    in the Workflow Tool.
    """
    assert not _workflow_factories.get(id), (
        'Workflow factory with id %r already exists.' % id)

    _workflow_factories[id] = {
      'factory': factory,
      'id': id,
      'title': title,
    }

# Workflow Creation DTML
manage_addWorkflowFormDtml = HTMLFile('dtml/addWorkflow', globals())

def _generateWorkflowConstructors(factory_info):
  """ Generate a "addWorkflow_?" and "addWorkflowForm_?" methods specific for
  each workflow factory. """

  FACTORY_FORM_PREFIX = 'addWorkflowForm_'
  FACTORY_ACTION_PREFIX = 'addWorkflow_'

  workflow_factory_id = factory_info['id']
  workflow_factory_title = factory_info['title']
  # the method names (last url segments)
  constructor_form_name = FACTORY_FORM_PREFIX + workflow_factory_id
  constructor_action_name = FACTORY_ACTION_PREFIX + workflow_factory_id

  # The form
  def manage_addWorkflowForm(dispatcher, REQUEST, RESPONSE):
    """Form to add a type-specific workflow to portal_workflow"""
    return manage_addWorkflowFormDtml(None, dispatcher, REQUEST,
      workflow_factory_title=workflow_factory_title,
      form_action=constructor_action_name)

  # The action of the form
  @postonly
  def manage_addWorkflow(dispatcher, workflow_id, REQUEST=None):
    """Add a type specific workflow with object-id as 'workflow_id'
    """
    # we could have just used the factory from factory_info here, but we use
    # addWorkflowByType to exercise it.
    workflow = addWorkflowByType(dispatcher, workflow_factory_id, workflow_id)
    if REQUEST is not None:
      return REQUEST.response.redirect(dispatcher.DestinationURL() +
                                       "/manage_main")
    return workflow

  # The constructors
  return [
    (constructor_form_name, manage_addWorkflowForm),
    (constructor_action_name, manage_addWorkflow),
  ]

def addWorkflowByType(container, workflow_factory_id, workflow_id):
  """ Add a workflow with name 'workflow_id' from factory identified by
  'workflow_factory_id'
  """
  # This functionality could be inside the generated manage_addWorkflow above,
  # but is placed here to be easily used directly from Python code.
  container._setObject(workflow_id,
    _workflow_factories[workflow_factory_id]['factory'](workflow_id))
  return aq_inner(container.restrictedTraverse(workflow_id))

def registerWorkflowFactory(context, factory_info):
  """ Register a workflow factory as a Zope2 style object factory that is only
  addable to portal_workflow"""
  context.registerClass(
    DCWorkflowDefinition, # this class is only used here for its interfaces
    meta_type=factory_info['title'],
    constructors=_generateWorkflowConstructors(factory_info),
    permission=Permissions.ManagePortal,
    visibility=None,
  )

def registerAllWorkflowFactories(context):
  """register workflow factories during product initialization
  """
  # the loop below will be empty on CMF 1.5, as the original addworkflowFactory
  # from CMF will not populate this WORKFLOW_FACTORIES dictionary.
  for factory_info in _workflow_factories.itervalues():
    registerWorkflowFactory(context, factory_info)

# Add a workflow factory for ERP5 style workflow, because some variables
# are needed for History tab.
def setupERP5Workflow(wf):
  """Sets up an DC Workflow with defaults variables needed by ERP5.
  """
  wf.setProperties(title='ERP5 Default Workflow')
  states = wf.states
  addState = states.addState
  for state_id, state_title in (('draft', 'Draft'),):
    addState(state_id)
    states[state_id].title = state_title
  states.setInitialState('draft')

  variables = wf.variables
  addVariable = variables.addVariable
  for v, property_dict in (
        ('action', {
            'description': 'Transition id',
            'default_expr': 'transition/getId|nothing',
            'for_status': 1,
            'update_always': 1,
          }),
        ('actor', {
            'description': 'Name of the user who performed transition',
            'default_expr': 'user/getIdOrUserName',
            'for_status': 1,
            'update_always': 1,
          }),
        ('comment', {
            'description': 'Comment about transition',
            'default_expr': "python:state_change.kwargs.get('comment', '')",
            'for_status': 1,
            'update_always': 1,
          }),
        ('history', {
            'description': 'Provides access to workflow history',
            'default_expr': 'state_change/getHistory',
          }),
        ('time', {
            'description': 'Transition timestamp',
            'default_expr': 'state_change/getDateTime',
            'for_status': 1,
            'update_always': 1,
          }),
        ('error_message', {
            'description': 'Error message if validation failed',
            'for_status': 1,
            'update_always': 1,
          }),
        ('portal_type', {
            'description': 'Portal type (used as filter for worklists)',
            'for_catalog': 1,
          }),
      ):
    addVariable(v)
    variables[v].setProperties(**property_dict)

  addManagedPermission = wf.addManagedPermission
  for perm in (Permissions.AccessContentsInformation,
               Permissions.View,
               Permissions.AddPortalContent,
               Permissions.ModifyPortalContent,
               Permissions.DeleteObjects):
    addManagedPermission(perm)

  # set by default the state variable to simulation_state.
  # anyway, a default workflow needs to be configured.
  variables.setStateVar('simulation_state')

def createERP5Workflow(id):
  """Creates an ERP5 Workflow """
  ob = DCWorkflowDefinition(id)
  setupERP5Workflow(ob)
  return ob

addWorkflowFactory(createERP5Workflow,
                   id='erp5_workflow',
                   title='ERP5-style pre-configured DCWorkflow')

class WorkflowHistoryList(DoublyLinkList):

  _bucket_size = 4000

  def __repr__(self):
    return '<%s object at 0x%x %r>' % (
      self.__class__.__name__, id(self), tuple(self))

  def __setstate__(self, state):
    # We implement a polyvalent __setstate__ on the base class because the
    # class of a ghost object may differ from the actual class and ZODB does
    # not fix it when it loads the object. 2 possible cases to fix:
    # - after a migration (self._migrate) that is aborted (transaction.abort)
    #   or invalidated (self._p_invalidate)
    # - the persistent reference in the parent (container)
    #   refers to a different class
    # If ZODB fixed the class as we would except, __setstate__ would be simpler
    # and only implemented on the legacy class.
    if type(state) is tuple:
      # legacy class that will migrate automatically
      from .patches import WorkflowTool
      self.__class__ = WorkflowTool.WorkflowHistoryList
      # BBB: Only the first 2 because of a production instance that
      #      used a temporary patch to speed up workflow history lists.
      self._prev, self._log = state[:2]
    else:
      self.__class__ = WorkflowHistoryList
      super(WorkflowHistoryList, self).__setstate__(state)

  def __getstate__(self):
    bucket = self._next
    if getattr(bucket, '_p_changed', None) is not None and \
       self._tail_count < bucket._tail_count:
      # This bucket won't be modified anymore so optimize this last change,
      # which is even more useful that there are often very few items added
      # within a transaction and many identical strings are rarely deduplicated.
      self._log = dedupStrings(self._log)
    return super(WorkflowHistoryList, self).__getstate__()


def dedupStrings(obj):
  _sequence_type_list = frozenset, list, set, tuple
  _by_id = {} # usually useless for workflow history lists
  # BBB: With Python 3, a single dict will be enough and it will even be
  #      possible to dedup hashable tuples/frozensets (workflow history
  #      lists usually don't contain these 2 types).
  _bytes = {}
  _str = {}
  def dedup(obj):
    id_ = id(obj)
    try:
      return _by_id[id_]
    except KeyError:
      t = getattr(obj, '__class__', None)
    if t is DateTime:
      obj._tz = dedup(obj._tz)
    elif t is bytes:
      obj = _bytes.setdefault(obj, obj)
    elif t is unicode:
      obj = _str.setdefault(obj, obj)
    elif t in _sequence_type_list:
      obj = t(map(dedup, obj))
    elif t is dict:
      obj = {dedup(k): dedup(v) for k, v in obj.iteritems()}
    else:
      return obj
    _by_id[id_] = obj
    return obj
  return dedup(obj)
