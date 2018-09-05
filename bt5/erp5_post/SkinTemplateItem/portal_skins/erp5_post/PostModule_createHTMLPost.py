# XXX do we need two scripts ??

portal = context.getPortalObject()

# create an HTML Post
post_module = portal.post_module

now = DateTime()
post_edit_kw = {
  "start_date": now,
  "follow_up_value": context.getPortalObject().restrictedTraverse(follow_up),
  "text_content": data,
  "source_reference": source_reference,
  "title": title,
}
if predecessor not in (None, ""):
  predecessor_value, = portal.portal_catalog(relative_url=predecessor, limit=2)
  post_edit_kw["predecessor_value"] = predecessor_value.getObject()
post = post_module.newContent(
  immediate_reindex=immediate_reindex_context_manager,
  portal_type='HTML Post',
  **post_edit_kw
)

return post
