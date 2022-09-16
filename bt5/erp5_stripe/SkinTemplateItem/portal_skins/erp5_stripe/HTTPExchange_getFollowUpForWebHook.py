import json
response = json.loads(context.getResponse())
assert response["object"] == "event", "Unexpected %s" % response
assert "data" in response
data = response["data"]["object"]
session_id = data["id"]
stripe_payment_session, = context.getPortalObject().portal_catalog(
  portal_type="Stripe Payment Session",
  reference=session_id,
  limit=2)

context.setFollowUpValue(stripe_payment_session.getObject())
