"""Create some data for support request UI test.

 * Logged in user needs to be Assignee / Assignor on the support requests
included in business template.
 * Some "static" data is already in business template, but because the dashboard
display statistics about recent support requests (like "less than 2 days from now"),
we need to generate support requests at a date relative from now.
"""
from DateTime import DateTime
from datetime import timedelta

portal = context.getPortalObject()
now = DateTime().asdatetime()

for support_request in portal.support_request_module.contentValues():
  if support_request.getId().startswith('erp5_officejs_support_request_ui_test'):
    support_request.manage_addLocalRoles(
        portal.portal_membership.getAuthenticatedMember().getId(),
        ['Assignee', 'Assignor'])
    support_request.reindexObject()
portal.portal_caches.clearAllCache()

portal.support_request_module.newContent(
  portal_type='Support Request',
  title="Yesterday - RobotMaking - Submitted",
  start_date=DateTime(now - timedelta(days=1)),
  source_project_value=portal.project_module.erp5_officejs_support_request_ui_test_project_001,
).submit()
portal.support_request_module.newContent(
  portal_type='Support Request',
  title="Yesterday - PlaneMaking - Open",
  start_date=DateTime(now - timedelta(days=1)),
  source_project_value=portal.project_module.erp5_officejs_support_request_ui_test_project_001,
).validate()
portal.support_request_module.newContent(
  portal_type='Support Request',
  title="Last Week - RobotMaking - Open",
  start_date=DateTime(now - timedelta(days=4)),
  source_project_value=portal.project_module.erp5_officejs_support_request_ui_test_project_001,
).validate()
portal.support_request_module.newContent(
  portal_type='Support Request',
  title="Last Week 2 - RobotMaking - Open",
  start_date=DateTime(now - timedelta(days=5)),
  source_project_value=portal.project_module.erp5_officejs_support_request_ui_test_project_001,
).validate()
portal.support_request_module.newContent(
  portal_type='Support Request',
  title="Two Weeks ago - PlaneMaking - Submitted",
  start_date=DateTime(now - timedelta(days=15)),
  source_project_value=portal.project_module.erp5_officejs_support_request_ui_test_project_001,
).submit()

return "Done."
