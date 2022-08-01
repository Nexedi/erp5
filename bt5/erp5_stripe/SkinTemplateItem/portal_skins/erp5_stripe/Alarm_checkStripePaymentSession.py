portal = context.getPortalObject()

active_process = context.newActiveProcess().getRelativeUrl()

connector_url, = [o.getRelativeUrl() for o in portal.portal_catalog(
  portal_type="Stripe Connector",
  reference=context.getTypeBasedMethod('getStripeConnectorReference')(),
  validation_state="validated",
)]

portal.portal_catalog.searchAndActivate(
  method_id='StripePaymentSession_checkStripeSessionOpen',
  method_kw={
    "active_process": active_process,
    "connector_url": connector_url
  },
  portal_type="Stripe Payment Session",
  validation_state="open"
)
