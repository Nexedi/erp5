portal = context.getPortalObject()

# create an HTML Post
post_module = portal.post_module

# get the related object
object_list = portal.portal_catalog(relative_url=follow_up) # with id keyword, this function will return a sequence data type which contains one element.
follow_up_object = None
if object_list:
  follow_up_object = object_list[0].getObject()
else:
  raise LookupError("Target follow up object not found")

now = DateTime()
post_edit_kw = {
  "start_date": now,
  "follow_up_value": follow_up_object,
  "text_content": data,
}
if predecessor is not None:
  predecessor_value, = portal.portal_catalog(relative_url=predecessor)
  post_edit_kw["predecessor_value"] = predecessor_value.getObject()
post = post_module.newContent(
  portal_type='HTML Post',
  **post_edit_kw
)

post.publish()
# We need to reindex the object on server. So the page will get the post which
# just submmitted.
post.immediateReindexObject()

return post
