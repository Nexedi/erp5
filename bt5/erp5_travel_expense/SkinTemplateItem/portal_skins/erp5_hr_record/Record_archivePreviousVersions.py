from Products.ZSQLCatalog.SQLCatalog import SimpleQuery

record = context
search_kw = {
  'portal_type': record.getPortalType(),
  'strict_follow_up_uid': record.getFollowUpUid(),
  'simulation_state': "stopped",
  # exclude current workflow changed document
  'uid': SimpleQuery(uid=record.getUid(), comparison_operator='!='),
}

# We can now archive all previous records
for old_document in context.getPortalObject().portal_catalog(**search_kw):
  old_document = old_document.getObject()
  if old_document.getSimulationState() in ("stopped"):
    old_document.deliver()
