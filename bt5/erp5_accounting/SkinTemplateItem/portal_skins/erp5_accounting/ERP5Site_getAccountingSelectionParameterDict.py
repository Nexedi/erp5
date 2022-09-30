"""Returns all parameters from preferences or selection.

This script gives priority to selection, and if not found in selection, it
tries to get the parameters from preference tool.
All parameters are stored/retrieved in a REQUEST cache, unless ignore_cache
argument is True.

caveats:
  * wants_from_date parameter is not taken into account in the cache.
"""

# do we have a cache already?
if not ignore_cache:
  params_cache = context.REQUEST.other.get(
          'ERP5Site_getAccountingSelectionParameterDict', None)
  if params_cache is not None:
    # return a copy
    return dict(params_cache)

params = {}
selection_params = {}
if selection_name is not None:
  # check if first parameter is used for selection instance
  if not isinstance(selection_name, str):
    context.log('Using selection parameter is deprecated. Please use selection_name instead.')
    selection_name = selection_name.getName()
  selection_params = context.portal_selections.getSelectionParamsFor(selection_name)
elif selection is not None:
  context.log('Using selection parameter is deprecated. Please use selection_name instead.')
  selection_params = selection.getParams()
preference = context.getPortalObject().portal_preferences

from_date = None
if wants_from_date:
  from_date = selection_params.get('from_date',
                preference.getPreferredAccountingTransactionFromDate())
  if from_date :
    params['from_date'] = from_date

at_date = selection_params.get('at_date',
              preference.getPreferredAccountingTransactionAtDate())
if at_date:
  params['at_date'] = at_date.latestTime()

section_category = selection_params.get('section_category',
                 preference.getPreferredAccountingTransactionSectionCategory())
if section_category:
  params['section_uid'] = context.Base_getSectionUidListForSectionCategory(section_category,
                              preference.isPreferredAccountingSectionCategoryStrict())
  currency = context.Base_getCurrencyForSection(section_category)
  # getQuantityPrecisionFromResource is defined on Base, but the portal is not
  # an instance of Base, so we call it on portal_simulation because it is
  # accessible to everyone.
  params['precision'] = context.portal_simulation\
                            .getQuantityPrecisionFromResource(currency)

  # calculate the period_start_date for this section
  # note that reports that precalculate a section_uid but no section_category
  # will have to calculate period_start_date themselves.
  period_start_date = selection_params.get('period_start_date')
  if not period_start_date and (from_date or at_date):
    period_start_date = \
          context.Base_getAccountingPeriodStartDateForSectionCategory(
              section_category=section_category, date=from_date or at_date)
  if period_start_date:
    params['period_start_date'] = period_start_date

# if we have a section uid, it haves priority
section_uid = selection_params.get('section_uid', None)
if section_uid:
  params.pop('section_category', None)
  params['section_uid'] = section_uid

# also if we have an explicit precision key, it has priority
precision = selection_params.get('precision', None)
if precision is not None:
  params['precision'] = precision

# Some reports, such as general ledger, uses different forms with different report
# parameters, we don't want to accidentally fill the cache with mirror_section_uid
# or payment_uid.
if not selection_params.get('no_mirror_section_uid_cache', 0):
  mirror_section_uid = selection_params.get('mirror_section_uid', None)
  if mirror_section_uid:
    params['mirror_section_uid'] = mirror_section_uid

  payment_uid = selection_params.get('payment_uid', None)
  if payment_uid:
    params['payment_uid'] = payment_uid

# Detailed Beginning Balance, from Account Statement
detailed_from_date_summary = selection_params.get('detailed_from_date_summary', None)
if detailed_from_date_summary is not None:
  params['detailed_from_date_summary'] = detailed_from_date_summary

simulation_state = selection_params.get('simulation_state',
             preference.getPreferredAccountingTransactionSimulationStateList())
if simulation_state:
  params['simulation_state'] = simulation_state

ledger = selection_params.get('ledger_uid', None)
if ledger is None:
  portal_categories = context.getPortalObject().portal_categories
  params['ledger_uid'] = [portal_categories.resolveCategory(category).getUid()
      for category in preference.getPreferredAccountingTransactionLedgerList([])]

portal_type = selection_params.get('movement_portal_type', None)
if portal_type:
  params['portal_type'] = portal_type
else:
  parent_portal_type = selection_params.get('parent_portal_type', None)
  if parent_portal_type:
    params['parent_portal_type'] = parent_portal_type

if not ignore_cache:
  context.REQUEST.other['ERP5Site_getAccountingSelectionParameterDict'] = params
return dict(params)
