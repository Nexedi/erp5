portal = context.getPortalObject()

# get the all HTML Posts which related to this Support Request
post_list = portal.portal_catalog(portal_type="HTML Post", strict_follow_up_uid=context.getUid(), sort_on=(('modification_date', 'descending'),), limit=1, validation_state="published") # with id keyword, this function will return a sequence data type which contains one element.
  
if len(post_list):
  return post_list[0].asStrippedHTML()
else:
  return None
