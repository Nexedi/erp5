# -*- coding: utf-8 -*-
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

from hashlib import md5

# Some workflow does not make sense in the context of mass transition and are
# not proposed.
skipped_workflow_id_list = ['delivery_causality_workflow',]

def generateUid(portal_type, workflow_id, workflow_state):
  return 'new_' + md5('%s/%s/%s' % (portal_type, workflow_id, workflow_state)).hexdigest()

def getDocumentGroupByWorkflowStateList(self, form_id='', **kw):
  """This returns the list of all "document groups", ie document of the same
  portal type, in the same workflow state.

  Note that this is not in a Script Python, because this would need a Manager
  proxy role, but if we use a script with proxy roles, those roles are used
  when searching catalog.
  """
  def UrlGetter(doc, state_var):
    """returns an url method."""
    def get_url(*args, **kw):
      return '%s?reset:int=1&%s=%s&portal_type=%s' % (
            self.absolute_url(), state_var, doc.getProperty(state_var),
            doc.getPortalTypeName())
    return get_url

  portal = self.getPortalObject()
  Base_translateString = portal.Base_translateString
  wf_tool = portal.portal_workflow
  selection_tool = portal.portal_selections
  last_form = getattr(self, form_id)

  last_listbox = last_form.Base_getListbox()
  selection_name = last_listbox.get_value('selection_name')

  # guess all column name from catalog schema
  possible_state_list = [column_name.split('.')[1] for column_name in
       self.getPortalObject().portal_catalog.getSQLCatalog().getColumnMap() if
       column_name.startswith('catalog.') and column_name.endswith('state')]

  # If there are checked uids, only use checked uids.
  selection_uid_list = selection_tool.getSelectionCheckedUidsFor(selection_name)

  document_list = []

  if not selection_uid_list:
    for workflow_state in possible_state_list:
      params = \
          selection_tool.getSelectionParamsFor(selection_name).copy()
      params['where_expression'] = \
                       'catalog.%s is not NULL' % workflow_state
      params['group_by'] = ('catalog.portal_type',
                                      'catalog.%s' % workflow_state)
      params['select_dict'] = {'count': 'count(catalog.uid)'}

      for brain in selection_tool.callSelectionFor(selection_name, params=params):
        doc = brain.getObject()
        for workflow in wf_tool.getWorkflowsFor(doc):
          if workflow.getId() in skipped_workflow_id_list:
            continue
          state_var = workflow.variables.getStateVar()
          translated_workflow_state_title = doc.getProperty(
                          'translated_%s_title' % state_var)
          if state_var == workflow_state:
            workflow_id = workflow.getId()
            current_workflow_state = doc.getProperty(state_var)
            document_list.append(doc.asContext(
                            uid=generateUid(doc.getPortalType(), workflow_id, current_workflow_state),
                            getListItemUrl=UrlGetter(doc, state_var),
                            workflow_title=Base_translateString(workflow.title_or_id()),
                            translated_workflow_state_title=
                                   translated_workflow_state_title,
                            count=brain.count,
                            workflow_id=workflow_id,
                            portal_type=doc.getPortalTypeName(),
                            state_var=state_var,
                            workflow_state=current_workflow_state,
                            ))

  else:
    getObject = portal.portal_catalog.getObject
    selected_document_list = [getObject(uid) for uid in selection_uid_list]
    # this will be a dictionnary with (portal_type, workflow_id, workflow_state)
    # as keys, and (count, a random document) as values
    workflow_state_dict = {}

    for document in selected_document_list:
      for state_var in possible_state_list:
        for workflow in wf_tool.getWorkflowsFor(document):
          if workflow.getId() in skipped_workflow_id_list:
            continue
          if state_var == workflow.variables.getStateVar():
            key = (document.getPortalTypeName(), workflow.getId(),
                        document.getProperty(state_var))
            document_count = workflow_state_dict.get(key, (None, 0))[1]
            workflow_state_dict[key] = document, document_count + 1


    for (ptype, workflow_id, _), (doc, document_count) in\
                workflow_state_dict.iteritems():
      workflow = wf_tool.getWorkflowById(workflow_id)
      state_var = workflow.variables.getStateVar()
      translated_workflow_state_title = doc.getProperty(
                      'translated_%s_title' % state_var)
      workflow_id = workflow.getId()
      current_workflow_state = doc.getProperty(state_var)
      document_list.append(doc.asContext(
                uid=generateUid(ptype, workflow_id, current_workflow_state),
                getListItemUrl=UrlGetter(doc, state_var),
                workflow_title=Base_translateString(workflow.title_or_id()),
                translated_workflow_state_title=
                       translated_workflow_state_title,
                count=document_count,
                workflow_id=workflow_id,
                portal_type=doc.getPortalTypeName(),
                state_var=state_var,
                workflow_state=current_workflow_state,
                ))

  # Let us sort this list by translated title of workflow state and workflow
  def compareState(a, b):
    return cmp((a.workflow_title, a.translated_workflow_state_title),
               (b.workflow_title, b.translated_workflow_state_title))
  document_list.sort(compareState)

  # Return result
  return document_list



def getWorkflowActionDocumentList(self, **kw):
  """This returns the list of all documents on which we will pass a workflow
  transition.
  """
  listbox = kw.get('workflow_action_listbox', None)
  if listbox is None:
    # if the listbox is empty
    return []

  selection_name = kw['module_selection_name']
  document_list = []
  portal = self.getPortalObject()
  wtool = portal.portal_workflow
  selection_tool = portal.portal_selections

  selection_uid_list = selection_tool.getSelectionCheckedUidsFor(selection_name)

  translate = self.Base_translateString
  for listbox_selection in listbox:
    if listbox_selection.get('workflow_action'):
      selection_params = selection_tool.getSelectionParamsFor(selection_name).copy()
      selection_params.setdefault('sort_on', kw.get('sort_on'))
      selection_params[listbox_selection['state_var']] = \
                                listbox_selection['workflow_state']
      selection_params['portal_type'] = listbox_selection['portal_type']
      if selection_uid_list:
        selection_params['uid'] = selection_uid_list

      workflow_id, action = listbox_selection['workflow_action'].split('/')[:2]
      workflow = wtool.getWorkflowById(workflow_id)
      for doc in selection_tool.callSelectionFor(selection_name, params=selection_params):
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

def getPossibleWorkflowActionItemList(self, brain, **kw):
  """
  SECURITY AUDIT - CHECKED
  This external method should be safe, because we cannot pass brain
  from URL.
  """
  portal = self.getPortalObject()
  Base_translateString = portal.Base_translateString
  item_list = [('', '')]
  for action in portal.portal_actions.listFilteredActionsFor(brain).get('workflow', []):
    transition = action.get('transition', None)
    if transition is not None:
      workflow_id = action['transition'].aq_parent.aq_parent.getId()
      if workflow_id == brain.workflow_id:
        dialog_id = action['url'].split('?', 1)[0].split('/')[-1]
        dialog_object = getattr(portal, dialog_id, None)
        if dialog_object is None or dialog_object.meta_type != 'ERP5 Form':
          dialog_id = portal.Base_viewWorkflowActionDialog.getId()
        item_list.append((Base_translateString(action['title']),
                          '%s/%s/%s' % (workflow_id, action['id'], dialog_id)))

  return item_list
