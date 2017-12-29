modified = state_change['object']
site = context.getPortalObject()

if modified.getValidationState() == 'commited':
  # Get all Business Manager which are affected by this commit
  bt_list = list(set([item for sublist
                      in [l.getFollowUpValueList()
                      for l in modified.objectValues()]
                      for item in sublist]))

# Now update the status of all Business Template to 'available'
for bt in bt_list:
  if site.portal_workflow.isTransitionPossible(
    bt, 'exhibit'):
    bt.exhibit()
