portal = context.getPortalObject()
support_request = context.getFollowUpValue()

# XXX what to do with PData ?
# As a first step just use a string.
data = str(context.getData())

is_html = context.getPortalType() == 'HTML Post'
if is_html:
  # sanitize HTML
  data = portal.portal_transforms.convertToData(
      'text/html',
       data,
       context=context,
       mimetype=context.getContentType())

web_message = portal.event_module.newContent(
    portal_type='Web Message',
    title=context.getTitle() if context.hasTitle() else None, # XXX how to find a title ?
    content_type='text/html' if is_html else 'text/plain',
    text_content=data,
    follow_up_value=support_request,
    aggregate_value=context,
    source_value=portal.portal_membership.getAuthenticatedMember().getUserValue(),
    start_date=context.getCreationDate(),
    source_reference=context.getSourceReference())

web_message.stop()
