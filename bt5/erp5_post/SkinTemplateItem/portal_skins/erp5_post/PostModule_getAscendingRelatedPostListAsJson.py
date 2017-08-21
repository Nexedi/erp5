from json import dumps

portal = context.getPortalObject()

comment_list = []
if not follow_up:
  return dumps(comment_list)

# get the follow up object
object_list = portal.portal_catalog(relative_url=follow_up) # with id keyword, this function will return a sequence data type which contains one element.
if object_list:
  follow_up_object = object_list[0].getObject()
else:
  raise NotImplementedError(follow_up)
  
# get the all HTML Posts which related to this follow up object
post_list = portal.portal_catalog(portal_type="HTML Post", strict_follow_up_uid=follow_up_object.getUid(), sort_on=(('modification_date', 'ascending'),), validation_state="published") # with id keyword, this function will return a sequence data type which contains one element.

preferred_date_order = portal.portal_preferences.getPreferredDateOrder()

def format_date(date):
  # XXX modification date & creation date are still in server timezone.
  #   See merge request !17
  #
  # if default_time_zone:
  #   date = date.toZone(default_time_zone)
  if preferred_date_order == 'dmy':
    return "%s/%s/%s&nbsp;&nbsp;&nbsp;%s" % (date.dd(), date.mm(), date.year(), date.TimeMinutes())
  if preferred_date_order == 'mdy':
    return "%s/%s/%s&nbsp;&nbsp;&nbsp;%s" % (date.mm(), date.dd(), date.year(), date.TimeMinutes())
  # ymd
  return "%s/%s/%s&nbsp;&nbsp;&nbsp;%s" % (date.year(), date.mm(), date.dd(), date.TimeMinutes())

for post in post_list:
  owner = post.Base_getOwnerTitle()
  time_stamp = format_date(post.getStartDate())
  content = post.getTextContent()
  successor_list = post.getSuccessorValueList()
  successor_name = successor_link = None
  if successor_list:
    successor_link, successor_name = successor_list[0].getRelativeUrl(), successor_list[0].getFilename()
    
  comment_list.append((owner, time_stamp, content, successor_link, successor_name))
  
return dumps(comment_list)
