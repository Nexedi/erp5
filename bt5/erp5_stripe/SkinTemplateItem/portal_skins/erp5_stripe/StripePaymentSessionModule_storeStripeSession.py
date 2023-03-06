portal = context.getPortalObject()

stripe_payment_session = portal.stripe_payment_session_module.newContent(
  portal_type="Stripe Payment Session",
  reference=reference,
  expiration_date=expiration_date,
  resource=resource,
  source_value=portal.restrictedTraverse(source),
  causality=causality
)

http_exchange = portal.system_event_module.newContent(
  portal_type="HTTP Exchange",
  title="Create Session",
  follow_up_value=stripe_payment_session,
  resource_value=portal.portal_categories.http_exchange_resource.stripe.create_session,
)

http_exchange.confirm()
http_exchange.acknowledge()
stripe_payment_session.open()
