portal = context.getPortalObject()
index = len(portal.portal_catalog(portal_type='Text Post', follow_up_uid=context.getUid()))
text_post = portal.post_message_module.newContent(
  portal_type = "Text Post",
  int_index = index,
  follow_up_value = context,
  destination_reference = context.getSourceReference(),
  source_reference = 'expense_validation_record',
  title = context.getTitle(),
  description= text_content)
text_post.post()
if not batch_mode:
  return context.Base_redirect(form_id,
         keep_items = dict(
             portal_status_message=context.Base_translateString("Comment added.")
  ))
else:
  return text_post
