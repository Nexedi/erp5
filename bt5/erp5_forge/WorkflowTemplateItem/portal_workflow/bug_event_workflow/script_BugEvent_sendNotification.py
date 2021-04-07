bug_message = state_change["object"]

# Bug Information
bug = bug_message.getParentValue()
body = """
  Bug     : %s
  Status  : %s
  Date    : %s
  Link    : %s/view
""" %  (bug.getTitle(''), bug.getSimulationStateTitle(),
            bug.getStartDate(''),  bug.getAbsoluteUrl())

if bug.getSourceTitle() is not None:
  body += """  Requester  : %s
  Assignee   : %s
""" % (bug.getDestinationTitle(''), bug.getSourceTitle(''),)

if bug.getSourceTradeTitle() is not None:
  body += """  Reporter   : %s
""" % (bug.getSourceTradeTitle(''),)

if bug.getSourceDecisionTitle() is not None:
  body += """  Supervisor : %s
""" % (bug.getSourceDecisionTitle(''),)

if bug.getDestinationProjectTitle() is not None:
  body += """  Request Project  : %s
""" % bug.getDestinationProjectTitle()

if bug.getSourceProjectTitle() is not None:
  body += """  Assigned Project : %s
""" % bug.getSourceProjectTitle()

body += """
  Description:

%s

""" % (bug.getDescription(''))

attachment_list = bug.Base_getRelatedDocumentList(
                          portal_type=bug.getPortalDocumentTypeList())
if attachment_list:
  body += """Attachments:

  %s

""" % ('\n  '.join(['%s %s/view' % (a.getTitle(), a.absolute_url()) for a in attachment_list]))
body += """ Messages :
"""
# Messages Information
simulation_state = ('delivered', 'started')
bug_message_list = [bug_message]
lines_list = bug.searchFolder(portal_type='Bug Line', sort_on=(("id", "DESC"),),
                              simulation_state=simulation_state)
bug_message_list.extend(lines_list)
message_count = len(bug_message_list)+1
for message in bug_message_list:
  message_count -= 1
  text = message.asText()
  body += """
++++++ Message #%s submitted by %s on %s ++++++
%s
""" % (message_count, message.getSourceTitle(''),
            message.getStartDate(),  text )

recipient_list = bug_message.BugLine_getRecipientValueList()
if not recipient_list: return

portal = bug_message.getPortalObject()
portal.portal_notifications.sendMessage(sender=bug_message.getSourceValue(),
                          recipient=recipient_list,
                          subject="[Bug %s] %s" % (bug.getReference(), bug.getTitle()),
                          message=body)
