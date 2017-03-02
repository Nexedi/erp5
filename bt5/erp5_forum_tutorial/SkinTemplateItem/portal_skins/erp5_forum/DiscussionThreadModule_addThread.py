person = context.getPortalObject().portal_membership.getAuthenticatedMember().getUserValue()
translateString = context.Base_translateString

discussion_thread = context.newContent(
    title=title,
    text_content=text_content,
    portal_type='Discussion Thread'
)
discussion_post = discussion_thread.newContent(
    title=title,
    text_content=text_content,
    source_value=person,
    portal_type='Discussion Post'
)

discussion_thread.publish()
portal_status_message = translateString(
    'New post created. Your post will be reviewed for approval..'
)

if batch_mode:
  # For unit tests
  return discussion_thread

return discussion_thread.Base_redirect('view',
    keep_items = dict(portal_status_message=portal_status_message), **kw)
