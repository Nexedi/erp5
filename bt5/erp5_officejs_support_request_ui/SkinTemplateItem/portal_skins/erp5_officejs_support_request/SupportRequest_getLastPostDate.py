portal = context.getPortalObject()

# get the related Support Request, this should not be None
support_request_list = portal.portal_catalog(portal_type="Support Request", id=context.getId()) # with id keyword, this function will return a sequence data type which contains one element.

support_request_object = support_request_list[0].getObject()

# get the all HTML Posts which related to this Support Request

post_list = portal.portal_catalog(portal_type="HTML Post", strict_follow_up_uid=support_request_object.getUid()) # with id keyword, this function will return a sequence data type which contains one element.

post_list = sorted(post_list, key=lambda x:x.getStartDate(), reverse=True)
  
preferred_date_order = portal.portal_preferences.getPreferredDateOrder()

if post_list:
  # raise NotImplementedError(post_list[0].getStartDate())
  post_date = post_list[0].getStartDate()
  if is_pure_date:
    return post_date
  # raise NotImplementedError(post_date.strftime("%H:%M:%S"))
  if post_date.isCurrentDay():
    return post_date.strftime("%H:%M:%S")
  else:
    if preferred_date_order == 'dmy':
      return "%s/%s/%s" % (post_date.dd(), post_date.mm(), post_date.year())
    if preferred_date_order == 'mdy':
      return "%s/%s/%s" % (post_date.mm(), post_date.dd(), post_date.year())
    # ymd
    return "%s/%s/%s" % (post_date.year(), post_date.mm(), post_date.dd())
else:
  return None
