from json import dumps
portal = context.getPortalObject()
document_type_list = portal.getPortalDocumentTypeList()

event_list = portal.portal_simulation.getMovementHistoryList(
    security_query=portal.portal_catalog.getSecurityQuery(),
    portal_type=portal.getPortalEventTypeList(),
    strict_follow_up_uid=context.getUid(),
    simulation_state=('started', 'stopped', 'delivered', ),
    only_accountable=False,
    omit_input=True,
    sort_on=(('date', 'asc'), ('uid', 'asc',),)
)


comment_list = []
for event in event_list:
  event = event.getObject()

  attachment_link = attachment_name = None
  attachment = event.getDefaultAggregateValue(portal_type=document_type_list)
  if attachment is not None:
    attachment_link, attachment_name = attachment.getRelativeUrl(), attachment.getFilename()

  comment_list.append((dict(
      user=event.getSourceTitle(),
      date=event.getStartDate().ISO8601(),
      text=event.asStrippedHTML(),
      attachment_link=attachment_link,
      attachment_name=attachment_name,
      message_id=event.getSourceReference(),
  )))

just_posted_comment = portal.portal_sessions[
    '%s.latest_comment' % context.getRelativeUrl()].pop(
    'comment_post_list', None)
if just_posted_comment is not None:
  # make sure not to display twice if it was already ingested in the meantime.
  if just_posted_comment['message_id'] not in [comment['message_id'] for comment in comment_list]:
    comment_list.append(just_posted_comment)

if as_json:
  return dumps(comment_list)
return comment_list
