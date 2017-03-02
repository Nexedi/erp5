person = context.getPortalObject().portal_membership.getAuthenticatedMember().getUserValue()

discussion_post = context.newContent(
    title=title,
    text_content=text_content,
    source_value=person,
    portal_type='Discussion Post'
)
if batch_mode:
  return discussion_post

translateString = context.Base_translateString

portal_status_message = translateString('New reply created.')
context.Base_redirect('view',
    keep_items = dict(portal_status_message=portal_status_message))
