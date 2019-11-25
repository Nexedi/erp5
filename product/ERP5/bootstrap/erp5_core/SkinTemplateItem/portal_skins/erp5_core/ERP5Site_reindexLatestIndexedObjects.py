# Reindex objects which indexation_timestamp is at most
# delta seconds before current time (ie, bound inclued).
# Unindex objects which cannot be found.
# Default delta is 172800 (=2*24*60*60=2 days)

portal = context.getPortalObject()
catalog = portal.portal_catalog.getSQLCatalog()
candidate_list = context.ERP5Site_zGetLatestIndexedObjectList(delta=delta)

reindex_count = 0
unindex_count = 0

for candidate in candidate_list:
  path = candidate['path']
  try:
    obj = portal.restrictedTraverse(path)
  except KeyError:
    # Object is unreachable, remove it from catalog
    # Use SQLQueue because all activities are triggered on the same object,
    # and SQLDict keeps only one.
    catalog.activate(activity="SQLQueue").unindexObject(uid=candidate['uid'])
    unindex_count += 1
  else:
    obj.reindexObject()
    reindex_count += 1

print '%s object reindexed, %s object unindexed' % (reindex_count, unindex_count)
return printed
