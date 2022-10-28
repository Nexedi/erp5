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
  # don't activate again if there's already a failed activity, to prevent activity failing again and
  # again for the same payment session when something goes wrong.
  if stripe_payment_session.getValidationState() == 'open'\
    and not stripe_payment_session.hasActivity(only_invalid=True):
    stripe_payment_session.activate(
      tag=tag,
    ).StripePaymentSession_checkStripeSessionOpen()
