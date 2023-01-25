# Auto-fill mirror accounts in transaction lines automatically, if necessary.
portal = context.getPortalObject()
movement_data_list = []
has_source = False
has_destination = False
for movement in context.contentValues(portal_type=portal.getPortalAccountingMovementTypeList()):
  source_account = movement.getSourceValue(portal_type='Account')
  destination_account = movement.getDestinationValue(portal_type='Account')
  if source_account is not None:
    has_source = True
  if destination_account is not None:
    has_destination = True
  # Interested in movements which lack one side only.
  if (source_account is not None) ^ (destination_account is not None):
    movement_data_list.append((movement, source_account, destination_account))

# If both are true or we have an internal invoice, mirror accounting is used
if (has_source and has_destination) or\
     context.getPortalType() == 'Internal Invoice Transaction':
  for movement, source_account, destination_account in movement_data_list:
    if source_account is None:
      account = destination_account
      base_category = 'source'
    else:
      account = source_account
      base_category = 'destination'

    mirror_account = account.getDefaultDestination()
    if mirror_account:
      movement.setProperty(base_category, mirror_account)
