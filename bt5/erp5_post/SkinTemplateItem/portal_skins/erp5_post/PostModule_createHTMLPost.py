portal = context.getPortalObject()

# create an HTML Post
post_module = portal.post_module

# get the related object
follow_up_object, = portal.portal_catalog(relative_url=follow_up, limit=2)
follow_up_object = follow_up_object.getObject()

now = DateTime()
post_edit_kw = {
  "start_date": now,
  "follow_up_value": follow_up_object,
  "text_content": data,
}
if predecessor is not None:
  predecessor_value, = portal.portal_catalog(relative_url=predecessor, limit=2)
  post_edit_kw["predecessor_value"] = predecessor_value.getObject()
post = post_module.newContent(
  portal_type='HTML Post',
  **post_edit_kw
)

return post
