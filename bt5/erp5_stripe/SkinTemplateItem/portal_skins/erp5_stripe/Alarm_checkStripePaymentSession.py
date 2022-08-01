portal = context.getPortalObject()

active_process = context.newActiveProcess().getRelativeUrl()
connector_url, = [o.getRelativeUrl() for o in portal.portal_catalog(
  portal_type="Stripe Connector",
  reference=context.getTypeBasedMethod('getStripeConnectorReference')(),
  validation_state="validated",
)]

method_id = "StripePaymentSession_checkStripeSessionOpen"

kw = {
  "portal_type": "Stripe Payment Session",
  "validation_state": "open",
}

uid_list = [r.uid
  for r in portal.portal_catalog(**kw)
  if portal.portal_activities.countMessage(
    method_id=method_id,
    path=r.path) == 0
]

if not uid_list:
  return

kw["uid"] = uid_list

method_kw = {
  "active_process": active_process,
  "connector_url": connector_url,
}

if params and "bypass_uid" in params:
  method_kw["bypass_uid"] = params["bypass_uid"]

portal.portal_catalog.searchAndActivate(
  method_id=method_id,
  method_kw=method_kw,
  **kw
)
