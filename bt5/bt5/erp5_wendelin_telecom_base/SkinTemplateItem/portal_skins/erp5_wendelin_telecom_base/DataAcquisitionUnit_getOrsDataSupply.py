'''
Return the pre-configured Data Supply related to a Data Acquisition Unit representing an ORS.

If the Data Acquisition Unit or the Data Supply do not fit the expected ORS format, return None.

In the unexpected event several matching Data Supplies exist, return the oldest one, as it is
most likely to be the one created by the ORS registration process.
'''

if context.getReference() is None:
  return None
ors_tag = context.getReference()

portal = context.getPortalObject()

data_supply_list = portal.data_supply_module.searchFolder(
  portal_type='Data Supply',
  reference=ors_tag,
  validation_state='validated'
)
data_supply_url_list = [
  data_supply.getRelativeUrl() for data_supply in data_supply_list
]

related_data_supply_list = []
for data_supply_line in context.Base_getRelatedObjectList(
  portal_type='Data Supply Line',
  validation_state='validated'
):
  # Be sure to only fetch Data Supplies the user has access to
  data_supply_url = data_supply_line.getParentRelativeUrl()
  if data_supply_url in data_supply_url_list:
    related_data_supply_list.append(portal.restrictedTraverse(data_supply_url))

if not related_data_supply_list:
  return None

# Several related Data Supplies have the expected reference: unexpected
# Return the one that was created first
related_data_supply_list.sort(key=lambda x: x.getCreationDate())

return related_data_supply_list[0]
