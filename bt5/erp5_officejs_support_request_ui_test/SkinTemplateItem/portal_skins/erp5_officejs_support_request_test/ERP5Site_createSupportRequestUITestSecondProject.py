"""Create a second project for support request UI test.

All support request services can be used on this project.
"""
portal = context.getPortalObject()

portal.project_module.newContent(
  id='erp5_officejs_support_request_test_second_project',
  title='Second Project'
).validate()

return "Done."
