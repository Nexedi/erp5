"""Return a list of dicts describing all immobilised Computer items with their
current net book value, accumulated depreciation, and remaining life.

Call on portal: context.CapexAsset_getReport()
Call with date: context.CapexAsset_getReport(at_date='2027/01/01')
"""
from DateTime import DateTime

portal = context.getPortalObject()
if at_date is not None:
  at_date = DateTime(at_date)

computer_list = portal.portal_catalog(
  portal_type='Computer',
  validation_state='validated',
)

result = []
for brain in computer_list:
  computer = brain.getObject()
  try:
    kw = {}
    if at_date is not None:
      kw['to_date'] = at_date
    periods = computer.getImmobilisationPeriodList(**kw)
    if not periods:
      continue
  except Exception:
    continue

  last_period = periods[-1]
  acquisition_cost = last_period.get('initial_main_price', 0) or 0
  disposal_price = last_period.get('initial_disposal_price', 0) or 0
  duration_months = last_period.get('initial_duration', 0) or 0
  method = last_period.get('initial_method', '')
  start_date = last_period.get('initial_date')
  owner = last_period.get('owner')

  try:
    if at_date is not None:
      nbv = computer.getAmortisationPrice(at_date=at_date)
    else:
      nbv = computer.getAmortisationPrice(at_date=DateTime())
  except Exception:
    nbv = None

  accumulated_depreciation = acquisition_cost - (nbv or acquisition_cost)

  if start_date and duration_months:
    from erp5.component.module.DateUtils import addToDate
    end_date = addToDate(start_date, month=duration_months)
    ref_date = at_date or DateTime()
    remaining_months = int((end_date - ref_date) / 30.44)
    if remaining_months < 0:
      remaining_months = 0
  else:
    end_date = None
    remaining_months = None

  entry = {
    'title': computer.getTitle(),
    'reference': computer.getReference(),
    'relative_url': computer.getRelativeUrl(),
    'acquisition_date': start_date,
    'acquisition_cost': acquisition_cost,
    'disposal_price': disposal_price,
    'depreciation_method': method,
    'duration_months': duration_months,
    'net_book_value': nbv,
    'accumulated_depreciation': accumulated_depreciation,
    'remaining_months': remaining_months,
    'end_date': end_date,
    'owner': owner.getTitle() if owner else None,
    'currency': owner.getPriceCurrency() if owner else None,
  }
  result.append(entry)

return result
