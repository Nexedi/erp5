from json import dumps
portal = context.getPortalObject()
document_type_list = portal.getPortalDocumentTypeList()

event_list = portal.portal_simulation.getMovementHistoryList(
    portal_type=portal.getPortalEventTypeList(),
    strict_follow_up_uid=context.getUid(),
    simulation_state=('started', 'stopped', 'delivered', ),
    only_accountable=True,
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

  comment_list.append((
      event.getSourceTitle(),
      event.getStartDate().rfc822(),
      event.asStrippedHTML(),
      attachment_link,
      attachment_name,
      event.getSourceReference(),
  ))

just_posted_comment = portal.portal_sessions[
    '%s.latest_comment' % context.getRelativeUrl()].pop(
    'comment_post_list', None)
if just_posted_comment is not None:
  # make sure not to display twice if it was already ingested in the meantime.
  if just_posted_comment[-1] not in [comment[-1] for comment in comment_list]:
    comment_list.append(just_posted_comment)


return dumps(comment_list)
