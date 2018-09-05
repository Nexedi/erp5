# XXX rename, this returns the Web Message.

from json import dumps
portal = context.getPortalObject()

preferred_date_order = portal.portal_preferences.getPreferredDateOrder() or "ymd"
preferred_date_order = "/".join(preferred_date_order)
def formatDate(date):
  # XXX modification date & creation date are still in server timezone.
  #   See merge request !17
  #
  # if default_time_zone:
  #   date = date.toZone(default_time_zone)
  return date.strftime("%s %%H:%%M" %(
    preferred_date_order.
    replace("y", "%Y").
    replace("m", "%m").
    replace("d", "%d"),
  ))

event_list = portal.portal_simulation.getMovementHistoryList(
    portal_type='Web Message',
    strict_follow_up_uid=context.getUid(),
    project_uid=context.getProjectUid(),
    simulation_state=('started', 'stopped', 'delivered', ),
    only_accountable=True,
    sort_on=(('date', ),)
)


post_list = portal.portal_catalog(
  portal_type="HTML Post",
  strict_follow_up_uid=context.getUid(),
  sort_on=(('modification_date', 'ascending'),),
  validation_state="published",
)
comment_list = []
for post in post_list:
  owner = post.Base_getOwnerTitle()
  time_stamp = formatDate(post.getStartDate())
  content = post.asStrippedHTML()
  successor_list = post.getSuccessorValueList()
  successor_name = successor_link = None
  if successor_list:
    successor_link, successor_name = successor_list[0].getRelativeUrl(), successor_list[0].getFilename()
  comment_list.append((owner, time_stamp, content, successor_link, successor_name))

return dumps(comment_list)

comment_list = [
  dict(
    source_reference=event.getSourceReference(),
    sender_title=event.getSourceTitle(),
    start_date=event.getStartDate().RFC(),
    content=data,
    attachment_list=[])]
return dumps(comment_list)
