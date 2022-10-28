import json
from Products.ERP5Type.Message import translateString

# ignore if SPS is not open or already had an error
if context.getValidationState() != "open" or context.hasErrorActivity():
  return

web_service = context.getSourceValue(portal_type="Stripe Connector")

assert web_service is not None, \
  "Connector not found in %s" % context.getRelativeUrl()

http_exchange = context.StripePaymentSession_retrieveSession(
  web_service, batch_mode=True)

response = json.loads(http_exchange.getResponse())

if "error" in response and response["error"][
    "type"] == "invalid_request_error":
  raise ValueError("Error to check %s" % context.getRelativeUrl())

assert response["object"] == "checkout.session", "Unexpected Stripe Object"
assert response["id"] == context.getReference(), "Unexpected Stripe ID"

if response["status"] == "expired":
  context.expire(
    comment=translateString(
      'Expired after ${http_exchange_id}',
      mapping={'http_exchange_id': http_exchange.getId()}))
elif response["status"] == "complete":
  # When completing, we pass the payment status as kwargs to the workflow
  # method, so that higher level code can access the state an interaction
  # workflow wrapping `complete` method, typically to create a payment
  # transaction when the payment was successful or notify customer when it
  # was not.
  context.complete(
    payment_status=response["payment_status"],
    comment=translateString(
      'Completed ${payment_status} after ${http_exchange_id}',
      mapping={
        "payment_status": response["payment_status"],
        "http_exchange_id": http_exchange.getId()}))
else:
  assert response["status"] == "open"
  context.setExpirationDate(
    context.getTypeBasedMethod('getStripePaymentSessionExpirationDate')())
