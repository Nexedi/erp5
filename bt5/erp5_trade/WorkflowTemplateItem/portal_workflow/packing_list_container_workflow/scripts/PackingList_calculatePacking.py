packing_list = state_change['object']
isTransitionPossible = packing_list.getPortalObject().portal_workflow.isTransitionPossible
if packing_list.isPacked():
  if isTransitionPossible(packing_list, 'pack'):
    packing_list.pack()
else:
  if isTransitionPossible(packing_list, 'miss'):
    packing_list.miss()
