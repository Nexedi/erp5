from Products.ERP5Type.Message import translateString
portal = context.getPortalObject()
support_request = context.getFollowUpValue()
web_site_value = portal.restrictedTraverse(web_site_relative_url)

# XXX what to do with PData ?
# As a first step just use bytes.
data = bytes(context.getData())

is_html = context.getPortalType() == 'HTML Post'
if is_html:
  # sanitize HTML
  data = portal.portal_transforms.convertToData(
      'text/x-html-safe',
       data,
       context=context,
       mimetype=context.getContentType())

# lookup a resource and a source.
# It's critical for support request app that we can create movement with source and resouce
# because movements without source & resource does not get indexed in stock table. As this
# app uses Inventory API to list the history of movements, movements needs to be indexed.
resource = web_site_value.getLayoutProperty('preferred_event_resource', None)
if not resource:
  resource = portal.portal_preferences.getPreferredEventResource()
assert resource, "No resource configured for event"

source_value = portal.Base_getUserValueByUserId(context.getOwnerInfo()['id'])
if source_value is None:
  # try harder to get a source for non-person users.
  source_value = support_request.getSourceSectionValue()

web_message = portal.event_module.newContent(
    portal_type='Web Message',
    title=context.getTitle() if context.hasTitle() else None,
    content_type='text/html' if is_html else 'text/plain',
    text_content=data.decode('utf-8'),
    follow_up_value=support_request,
    aggregate_value_list=[context] + context.getSuccessorValueList(
      portal_type=portal.getPortalDocumentTypeList()),
    resource=resource,
    source_value=source_value,
    start_date=context.getCreationDate(),
    source_reference=context.getSourceReference())

context.archive(
  comment=translateString('Ingested as ${web_message_reference}',
    mapping={'web_message_reference': web_message.getReference()}))

web_message.stop()
