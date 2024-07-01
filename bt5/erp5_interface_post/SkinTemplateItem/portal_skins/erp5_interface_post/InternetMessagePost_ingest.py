"""
From an Internet Message Post, creates a Mail Message (and attachements)
in ERP5.
"""
from Products.ZSQLCatalog.SQLCatalog import SimpleQuery

import email
import six

portal = context.getPortalObject()

if six.PY2:
  message_from_bytes = email.message_from_string
else:
  message_from_bytes = email.message_from_bytes

email_object = message_from_bytes(bytes(context.getData()))

mail_message = portal.portal_contributions.newContent(
  container_path='event_module',
  filename='internet_message_post_ingestion.eml',
  data=context.getData(),
)
mail_message.setAggregateValue(context)

strict_causality_reference = context.stripMessageId(email_object['in-reply-to'])

if strict_causality_reference:
  causality_post_result_list = portal.internet_message_post_module.searchFolder(
    portal_type=context.getPortalType(),
    query=SimpleQuery(reference=strict_causality_reference),
  )
  if len(causality_post_result_list) == 1:
    causality_event = causality_post_result_list[0].getAggregateRelatedValue()
    mail_message.setCausalityValue(causality_event)
    # If causality has a follow up (ie: on a Support Request), then they most
    # likely share the same follow up
    mail_message.setDefaultFollowUp(causality_event.getDefaultFollowUp())

mail_message.stop()

return [mail_message,]
