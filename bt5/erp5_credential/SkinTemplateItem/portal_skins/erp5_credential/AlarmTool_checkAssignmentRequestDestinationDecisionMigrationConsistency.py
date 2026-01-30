portal = context.getPortalObject()
from Products.ZSQLCatalog.SQLCatalog import SimpleQuery
result_list = []


migration_kw = {
  'portal_type': ['Assignment Request'],
  'destination__uid': '%',
  'destination_decision_uid': SimpleQuery(destination_decision_uid=None)
}

non_migrated_assignment_request = portal.portal_catalog(limit=1, **migration_kw)
if len(non_migrated_assignment_request) == 1:
  result_list.append("all X needs updates %s" % non_migrated_assignment_request[0].getRelativeUrl())
  if fixit:
    portal.portal_catalog.searchAndActivate(
      activate_kw=dict(priority=5,
                       tag=script.getId(),
                       after_method_id=('immediateReindexObject',
                                        'recursiveImmediateReindexObject')),
      method_id='fixConsistency',
      **migration_kw)
return result_list
