# XXX do we need two scripts ??

portal = context.getPortalObject()
traverse = context.getPortalObject().restrictedTraverse

# create an HTML Post
post_module = portal.post_module

now = DateTime()
post_edit_kw = {
  "start_date": now,
  "follow_up_value": traverse(follow_up),
  "text_content": data,
  "source_reference": source_reference,
  "title": title,
}

if predecessor:
  post_edit_kw["predecessor"] = traverse(predecessor)

post = post_module.newContent(
  portal_type='HTML Post',
  **post_edit_kw
)

return post
