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

from Products.ERP5Type import Permissions
from App.special_dtml import HTMLFile
from Acquisition import aq_inner
from AccessControl.requestmethod import postonly
from Products.DCWorkflow.DCWorkflow import DCWorkflowDefinition

# ERP5 workflow factory definitions
_workflow_factories = {}

try:
  from Products.CMFCore.WorkflowTool import addWorkflowFactory as baseAddWorkflowFactory
  # We're on CMF 1.5
except ImportError:
  # We're on CMF 2
  def baseAddWorkflowFactory(factory, id, tittle):
    pass

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

    factory_info = dict(factory=factory,
                        id=id,
                        title=title)
    _workflow_factories[id] = factory_info
    # register with CMF 1 if it's still there
    baseAddWorkflowFactory(factory, id, title)

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
  constructor_form_name=FACTORY_FORM_PREFIX + workflow_factory_id
  constructor_action_name=FACTORY_ACTION_PREFIX + workflow_factory_id

  # The form
  def manage_addWorkflowForm(dispatcher, REQUEST, RESPONSE):
    """Form to add a type-specific workflow to portal_workflow"""
    kw = dict(workflow_factory_title=workflow_factory_title,
              form_action=constructor_action_name)
    return manage_addWorkflowFormDtml(None, dispatcher, REQUEST, **kw)
  
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
  constructors = [(constructor_form_name, manage_addWorkflowForm),
                  (constructor_action_name, manage_addWorkflow)]
  return constructors

def addWorkflowByType(container, workflow_factory_id, workflow_id):
  """ Add a workflow with name 'workflow_id' from factory identified by
  'workflow_factory_id'
  """
  # This functionality could be inside the generated manage_addWorkflow above,
  # but is placed here to be easily used directly from Python code.
  workflow_factory = _workflow_factories[workflow_factory_id]['factory']
  workflow = workflow_factory(workflow_id)
  container._setObject(workflow_id, workflow)
  return aq_inner(container.restrictedTraverse(workflow_id))

def registerWorkflowFactory(context, factory_info):
  """ Register a workflow factory as a Zope2 style object factory that is only
  addable to portal_workflow"""
  constructors = _generateWorkflowConstructors(factory_info)
  permission = Permissions.ManagePortal
  context.registerClass(DCWorkflowDefinition, # this class is only used here for its interfaces
                        meta_type=factory_info['title'],
                        constructors=constructors,
                        permission=permission,
                        visibility=None)

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
  for state_id, state_title in (('draft', 'Draft'),):
    wf.states.addState(state_id)
    wf.states[state_id].title = state_title
  for v in ('action', 'actor', 'comment', 'history', 'time',
            'error_message', 'portal_type'):
    wf.variables.addVariable(v)
  for perm in (Permissions.AccessContentsInformation,
               Permissions.View,
               Permissions.AddPortalContent,
               Permissions.ModifyPortalContent,
               Permissions.DeleteObjects):
    wf.addManagedPermission(perm)

  wf.states.setInitialState('draft')
  # set by default the state variable to simulation_state.
  # anyway, a default workflow needs to be configured.
  wf.variables.setStateVar('simulation_state')

  vdef = wf.variables['action']
  vdef.setProperties(description='The last transition',
                     default_expr='transition/getId|nothing',
                     for_status=1, update_always=1)

  vdef = wf.variables['actor']
  vdef.setProperties(description='The name of the user who performed '
                     'the last transition',
                     default_expr='user/getUserName',
                      for_status=1, update_always=1)

  vdef = wf.variables['comment']
  vdef.setProperties(description='Comments about the last transition',
               default_expr="python:state_change.kwargs.get('comment', '')",
               for_status=1, update_always=1)

  vdef = wf.variables['history']
  vdef.setProperties(description='Provides access to workflow history',
                     default_expr="state_change/getHistory")

  vdef = wf.variables['time']
  vdef.setProperties(description='Time of the last transition',
                     default_expr="state_change/getDateTime",
                     for_status=1, update_always=1)

  vdef = wf.variables['error_message']
  vdef.setProperties(description='Error message if validation failed',
                     for_status=1, update_always=1)
  
  vdef = wf.variables['portal_type']
  vdef.setProperties(description='portal type (use as filter for worklists)',
                     for_catalog=1)

def createERP5Workflow(id):
  """Creates an ERP5 Workflow """
  ob = DCWorkflowDefinition(id)
  setupERP5Workflow(ob)
  return ob

addWorkflowFactory(createERP5Workflow,
                   id='erp5_workflow',
                   title='ERP5-style empty workflow')
