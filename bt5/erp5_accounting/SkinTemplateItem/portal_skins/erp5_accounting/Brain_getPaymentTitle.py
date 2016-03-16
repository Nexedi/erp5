request = container.REQUEST
payment_title = ''
try:
  return request.other[context.payment_uid]
except KeyError:
  if context.payment_uid:
    payment = context.getPortalObject().portal_catalog.getobject(context.payment_uid)
    if payment is not None:
      payment_title = payment.getTitle()
  
request.other[context.payment_uid] = payment_title
return payment_title
