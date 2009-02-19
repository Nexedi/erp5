##############################################################################
#
# Copyright (c) 2007-2008 Nexedi SA and Contributors. All Rights Reserved.
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

from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from DocumentationHelper import DocumentationHelper
from Products.ERP5Type import Permissions
from Products.DCWorkflowGraph.DCWorkflowGraph import getGraph


def getRoleList(workflow):
  role_set = set()
  for state in workflow.states.objectValues():
    if state.permission_roles:
      for role_list in state.permission_roles.itervalues():
        role_set.update(role_list)
  return sorted(role_set)


class DCWorkflowDocumentationHelper(DocumentationHelper):
  """
    Provides access to all documentation information
    of a workflow.
  """

  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  _section_list = (
    dict(
      id='state',
      title='Workflow States',
      class_name='DCWorkflowStateDocumentationHelper',
    ),
    dict(
      id='transition',
      title='Workflow Transitions',
      class_name='DCWorkflowTransitionDocumentationHelper',
    ),
    dict(
      id='variable',
      title='Workflow Variables',
      class_name='DCWorkflowVariableDocumentationHelper',
    ),
    dict(
      id='worklist',
      title='Workflow Worklists',
      class_name='DCWorkflowWorklistDocumentationHelper',
    ),
    dict(
      id='script',
      title='Workflow Scripts',
      class_name='DCWorkflowScriptDocumentationHelper',
    ),
  )

  security.declareProtected(Permissions.AccessContentsInformation, 'getType')
  def getType(self):
    """
    Returns the type of the documentation helper
    """
    return "DC Workflow"

  security.declareProtected(Permissions.AccessContentsInformation, 'getRoleColumnList')
  def getRoleColumnList(self):
    """Return the list of pertinent columns for permissions on states."""
    return [(role.lower().replace(' ', '_') + '_permissions', role)
            for role in getRoleList(self.getDocumentedObject())]

  def getStateUriList(self):
    return ['%s/states#%s' % (self.uri, state)
            for state in sorted(self.getDocumentedObject().states.objectIds())]

  security.declareProtected(Permissions.AccessContentsInformation, 'getStateItemList')
  def getStateItemList(self, **kw):
    """
    """
    item_list = []
    role_column_list = self.getRoleColumnList()
    for uri in self.getStateUriList():
      helper = self.getDocumentationHelper('DCWorkflowStateDocumentationHelper', uri)
      for column_id, role in role_column_list:
        setattr(helper, column_id, helper.getPermissionsOfRole(role))
      item_list.append(helper)
    return item_list

  security.declareProtected(Permissions.AccessContentsInformation, 'getTransitionIdList')
  def getTransitionIdList(self):
    """
    """
    transition_list = []
    transitions = getattr(self.getDocumentedObject(), 'transitions', None)
    if transitions is not None:
      for transition in transitions.objectValues():
        transition_list.append(transition.getId())
    return transition_list

  security.declareProtected(Permissions.AccessContentsInformation, 'getTransitionItemList')
  def getTransitionItemList(self):
    """
    """
    transition_list = []
    trigger_type_list = ['Automatic','Initiated by user action','Initiated by WorkflowMethod']
    transitions = getattr(self.getDocumentedObject(), 'transitions', None)
    if transitions is not None:
      for transition in  self.getDocumentedObject().transitions.objectValues():
        guard_roles = ""
        guard = dir(transition.guard)
        if hasattr(transition.guard, '__dict__'):
          if 'roles' in transition.guard.__dict__.keys():
            guard_roles = ', '.join(role for role in transition.guard.__dict__['roles'])
        transition_list.append((transition.getId(),
                                getattr(transition, "title", ""),
                                trigger_type_list[transition.trigger_type],
                                getattr(transition, "description", ""),
                                guard_roles
                              ))
    return transition_list

  security.declareProtected(Permissions.AccessContentsInformation, 'getTransitionUriList')
  def getTransitionUriList(self):
    """
    """
    transition_id_list = self.getTransitionIdList()
    return map(lambda x: ('%s/transitions/%s' % (self.uri, x)), transition_id_list)

  security.declareProtected(Permissions.AccessContentsInformation, 'getTransitionURIList')
  def getTransitionURIList(self):
    """
    """
    transition_item_list = self.getTransitionItemList()
    klass = self.getDocumentedObject().__class__
    class_name = klass.__name__
    module = klass.__module__
    uri_prefix = '%s.%s.' % (module, class_name)
    return map(lambda x: ('%s%s' % (uri_prefix, x[0]), x[1], x[2], x[3], x[4]), transition_item_list)

  security.declareProtected(Permissions.AccessContentsInformation, 'getVariableIdList')
  def getVariableIdList(self):
    """
    """
    variable_list = []
    variables = getattr(self.getDocumentedObject(), 'variables', None)
    if variables is not None:
      for variable in variables.objectValues():
        variable_list.append(variable.getId())
    return variable_list

  security.declareProtected(Permissions.AccessContentsInformation, 'getVariableItemList')
  def getVariableItemList(self):
    """
    """
    variable_list = []
    variables = getattr(self.getDocumentedObject(), 'variables', None)
    if variables is not None:
      for variable in  variables.objectValues():
        variable_list.append((variable.getId(),
                              getattr(variable, "title", ""),
                              getattr(variable, "description", "")
                            ))
    return variable_list

  security.declareProtected(Permissions.AccessContentsInformation, 'getVariableURIList')
  def getVariableURIList(self):
    """
    """
    variable_item_list = self.getVariableItemList()
    klass = self.getDocumentedObject().__class__
    class_name = klass.__name__
    module = klass.__module__
    uri_prefix = '%s.%s.' % (module, class_name)
    return map(lambda x: ('%s%s' % (uri_prefix, x[0]), x[1], x[2]), variable_item_list)

  security.declareProtected(Permissions.AccessContentsInformation, 'getVariableUriList')
  def getVariableUriList(self):
    """
    """
    variable_id_list = self.getVariableIdList()
    return map(lambda x: ('%s/variables/%s' % (self.uri, x)), variable_id_list)

  security.declareProtected(Permissions.AccessContentsInformation, 'getPermissionList')
  def getPermissionList(self):
    """
    """
    return getattr(self.getDocumentedObject(), "permissions", ())

  security.declareProtected(Permissions.AccessContentsInformation, 'getWorklistIdList')
  def getWorklistIdList(self):
    """
    """
    worklist_list = []
    worklists = getattr(self.getDocumentedObject(), "worklists", None)
    if worklists is not None:
      for wl in worklists.objectValues():
        worklist_list.append(getattr(wl, "__name__", ''))
    return worklist_list

  security.declareProtected(Permissions.AccessContentsInformation, 'getWorklistItemList')
  def getWorklistItemList(self):
    """
    """
    worklist_list = []
    worklists = getattr(self.getDocumentedObject(), "worklists", None)
    if worklists is not None:
      for wl in worklists.objectValues():
        guard_roles = ""
        guard = dir(wl.guard)
        if wl.title == "":
          title = wl.actbox_name
        else:
          title = wl.title
        if hasattr(wl.guard, '__dict__'):
          if 'roles' in wl.guard.__dict__.keys():
            guard_roles = ', '.join(role for role in wl.guard.__dict__['roles'])
        worklist_list.append((wl.__name__, title, wl.__dict__["description"],guard_roles))
    return worklist_list

  security.declareProtected(Permissions.AccessContentsInformation, 'getWorklistURIList')
  def getWorklistURIList(self):
    """
    """
    worklist_item_list = self.getWorklistItemList()
    klass = self.getDocumentedObject().__class__
    class_name = klass.__name__
    module = klass.__module__
    uri_prefix = '%s.%s.' % (module, class_name)
    return map(lambda x: ('%s%s' % (uri_prefix, x[0]), x[1], x[2], x[3]), worklist_item_list)

  security.declareProtected(Permissions.AccessContentsInformation, 'getWorklistUriList')
  def getWorklistUriList(self):
    """
    """
    worklist_id_list = self.getWorklistIdList()
    return map(lambda x: ('%s/worklists/%s' % (self.uri, x)), worklist_id_list)

  security.declareProtected(Permissions.AccessContentsInformation, 'getScriptIdList')
  def getScriptIdList(self):
    """
    """
    script_list = []
    scripts = getattr(self.getDocumentedObject(), "scripts", None)
    if scripts is not None:
      for script in scripts.objectValues():
        script_list.append(getattr(script, "__name__", ''))
    return script_list

  security.declareProtected(Permissions.AccessContentsInformation, 'getScriptItemList')
  def getScriptItemList(self):
    """
    """
    script_list = []
    scripts = getattr(self.getDocumentedObject(), "scripts", None)
    if scripts is not None:
      for script in scripts.objectValues():
        script_list.append((getattr(script, "__name__", ''),
                            getattr(script, "title", '')
                           ))
    return script_list

  security.declareProtected(Permissions.AccessContentsInformation, 'getScriptURIList')
  def getScriptURIList(self):
    """
    """
    script_item_list = self.getScriptItemList()
    klass = self.getDocumentedObject().__class__
    class_name = klass.__name__
    module = klass.__module__
    uri_prefix = '%s.%s.' % (module, class_name)
    return map(lambda x: ('%s%s' % (uri_prefix, x[0]), x[1]), script_item_list)

  security.declareProtected(Permissions.AccessContentsInformation, 'getScriptUriList')
  def getScriptUriList(self):
    """
    """
    script_id_list = self.getScriptIdList()
    return map(lambda x: ('%s/scripts/%s' % (self.uri, x)), script_id_list)

  security.declareProtected(Permissions.AccessContentsInformation, 'getGraphImageURL')
  def getGraphImageURL(self):
    """
      Returns a URL to a graphic representation of the workflow
    """
    ""

  security.declareProtected(Permissions.AccessContentsInformation, 'getGraphImageData')
  def getGraphImageData(self, format='png'):
    """
      Returns the graphic representation of the workflow as a PNG file
    """
    return getGraph(self, wf_id=getattr(self.getDocumentedObject(), "__name__", ''), format=format)


InitializeClass(DCWorkflowDocumentationHelper)
