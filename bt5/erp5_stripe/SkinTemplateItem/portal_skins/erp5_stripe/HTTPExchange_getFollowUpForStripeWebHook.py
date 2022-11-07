import json
portal = context.getPortalObject()
response = json.loads(context.getResponse())
assert response["object"] == "event", "Unexpected %s" % response
assert "data" in response
data = response["data"]["object"]
session_id = data["id"]

assert session_id
stripe_payment_session, = portal.portal_catalog(
  portal_type="Stripe Payment Session",
  reference=session_id,
  limit=2,
)

stripe_payment_session = stripe_payment_session.getObject()
tag = '{}:{}'.format(script.getId(), stripe_payment_session.getId())

with stripe_payment_session.defaultActivateParameterDict(
  {'tag': tag},
):
  # set an expiration date in the past so that next alarm run process this payment session
  stripe_payment_session.setExpirationDate(DateTime() - 1)
context.setFollowUpValue(stripe_payment_session)

# activate alarm after the payment session is reindexed
alarm = portal.portal_alarms.check_stripe_payment_session
alarm.activate(queue='SQLQueue', after_tag=tag).activeSense()
