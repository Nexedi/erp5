from Products.ERP5Type.Message import translateString
portal = context.getPortalObject()
messenger_thread = context.getFollowUpValue()
web_site_value = portal.restrictedTraverse(web_site_relative_url) if web_site_relative_url else None

data = str(context.getData())
is_html = context.getPortalType() == 'HTML Post'
if is_html: # sanitize HTML
  data = portal.portal_transforms.convertToData(
      'text/x-html-safe',
       data,
       context=context,
       mimetype=context.getContentType())

# TODO: check resource, in support_request seems to be important
resource = None
source_value = context.ERP5Site_getAuthenticatedMemberPersonValue()

web_message = portal.event_module.newContent(
                portal_type = 'Web Message',
                title = context.getTitle(),
                content_type = 'text/html' if is_html else 'text/plain',
                text_content = data,
                follow_up_value = messenger_thread,
                aggregate_value_list = [context] + context.getSuccessorValueList(
                  portal_type = portal.getPortalDocumentTypeList()),
                resource = resource,
                source_value = source_value,
                start_date = context.getCreationDate(),
                source_reference = context.getSourceReference())

web_message.stop()
context.archive(
  comment=translateString('Ingested as ${web_message_reference}',
    mapping={'web_message_reference': web_message.getReference()}))
