portal = context.getPortalObject()

for brain in portal.portal_catalog(
  portal_type="Stripe Payment Session",
  validation_state="open",
  expiration_date={
    'query': DateTime(),
    'range': 'ngt',
  },
):
  stripe_payment_session = brain.getObject()
  stripe_payment_session.activate(
    tag=tag,
  ).StripePaymentSession_checkStripeSessionOpen()
