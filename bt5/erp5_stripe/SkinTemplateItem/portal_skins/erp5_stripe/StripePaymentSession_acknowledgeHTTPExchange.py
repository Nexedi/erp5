# Proxy role: assignor
"""
 We set Stripe Payment Session as follow up to the HTTP exchange and when we set it,
 HTTPExchange_setFollowUpAndInquiry will fail after to every http exchange related to Stripe Pyament Sessions

 In some cases, we need proxy role to call acknowledge. Then, to avoid proxy roles in big scripts,
 we create a very strict strict with the proxy role
"""
assert http_exchange.getPortalType() == "HTTP Exchange", "Unexpected object %s" % http_exchange
assert http_exchange.getFollowUp() == context.getRelativeUrl(), "context (%s) must be set as follow up %s" % context
http_exchange.acknowledge()
