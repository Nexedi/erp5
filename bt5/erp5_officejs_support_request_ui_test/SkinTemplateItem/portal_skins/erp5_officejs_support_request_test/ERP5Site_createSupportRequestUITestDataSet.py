"""Create some data for support request UI test.

Logged in user needs to be Assignee / Assignor on the support requests
included in business template.
"""
portal = context.getPortalObject()

for support_request in portal.support_request_module.contentValues():
  if support_request.getId().startswith('erp5_officejs_support_request_ui_test'):
    support_request.manage_addLocalRoles(
        portal.portal_membership.getAuthenticatedMember().getId(),
        ['Assignee', 'Assignor'])
    support_request.reindexObject()

portal.portal_caches.clearAllCache()
return "Done."
