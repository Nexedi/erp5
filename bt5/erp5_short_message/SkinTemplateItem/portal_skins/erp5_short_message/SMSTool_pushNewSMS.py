"""Create new SMS from a push of the sms gateway
Parameter:
message_id -- Reference of the message in gateway side (String)
sender -- Phone number of the sender (String)
recipient -- Phone number of the recipient (String)
text_content -- the message (String)
message_type -- Type of message (String)
reception_date -- The date when the message was received (DateTime)"""
#XXX-Should be replace by portal_contribution
module = context.getDefaultModule("Short Message")
event = module.newContent(portal_type="Short Message",
                   sender=sender,
                   recipient=recipient,
                   content_type=message_type,
                   text_content=text_content,
                   start_date=reception_date,
    #XXX-Fx : See with JPS for a new event implementation
    #XXX-Fx : DestinationReference property must be replace by a category
                   destination_reference=message_id,
                   )

#Mark the message as received
event.receive()

#Search sender and recipient
def searchParentOfTelephoneNumber(phone_number):
  getResultValue = context.portal_catalog.getResultValue

  phone = getResultValue(url_string={'query':phone_number, 'key':'ExactMatch'}, portal_type='Telephone', parent_portal_type='Person')
  if phone is None:
    phone = getResultValue(url_string={'query':phone_number, 'key':'ExactMatch'}, portal_type='Telephone', parent_portal_type='Organisation')
  if phone is not None:
    return phone.getParentValue()

  return None

event.setSourceValue(searchParentOfTelephoneNumber(sender))
event.setDestinationValue(searchParentOfTelephoneNumber(recipient))
event.setGateway(context.getRelativeUrl())
#context.log("new SMS added at %s" % event.getRelativeUrl())
