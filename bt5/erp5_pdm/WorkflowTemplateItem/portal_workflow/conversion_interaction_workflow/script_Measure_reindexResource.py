resource = state_change['object'].getResourceValue()
if len(context.portal_catalog(uid=resource.getUid())) > 0:
  # Reindex resource only when resource is not unindexed.
  resource.reindexObject()
