from erp5.component.module.Log import log
# Reindex objects which indexation_timestamp is at most
# delta seconds before current time (ie, bound inclued).
# Unindex objects which cannot be found.
# Default delta is 172800 (=2*24*60*60=2 days)

portal = context.getPortalObject()
catalog = portal.portal_catalog.getSQLCatalog()
candidate_list = context.ERP5Site_zGetLatestIndexedObjectList(delta=delta)

reindex_count = 0
unindex_count = 0

row_count = len(candidate_list)
for i, candidate in enumerate(candidate_list):
  path = candidate['path']
  try:
    obj = portal.restrictedTraverse(path)
  except KeyError:
    # Object is unreachable, remove it from catalog
    # Use SQLQueue because all activities are triggered on the same object,
    # and SQLDict keeps only one.
    catalog.activate(activity="SQLQueue").uncatalogObject(uid=candidate['uid'])
    unindex_count += 1
  else:
    obj.reindexObject()
    reindex_count += 1
  if i % 1000 == 0:
    log('processed %i/%i lines' % (i, row_count))

message = '%s object reindexed, %s object unindexed' % (reindex_count, unindex_count)
log(message)
return message
