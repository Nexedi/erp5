"""Update modification date of the ticket when posting a new event, on tickets where this makes sense.
Typically, we do this on "small tickets focusing on one thing", such as support requests or bugs, but
not, for example, on campaigns.
"""
event = sci['object']

ticket = event.getFollowUpValue()
if ticket is not None:
  afterNewEvent = ticket.getTypeBasedMethod('afterNewEvent')
  if afterNewEvent:
    afterNewEvent(event)
