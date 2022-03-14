from builtins import range
history = context.Base_getWorkflowHistory()
bug_history = history.get('bug_workflow', None)

follow_up_list = []

if bug_history is not None:
  title_list = bug_history['title_list']
  item_list = bug_history['item_list']
  index_dict = {}

  for i in range(len(title_list)):
    index_dict[title_list[i]] = i

  for item in item_list:
    action = item[index_dict['Action']]
    comment = item[index_dict['Comment']]
    time = item[index_dict['Time']]
    actor = item[index_dict['Actor']]

    if action is not None and action.endswith('_action'):
      if action.startswith('open'):
        # I guess nobody wants to enter a comment to open a bug.
        continue
      if not comment:
        comment = ''
      else:
        comment = comment.strip()
      if not actor:
        actor = 'unknown'
      if not time:
        time = 'unknown'
      else:
        time = time.ISO()
      follow_up_list.append('%s by %s at %s:\n%s' % (action[:-7], actor, time, comment))

comment_id = len(follow_up_list)
for i in range(len(follow_up_list)):
  follow_up_list[i] = ('Comment #%d: ' % comment_id) + follow_up_list[i]
  comment_id -= 1

return '\n\n'.join(follow_up_list)
