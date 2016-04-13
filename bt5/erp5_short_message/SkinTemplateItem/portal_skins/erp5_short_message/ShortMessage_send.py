"""
  Send the current sms by using a SMS gateway.
  Use default mobile phone of source and destination
"""

#Get recipients
if not to_url:
  recipient_phone_list = [person.getDefaultMobileTelephoneValue() for person in context.getDestinationValueList()]
  if None in recipient_phone_list:
    raise ValueError("All recipients should have a default mobile phone")

  to_url = [phone.asURL() for phone in recipient_phone_list]
  if None in to_url:
    raise ValueError("All recipients should have a valid default mobile phone number")

#Get sender
if not from_url:
  if context.getSourceValue():
    sender_phone = context.getSourceValue().getDefaultMobileTelephoneValue()
    if not sender_phone:
      raise ValueError("The sender(%s) should have a default mobile phone" % context.getSourceValue())
    #We use title of sender
    from_title = sender_phone.getTitle()
    from_url = sender_phone.asURL()

if not body:
  body = context.getTextContent()

if not context.getStartDate():
  context.setStartDate(DateTime())

context.portal_sms.activate(
  activity="SQLQueue",
  # We do not retry these activities not to send SMS multiple times
  max_retry=0,
  conflict_retry=False,
).send(
  text=body,
  recipient=to_url,
  sender=from_url,
  sender_title=from_title,
  message_type="MULTITEXT",
  test=download,
  document_relative_url=context.getRelativeUrl(),
  **kw)
