## Script (Python) "TemplateTool_getWorkflowListAsCSV"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
workflow_dict = {}

for bt in context.portal_templates.contentValues(filter={'portal_type':'Business Template'}):
  workflow_dict[bt.getTitle()] = {}
  for id in bt.getTemplateWorkflowIdList():
    workflow_dict[bt.getTitle()][id] = 1

bt_list = workflow_dict.keys()
bt_list.sort()

workflow_list = []
for wf in context.portal_workflow.objectValues():
  workflow_list.append(wf.getId())
workflow_list.sort()

msg = ','.join([''] + bt_list) + '\n'
for wf in workflow_list:
  msg += wf
  for bt in bt_list:
    msg += wf in workflow_dict[bt] and ',X' or ','
  msg += '\n'

return msg
