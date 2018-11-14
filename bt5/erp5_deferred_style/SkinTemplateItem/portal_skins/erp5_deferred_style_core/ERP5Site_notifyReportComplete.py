portal = context.getPortalObject()
prefs = portal.portal_preferences
report_item_list = []
from Products.PythonScripts.standard import newline_to_br, html_quote
message_text_format = "text/plain"

if prefs.getPreferredDeferredReportStoredAsDocument():
  for attachment in attachment_list:
    document = portal.portal_contributions.newContent(
          data=attachment['content'],
          publication_section=prefs.getPreferredDeferredReportPublicationSection(),
          classification=prefs.getPreferredDeferredReportClassification(),
          filename=attachment['name'],
          #title=attachment['name'],
    )
    document.share()
    report_item_list.append(
      (attachment.get('title', document.getStandardFilename(format=format)), #attachment['name']),
        document.getRelativeUrl()))

  url_base = portal.ERP5Site_getAbsoluteUrl()
  report_url_text = '<br/>'.join([
    '''<a href="%s/%s?format=%s">%s</a>''' % (url_base , report_url, format, report_name ) for (report_name, report_url) in report_item_list ])
  message = '%s<br/>%s' % ( newline_to_br(html_quote(message)), report_url_text )
  message_text_format = "text/html"
  attachment_list = []
  notification_message_reference = prefs.getPreferredDeferredReportNotificationMessageReference()
  if notification_message_reference:
    notification_message = portal.portal_notifications.getDocumentValue(reference=notification_message_reference)
    if notification_message is None:
      raise ValueError('Notification message not found by %r' % prefs.getPreferredDeferredReportNotificationMessageReference())
    notification_mapping_dict={
        'report_link_list': report_url_text,
      }
    if notification_message.getContentType() == "text/html":
      message = notification_message.asEntireHTML(
        safe_substitute=False,
        substitution_method_parameter_dict={'mapping_dict':notification_mapping_dict})
    else:
      message_text_format = "text/plain"
      message = notification_message.asText(
        safe_substitute=False,
        substitution_method_parameter_dict={'mapping_dict':notification_mapping_dict})


portal.portal_notifications.activate(activity='SQLQueue').sendMessage(
    recipient=user_name,
    subject=subject,
    message=message,
    message_text_format=message_text_format,
    notifier_list=('Mail Message',),
    store_as_event=False,
    attachment_list=attachment_list,
  )
