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

def getLastFollowUpRelated(ob):
  prefix = "aggregate/"
  last = None
  for category in ob.getCategoryList():
    if category.startswith(prefix):
      last = category[len(prefix):]
  return last

post_list = portal.portal_catalog(
  portal_type="HTML Post",
  strict_follow_up_uid=context.getUid(),
  sort_on=(('modification_date', 'ascending'),),
  validation_state="published",
)
last_follow_up_related = getLastFollowUpRelated(context)
comment_list = []
for post in post_list:
  if post.getRelativeUrl() == last_follow_up_related:
    last_follow_up_related = None
  owner = post.Base_getOwnerTitle()
  time_stamp = formatDate(post.getStartDate())
  content = post.getTextContent()
  successor_list = post.getSuccessorValueList()
  successor_name = successor_link = None
  if successor_list:
    successor_link, successor_name = successor_list[0].getRelativeUrl(), successor_list[0].getFilename()
  comment_list.append((owner, time_stamp, content, successor_link, successor_name))

# XXX dirty hack to avoid immediateReindexObject
#     using support_request (context) aggregate.
#     The best way would be to check Index Related Documents Locally on portal_categories/follow_up
if last_follow_up_related:
  post = portal.restrictedTraverse("post_module/" + last_follow_up_related)
  owner = post.Base_getOwnerTitle()
  time_stamp = formatDate(post.getStartDate())
  content = post.getTextContent()
  successor_list = post.getSuccessorValueList()
  successor_name = successor_link = None
  if successor_list:
    successor_link, successor_name = successor_list[0].getRelativeUrl(), successor_list[0].getFilename()
  comment_list.append((owner, time_stamp, content, successor_link, successor_name))

return dumps(comment_list)
