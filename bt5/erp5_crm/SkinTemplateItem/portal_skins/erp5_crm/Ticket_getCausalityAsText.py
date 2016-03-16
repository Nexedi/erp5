event = context.Ticket_getCausalityValue()
if event is not None:
  return event.asText()
