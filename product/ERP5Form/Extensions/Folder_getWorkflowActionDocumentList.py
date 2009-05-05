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
            doc.getPortalTypeName())
    return get_url

  request = self.REQUEST
  portal = self.getPortalObject()
  Base_translateString = portal.Base_translateString
  wf_tool = portal.portal_workflow
  selection_tool = portal.portal_selections
  
  selection_name = request['selection_name']

  # guess all column name from catalog schema
  possible_state_list = [column_name for column_name in
       self.getPortalObject().portal_catalog.getSQLCatalog().getColumnMap() if
       column_name.endswith('state') and '.' not in column_name]

  # If there are checked uids, only use checked uids.
  selection_uid_list = selection_tool.getSelectionCheckedUidsFor(selection_name)
  
  document_list = []
  
  counter = 0
  if not selection_uid_list:
    for workflow_state in possible_state_list:
      selection_params = \
              selection_tool.getSelectionParamsFor(selection_name).copy()
      selection_params['where_expression'] = \
                        'catalog.%s is not NULL' % workflow_state
      selection_params['group_by'] = ('catalog.portal_type',
                                      'catalog.%s' % workflow_state)
      selection_params['select_expression'] = (
          'count(catalog.uid) as count, catalog.portal_type, catalog.%s'
            % workflow_state)
      
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
                            workflow_title=Base_translateString(workflow.title_or_id()),
                            translated_workflow_state_title=
                                   translated_workflow_state_title,
                            count=brain.count,
                            
                            workflow_id=workflow.getId(),
                            portal_type=doc.getPortalTypeName(),
                            state_var=state_var,
                            workflow_state=doc.getProperty(state_var),
                            ))
  
  else:
    getObject = portal.portal_catalog.getObject
    selected_document_list = [getObject(uid) for uid in selection_uid_list]
    marker = []
    # this will be a dictionnary with (portal_type, workflow_id, workflow_state)
    # as keys, and (count, a random document) as values
    workflow_state_dict = dict()

    for document in selected_document_list:
      for state_var in possible_state_list:
        for workflow in wf_tool.getWorkflowsFor(document):
          if state_var == workflow.variables.getStateVar():
            key = (document.getPortalTypeName(), workflow.getId(),
                        document.getProperty(state_var))
            document_count = workflow_state_dict.get(key, [None, 0])[1]
            workflow_state_dict[key] = document, document_count + 1
    
    
    counter = 0
    for (ptype, workflow_id, state), (doc, document_count) in\
                workflow_state_dict.items():
      counter += 1
      workflow = wf_tool.getWorkflowById(workflow_id)
      state_var = workflow.variables.getStateVar()
      translated_workflow_state_title = doc.getProperty(
                      'translated_%s_title' % state_var)
      document_list.append(doc.asContext(
                uid='new_%s' % counter,
                getListItemUrl=UrlGetter(doc, state_var),
                workflow_title=Base_translateString(workflow.title_or_id()),
                translated_workflow_state_title=
                       translated_workflow_state_title,
                count=document_count,
                
                workflow_id=workflow.getId(),
                portal_type=doc.getPortalTypeName(),
                state_var=state_var,
                workflow_state=doc.getProperty(state_var),
                ))
  
  return document_list



def getWorkflowActionDocumentList(self, **kw):
  """This returns the list of all documents on which we will pass a workflow
  transition.
  """
  listbox = kw.get('listbox', None)
  if listbox is None:
    # if the listbox is empty
    return []

  selection_name = kw['module_selection_name']
  document_list = []
  portal = self.getPortalObject()
  getObject = portal.portal_catalog.getObject
  searchResults = portal.portal_catalog.searchResults
  wtool = portal.portal_workflow
  stool = portal.portal_selections
  original_selection_params = stool.getSelectionParamsFor(selection_name)
  original_selection_params.setdefault('sort_on', kw.get('sort_on'))

  selection_uid_list = stool.getSelectionCheckedUidsFor(selection_name)

  if selection_uid_list:
    original_selection_params['uid'] = selection_uid_list

  translate = self.Base_translateString
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
                             workflow_action_title=translate(action_list[0]['name']),
                             workflow_action=action,
                             workflow_id=workflow_id))

  return document_list

