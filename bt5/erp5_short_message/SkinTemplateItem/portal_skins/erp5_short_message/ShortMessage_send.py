"""
  Send the current sms by using a SMS gateway.
  Use default mobile phone of source and destination
"""

#Get recipients
recipient_phone_list = [
    person.getDefaultMobileTelephoneValue() for person in context.getDestinationValueList()]
if None in recipient_phone_list:
  raise ValueError("All recipients should have a default mobile phone")

to_url = [phone.asURL() for phone in recipient_phone_list]
if None in to_url:
  raise ValueError("All recipients should have a valid default mobile phone number")

body = context.getTextContent()

if not context.getStartDate():
  context.setStartDate(DateTime())

for recipient in context.getDestinationList():
  context.portal_sms.activate(
    activity="SQLQueue",
    # We do not retry these activities not to send SMS multiple times
    max_retry=0,
    conflict_retry=False,
  ).send(
    text=body,
    sender=context.getSource(),
    recipient=recipient,
    document_relative_url=context.getRelativeUrl(),
  )
