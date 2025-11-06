portal = context.getPortalObject()

preference_key = "preferred_accounting_transaction_default_%s_account" % context.getId()
preferred_default_account = portal.portal_preferences.getPreference(preference_key, None)

if preferred_default_account is None:
  return

if context.getPortalType() == "Purchase Invoice Transaction":
  context.setDestination(preferred_default_account)
else:
  context.setSource(preferred_default_account)
