import json

# ignore if SPS is not open or not expired yet
if context.getValidationState() != "open" or \
    context.getExpirationDate() > DateTime():
  return

assert connector_url not in (None, ""), connector_url

portal = context.getPortalObject()

web_service = portal.restrictedTraverse(
  connector_url
)

assert web_service.getPortalType() == "Stripe Connector", \
  "Unexpected connector %s" % connector_url


activity_tag = context.StripePaymentSession_generateActivityTag()
with context.defaultActivateParameterDict({'tag': activity_tag}, placeless=True):
  http_exchange = context.StripePaymentSession_retrieveSession(
    web_service,
    batch_mode=True
  )

  response = json.loads(http_exchange.getResponse())

  if "error" in response and response["error"]["type"] == "invalid_request_error":
    raise ValueError("Error to check %s" % context.getRelativeUrl())

  assert response["object"] == "checkout.session", "Unexpected Stripe Object"
  assert response["id"] == context.getReference(), "Unexpected Stripe ID"

# allow custom projects create workflow interactions that wait catalog to index http exchange
with context.defaultActivateParameterDict({'after_tag': activity_tag}, placeless=True):
  if response["status"] == "expired":
    context.expire()
  elif response["status"] == "complete":
    context.complete()
  else:
    context.setExpirationDate(
      context.getTypeBasedMethod('getStripePaymentSessionExpirationDate')()
    )
