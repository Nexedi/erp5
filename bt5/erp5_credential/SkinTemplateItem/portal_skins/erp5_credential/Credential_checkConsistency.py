"""Check credential consistency. Usefull before make some actions
By default, just a related person is required, please override this script if you want more.
Parameter:
destination_decision_type - List of portal type required in destination decision value list
Proxy:
Assignee -- allow to check credential informations"""

for portal_type in destination_decision_type:
  destination = context.getDestinationDecisionValue(portal_type=portal_type)
  if destination is None:
    raise ValueError('%s request must  be in relation with a %s' % (context.getPortalType(),portal_type))
