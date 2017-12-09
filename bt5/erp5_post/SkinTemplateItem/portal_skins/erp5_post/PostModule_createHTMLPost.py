portal = context.getPortalObject()
post_module = portal.post_module

now = DateTime()
assert "text_content" in post_edit_kw or "data" in post_edit_kw
post = post_module.newContent(
  portal_type='HTML Post',
  start_date=now,
  **post_edit_kw
)
assert post.getFollowUp()

return post
