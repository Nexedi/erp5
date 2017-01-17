import json
transition_comment = {}
transition_comment_list = []
index = 0

item_list = context.Base_getWorkflowHistoryItemList(workflow_id = workflow_id)
for i in item_list:
  comment = getattr(i, 'comment')
  if comment:
    action = getattr(i, 'action')
    if action in  ('Ask Question Action','Close Ticket Action','Open Ticket Action','Accept Ticket Acction', 'Open Ticket'):
      if listbox_view:
        transition_comment_list.append(i)
      else:
        transition_comment[index] = {
          'actor': getattr(i, 'actor'),
          'time': getattr(i, 'time').Date().replace('/','-'),
          'comment': comment
        }
        index += 1

if listbox_view:
  return transition_comment_list
return json.dumps(transition_comment)
