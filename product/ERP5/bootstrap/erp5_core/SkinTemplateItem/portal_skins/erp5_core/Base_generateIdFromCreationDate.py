# retrieve a date from object and return the new id
if obj is None:
  obj = context
# first try to get the creation date directly
date = obj.getCreationDate()
if date is None:
  workflow_item_list = context.Base_getWorkflowHistoryItemList('edit_workflow', display=0)
  workflow_item_list.reverse()
  for workflow_item in workflow_item_list:
    if workflow_item.getProperty('action') == "edit":
      date = workflow_item.getProperty('time')
      break
if date is None:
  # else use current date
  from DateTime import DateTime
  date = DateTime()

date = date.Date().replace('/', '')
old_id = obj.getId()
return "%s-%s" %(date, old_id)
