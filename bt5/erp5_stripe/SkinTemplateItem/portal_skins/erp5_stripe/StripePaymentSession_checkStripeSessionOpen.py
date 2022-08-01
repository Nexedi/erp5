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

http_exchange = context.StripePaymentSession_retrieveSession(
  web_service,
  batch_mode=True
)

response = json.loads(http_exchange.getResponse())
if "error" in response:
  if response["error"]["type"] == "invalid_request_error":
    context.expire()
    return
  else:
    raise ValueError("Unexpected type in %s" % response)

assert response["object"] == "checkout.session", "Unexpected Stripe Object"
assert response["id"] == context.getReference(), "Unexpected Stripe ID"

if response["status"] == "expired":
  context.expire()
elif response["status"] == "complete":
  context.complete()
else:
  context.setExpirationDate(
    context.getTypeBasedMethod('getStripePaymentSessionExpirationDate')()
  )
