# Check if the conext is Commit Tool
if context.getPortalType() != 'Commit Tool':
  return 'context is not commit tool'

# Get the HEAD commit and create a snapshot based on it
head_commit = context.getHeadCommit()

# Create a new snapshot based on HEAD commit
snapshot = head_commit.createEquivalentSnapshot()

return context.Base_redirect('view')
