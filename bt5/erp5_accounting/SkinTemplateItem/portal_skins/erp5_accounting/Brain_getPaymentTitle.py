request = container.REQUEST
payment_title = ''
try:
  return request.other[context.payment_uid]
except KeyError:
  if context.payment_uid:
    brain_list = context.getPortalObject().portal_catalog(uid=context.payment_uid, limit=2)
    if brain_list:
      brain, = brain_list
      payment_title = brain.getObject().getTitle()

request.other[context.payment_uid] = payment_title
return payment_title
