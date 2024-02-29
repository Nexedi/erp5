'''
  This script get year to date amount for the slice corresponding to slice_path
  of the model.
'''
portal = context.getPortalObject()
accounting_module = portal.accounting_module

from_date=DateTime(context.getStartDate().year(), 1, 1)
to_date=context.getStartDate()

search_params = {
    'portal_type'         : 'Pay Sheet Transaction',
    'delivery.start_date' : {'range': "minmax", 'query': (from_date, to_date)},
    'delivery.source_section_uid' : context.getSourceSectionUid(),
    'delivery.destination_section_uid' : context.getDestinationSectionUid(),
    'simulation_state'    : ['stopped', 'delivered'],
}

paysheet_list = [r.getObject() for r in accounting_module.searchFolder(**search_params)]
paysheet_list.append(context)
yearly_slice_amount = 0

for paysheet in paysheet_list:
  salary = paysheet.PaySheetTransaction_getMovementTotalPriceFromCategory(
        base_contribution=base_contribution,
        contribution_share='contribution_share/employee')
  if slice_path is None:
    yearly_slice_amount += salary
    continue
  model = paysheet.getSpecialiseValue().getEffectiveModel(\
      start_date=paysheet.getStartDate(),
      stop_date=paysheet.getStopDate())
  if model is not None:
    slice_cell = model.getCell(slice_path)
    if slice_cell is None:
      return 0.0
    plafond_max = slice_cell.getQuantityRangeMax()
    plafond_min = slice_cell.getQuantityRangeMin()
    yearly_slice_amount += min(salary, plafond_max) - plafond_min

return yearly_slice_amount
