#############################################################################
#
# Copyright (c) 2007 Nexedi SA and Contributors. All Rights Reserved.
#                    Jerome Perrin <jerome@nexedi.com>
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

from Products.PythonScripts.standard import Object


def getDocumentGroupByWorkflowStateList(self, **kw):
  """This returns the list of all "document groups", ie document of the same
  portal type, in the same workflow state.
  
  Note that this is not in a Script Python, because this would need a Manager
  proxy role, but if we use a script with proxy roles, those roles are used
  when searching catalog.
  """
  def UrlGetter(doc, state_var):
    """returns an url method."""
    def get_url(*args, **kw):
      return '%s/view?reset:int=1&%s=%s&portal_type=%s' % (
            self.absolute_url(), state_var, doc.getProperty(state_var),
            doc.getPortalType())
    return get_url

  request = self.REQUEST
  portal = self.getPortalObject()
  N_ = portal.Base_translateString
  wf_tool = portal.portal_workflow
  selection_tool = portal.portal_selections
  
  selection_name = request['selection_name']
  # TODO this should be guessed somehow, but portal_catalog.schema() contains
  # much more than what we need here.
  possible_state_list = ['validation_state', 'simulation_state', 'payment_state',]
  
  # If there are checked uids, only use checked uids.
  selection_uid_list = selection_tool.getSelectionCheckedUidsFor(selection_name)
  # TODO invert mode: calculate in python
  
  document_list = []
  
  counter = 0
  if not selection_uid_list:
    for workflow_state in possible_state_list:
      selection_params = \
              selection_tool.getSelectionParamsFor(selection_name).copy()
      selection_params['where_expression'] = '%s is not NULL' % workflow_state
      selection_params['group_by'] = ('portal_type', workflow_state)
      selection_params['select_expression'] = (
           'count(catalog.uid) as count, portal_type, %s' % workflow_state)
      
      for brain in self.searchFolder(**selection_params):
        doc = brain.getObject()
        for workflow in wf_tool.getWorkflowsFor(doc):
          state_var = workflow.variables.getStateVar()
          translated_workflow_state_title = doc.getProperty(
                          'translated_%s_title' % state_var)
          if state_var == workflow_state:
            counter += 1
            document_list.append(doc.asContext(
                            uid='new_%s' % counter,
                            getListItemUrl=UrlGetter(doc, state_var),
                            workflow_title=N_(workflow.title_or_id()),
                            translated_workflow_state_title=
                                   translated_workflow_state_title,
                            count=brain.count,
                            
                            workflow_id=workflow.getId(),
                            portal_type=doc.getPortalType(),
                            state_var=state_var,
                            workflow_state=doc.getProperty(state_var),
                            ))
  
  else:
    getObject = portal.portal_catalog.getObject
    workflow_state_dict = dict()
    for document in [getObject(uid) for uid in selection_uid_list]:
      state = document.getProperty(workflow_state)
      ptype = document.getPortalTypeName()
      workflow_state_dict[(ptype, state)] = \
             workflow_state_dict.get((ptype, state), 0) + 1
  
      document_list = [Object(uid='new_',
            translated_portal_type='TODO: count in python')]
  
  return document_list



def getWorkflowActionDocumentList(self, **kw):
  """This returns the list of all documents on which we will pass a workflow
  transition.
  """
  listbox = kw['listbox']
  selection_name = kw['module_selection_name']
  document_list = []
  portal = self.getPortalObject()
  getObject = portal.portal_catalog.getObject
  searchResults = portal.portal_catalog.searchResults
  wtool = portal.portal_workflow
  stool = portal.portal_selections
  original_selection_params = \
    portal.portal_selections.getSelectionParamsFor(selection_name)
  original_selection_params.setdefault('sort_on', kw.get('sort_on'))

  # TODO: invert mode

  for listbox_selection in listbox:
    if listbox_selection.get('workflow_action'):
      selection_params = original_selection_params.copy()
      selection_params[listbox_selection['state_var']] = \
                                listbox_selection['workflow_state']
      selection_params['portal_type'] = listbox_selection['portal_type']

      workflow_id, action = listbox_selection['workflow_action'].split('/')
      workflow = wtool.getWorkflowById(workflow_id)
      for doc in searchResults(**selection_params):
        doc = doc.getObject()
        action_list = [ai for ai in
                        workflow.listObjectActions(wtool._getOAI(doc))
                        if ai['id'] == action]
        if action_list:
          document_list.append(doc.asContext(
                             workflow_action_title=action_list[0]['name'],
                             workflow_action=action,
                             workflow_id=workflow_id))

  return document_list

