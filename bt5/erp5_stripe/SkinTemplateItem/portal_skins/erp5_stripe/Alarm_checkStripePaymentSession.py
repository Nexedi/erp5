portal = context.getPortalObject()

portal.portal_catalog.searchAndActivate(
  portal_type="Stripe Payment Session",
  validation_state="open",
  expiration_date={
    'query': DateTime(),
    'range': 'ngt',
  },
  method_id='StripePaymentSession_checkStripeSessionOpen',
  activate_kw={'tag': tag}
)

context.activate(after_tag=tag).getId()
