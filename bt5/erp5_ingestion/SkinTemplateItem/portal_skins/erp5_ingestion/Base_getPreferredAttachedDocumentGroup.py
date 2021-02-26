"""
  Return the default group relative url to be added in the
  document uploaded when attaching document using Base_viewNewFileDialog
"""
portal = context.getPortalObject()
group = context.getProperty('group')
if not group:
  user = portal.portal_membership.getAuthenticatedMember().getUserValue()
  if user is not None:
    group = user.getGroup()

return group
