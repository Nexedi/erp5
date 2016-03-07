"""Search the event and set it delivered
#XXX-Fx : See with JPS for a new event implementation
#XXX-Fx : DestinationReference property must be replace by a category (multiple reference)
#XXX-FX : Other possibility : use acknowledgment
"""
event = context.portal_catalog.getResultValue(portal_type=portal_type, destination_reference="%"+destination_reference+"%")
if event is not None:
  #All sms must be delivered to set event as delivered
  if event.getQuantity() > 1:
    if event.isDelivered():
      event.setStopDate(delivery_date)
      event.deliver()
