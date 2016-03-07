""" Send notification email when a person send subscription form.
Parameters:
context_url -- url of context (string)
notification_reference -- reference of notification message used to send email (string)

Proxy
Member -- Use mailhost service
"""

from random import randint

#Get message
notification_message = context.portal_catalog.getResultValue(portal_type="Notification Message",
                                                             reference=notification_reference)
notification_message_reference = randint(0, 999**9)

active_user_link = "%s/ERP5Site_activeLogin?key=%s" % (context_url,
                                                       notification_message_reference)
mapping_dict = {'user':context.getTitle(),
                'active_user_link': active_user_link,
                }

if notification_message.getContentType() == "text/html":
  mail_text = notification_message.asEntireHTML(
    substitution_method_parameter_dict={'mapping_dict':mapping_dict})
else:
  mail_text = notification_message.asText(
    substitution_method_parameter_dict={'mapping_dict':mapping_dict})

context.portal_notifications.sendMessage(
  recipient=(context,),
  subject=notification_message.getTitle(),
  message=mail_text,
  message_text_format=notification_message.getContentType(),
  notifier_list=('Mail Message',),
  portal_type_list=("Notification Message",),
  store_as_event=True,
  event_keyword_argument_dict={'follow_up':context.getRelativeUrl(), 'reference': notification_message_reference},
)
