# pylint: disable=redefined-builtin
from Products.PythonScripts.standard import newline_to_br, html_quote
portal = context.getPortalObject()
prefs = portal.portal_preferences
report_item_list = []
message_text_format = "text/plain"
pre_convert_tag = 'pre-convert-report-%s' % random.randint(0, 1000)

if prefs.getPreferredDeferredReportStoredAsDocument():
  for attachment in attachment_list:
    document = portal.portal_contributions.newContent(
          data=attachment['content'],
          publication_section=prefs.getPreferredDeferredReportPublicationSection(),
          classification=prefs.getPreferredDeferredReportClassification(),
          filename=attachment['name'],
    )
    document.share()
    report_item_list.append(
      (attachment.get('title', document.getStandardFilename(format=format)), document.getRelativeUrl()))
    # pre-convert document before sending notification
    if format:
      document.activate(
          node=portal.portal_preferences.getPreferredDeferredReportActivityFamily(),
          tag=pre_convert_tag,
      ).convert(format=format)

  url_base = portal.ERP5Site_getAbsoluteUrl()
  attachment_link_list = [
    {
      'download_link': '%s/%s?format=%s' % (url_base , report_url, format),
      'name': report_name
    } for  (report_name, report_url) in report_item_list
  ]
  message_html = newline_to_br(html_quote(message))

  message_text_format = "text/html"
  attachment_list = []
  notification_message_reference = prefs.getPreferredDeferredReportNotificationMessageReference()
  if notification_message_reference:
    notification_message = portal.portal_notifications.getDocumentValue(reference=notification_message_reference)
    if notification_message is None:
      raise ValueError('Notification message not found by %r' % prefs.getPreferredDeferredReportNotificationMessageReference())
    notification_mapping_dict = {
        'report_link_list': portal.ERP5Site_viewReportCompleteNotificationMessage(
            attachment_link_list=attachment_link_list
        ),
        'message': message_html
    }
    message = notification_message.asEntireHTML(
        safe_substitute=False,
        substitution_method_parameter_dict={'mapping_dict': notification_mapping_dict})
  else:
    # fallback to generating message with the page template when no notification message
    message = portal.ERP5Site_viewReportCompleteNotificationMessage(
        attachment_link_list=attachment_link_list,
        message=message_html
    )

portal.portal_notifications.activate(
    activity='SQLQueue',
    node=portal.portal_preferences.getPreferredDeferredReportActivityFamily(),
    after_tag=pre_convert_tag,
  ).sendMessage(
    recipient=user_name,
    subject=subject,
    message=message,
    message_text_format=message_text_format,
    notifier_list=('Mail Message',),
    store_as_event=False,
    attachment_list=attachment_list,
  )
