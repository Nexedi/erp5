import json

portal = context.getPortalObject()

response = connector.createSession(data=data)

assert "id" in response, response

stripe_payment_session = portal.stripe_payment_session_module.newContent(
  portal_type="Stripe Payment Session",
  reference=response["id"],
  expiration_date=context.getTypeBasedMethod('getStripePaymentSessionExpirationDate')(),
  resource=resource,
  causality=causality
)

http_exchange = portal.system_event_module.newContent(
  portal_type="HTTP Exchange",
  title="Create Session",
  follow_up_value=stripe_payment_session,
  source_value=context,
  resource="http_exchange_resource/stripe/create_session",
  request=json.dumps(data, indent=2),
  response=json.dumps(response, indent=2)
)

http_exchange.confirm()
http_exchange.acknowledge()
stripe_payment_session.open()

if batch_mode:
  return stripe_payment_session

return context.REQUEST.RESPONSE.redirect(response["url"])
