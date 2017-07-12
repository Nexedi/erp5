portal = context.getPortalObject()

# get the related Support Request, this should not be None
support_request_list = portal.portal_catalog(portal_type="Support Request", id=context.getId()) # with id keyword, this function will return a sequence data type which contains one element.

support_request_object = support_request_list[0].getObject()

# get the all HTML Posts which related to this Support Request

post_list = portal.portal_catalog(portal_type="HTML Post", strict_follow_up_uid=support_request_object.getUid()) # with id keyword, this function will return a sequence data type which contains one element.

post_list = sorted(post_list, key=lambda x:x.getStartDate(), reverse=False)

if post_list:
  return post_list[0].Base_getOwnerTitle()
else:
  return None
