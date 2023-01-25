portal = context.getPortalObject()
accounting_module = portal.accounting_module

from_date=DateTime(context.getStartDate().year(), 1, 1)
to_date=context.getStartDate()

search_params = \
  {
   'portal_type'         : 'Pay Sheet Transaction',
   'delivery.start_date' : {'range': "minmax", 'query': (from_date, to_date)},
   'delivery.source_section_uid' : context.getSourceSectionUid(),
   'delivery.destination_section_uid' : context.getDestinationSectionUid(),
   'simulation_state'    : ['confirmed', 'stopped', 'delivered'],
  }

paysheet_list = accounting_module.searchFolder( **search_params)

nb_heures_supp = 0
for paysheet in paysheet_list:
  nb_heures_supp += paysheet.PaySheetTransaction_getMovementQuantityFromCategory(
    'base_contribution/base_amount/payroll/report/overtime')

return nb_heures_supp
