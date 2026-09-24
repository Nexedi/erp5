artificial_task = context
portal = artificial_task.getPortalObject()
user = portal.portal_membership.getAuthenticatedMember().getUserValue()
if user:
  artificial_task.setContributorValue(user)
