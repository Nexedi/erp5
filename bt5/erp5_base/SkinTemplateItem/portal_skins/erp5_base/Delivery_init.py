if context.hasLedger():
  return
elif kw.get('ledger', None) is not None:
  context.setLedger(kw.get('ledger'))
else:
  portal_type_id = context.getPortalType()
  portal_type = context.getPortalObject().portal_types.get(portal_type_id, None)
  if portal_type:
    context.setLedger(portal_type.getDefaultLedger(None))
