'''
  this script return the total price of the base contribution list
  from the first of january of the year of the paysheet and until
  the start_date of this current paysheet. Return 0.0 if there is no amount.
'''

# XXX-Aurel : this script is currently not working as paysheet transaction line/cell
# are not in stock table due to the lack of source/destination definition

if paysheet is None:
  paysheet = context

# test the list parameters
if base_contribution_list is None:
  base_contribution_list = []
elif not (same_type(base_contribution_list, []) or
          same_type(base_contribution_list, ())):
  base_contribution_list = [base_contribution_list]

portal = context.getPortalObject()
portal_simulation = portal.portal_simulation

base_amount = portal.portal_categories.base_amount

base_contribution_uid_list = []
for category in base_contribution_list:
  category_value = base_amount.restrictedTraverse(category)
  if category_value is None:
    raise ValueError('Category "%s/%s" not found.' % (base_amount.getPath(), category))
  base_contribution_uid_list.append(category_value.getUid())

params = {
    'node_uid' : paysheet.getSourceSectionUid(),
    'mirror_section_uid' : paysheet.getSourceSectionUid(),
    'section_uid' : paysheet.getDestinationSectionUid(),
    'contribution_share_uid' :\
        portal.portal_categories.contribution_share.employee.getUid(),
    'to_date' : paysheet.getStartDate(),
    'from_date' : DateTime(paysheet.getStartDate().year(), 1, 1),
    'simulation_state'    : ['stopped', 'delivered'],
    'precision' : paysheet.getPriceCurrencyValue().getQuantityPrecision(),
    'parent_base_contribution_uid' : base_contribution_uid_list,
    'src__' : src__,
  }

return portal_simulation.getInventoryAssetPrice(**params)
