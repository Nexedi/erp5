# Check if the conext is Commit Tool
if context.getPortalType() != 'Commit Tool':
  return 'context is not commit tool'

# Check if the last created sub-object in Commit Tool is a commit and is not
# raise an Error
last_obj = max(context.objectValues(), key=(lambda x: x.getCreationDate()))

if last_obj.getPortalType() != 'Business Commit':
  raise ValueError('You are trying to generate a new snapshot via Commit Tool but there \
are no commits added after last snapshot. Add a commit and try again.')

# Create a new snapshot based on last commit
snapshot = last_obj.createEquivalentSnapshot()

return context.Base_redirect('view')
