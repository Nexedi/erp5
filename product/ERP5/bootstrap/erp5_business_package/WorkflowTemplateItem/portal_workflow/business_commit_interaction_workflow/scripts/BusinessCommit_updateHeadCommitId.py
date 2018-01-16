modified = state_change['object']
site = context.getPortalObject()
portal_commits = site.portal_commits

# If the state of modified commit is commited, then update the value of HEAD
# commit ID
if modified.getValidationState() == 'commited':
  portal_commits.setHeadCommitId(modified.getId())
