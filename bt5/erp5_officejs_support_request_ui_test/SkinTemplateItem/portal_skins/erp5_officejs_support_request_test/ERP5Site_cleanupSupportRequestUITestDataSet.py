"""Cleanup the data from support request module.

So that test are isolated.
"""
from Products.ZSQLCatalog.SQLCatalog import Query, NegatedQuery
portal = context.getPortalObject()
test_project_set = set((
    portal.project_module.erp5_officejs_support_request_ui_test_project_001,
    portal.project_module.erp5_officejs_support_request_ui_test_project_002))

to_delete_list = []
for brain in portal.portal_catalog(
    portal_type="Support Request",
    simulation_state=NegatedQuery(Query(simulation_state=("cancelled",)))):
  support_request = brain.getObject()
  if support_request.getId().startswith('erp5_officejs_support_request_ui_test_'):
    continue # business template data
  assert support_request.getSourceProjectValue() in test_project_set, \
     "Support request %s have unexpected project." % support_request.absolute_url()
  to_delete_list.append(support_request.getId())
portal.support_request_module.manage_delObjects(to_delete_list)

# Clear worklist cache
portal.portal_caches.clearAllCache()

return "Done."
