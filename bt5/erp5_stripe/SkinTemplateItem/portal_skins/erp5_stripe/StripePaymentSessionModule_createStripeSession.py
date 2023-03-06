import json

response = connector.createSession(data=data)
assert "id" in response, response

context.activate().StripePaymentSessionModule_storeStripeSession(
  reference=response["id"],
  expiration_date=context.getTypeBasedMethod('getStripePaymentSessionExpirationDate')(),
  resource=resource,
  source=connector.getRelativeUrl(),
  causality=causality,
  request=json.dumps(data, indent=2),
  response=json.dumps(response, indent=2)
)

return context.REQUEST.RESPONSE.redirect(response["url"])
