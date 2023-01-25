result = []
url = context.getRelativeUrl()
Base_translateString = context.Base_translateString
action_list = context.portal_actions.listFilteredActionsFor(context.getObject()).get('workflow', [])


# Javascript code
hide_and_process_js = """javascript:xmlHttp=new XMLHttpRequest();
xmlHttp.open("GET", "%s/EmailThread_processAction?action=%s", false);
xmlHttp.send(null);
this.parentNode.parentNode.style.display = 'none';
return false;"""

hide_and_reply_js = """javascript:this.parentNode.parentNode.style.display = 'none';
window.open('%s/EmailThread_processReply');
return false;
"""


# This part must be cached and optimised - XXX
# Idea: get the state, retrieve standard action string for the state
# if not available, call getObject, portal_actions, etc.
# build the standard action string - last, fead the action string with
# params through %
for action in action_list:
  action_id = action['id']
  if action_id == 'read_action':
    # Not need to display
    pass
  elif action_id == 'reply_action':
    result.append((Base_translateString(action['title']), hide_and_reply_js % url))
  else:
    result.append((Base_translateString(action['title']), hide_and_process_js % (url, action_id)))

#result.append(('Info', 'info'))
#result.append(('Subject', 'subject'))

return result
