bug = state_change["object"]
history = bug.portal_workflow.getInfoFor(bug, 'history',
                                         wf_id='bug_workflow')
is_re_assign_action = False
send_event = None
for history_item in history[::-1]:
  if same_type(history_item['action'], '') and history_item['action'].endswith('action'):
    send_event = history_item['send_event']
    is_re_assign_action = bool(history_item['action'] == 're_assign_action')
    break

valid_transaction_list = ["confirm_action", "stop_action",
                          "deliver_action", "set_ready_action", "cancel_action", "re_assign_action"]

message = [ h for h in state_change.getHistory() \
                                        if h['action'] in valid_transaction_list]

comment = ""
if len(message) > 0:
  comment=message[-1]["comment"]

state = bug.getSimulationStateTitle()
if is_re_assign_action:
  state = 'Re %s' % (state)
line = bug.newContent(title="%s %s was %s" % (bug.getPortalType(),
                                              bug.getReference(),
                                              state),
                      portal_type="Bug Line",
                      text_content=comment,
                      content_type='text/plain')
if send_event:
  # This will post The message Automatically.
  line.start()
else:
  line.plan()
