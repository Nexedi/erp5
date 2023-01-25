'''
This script will call the PaySheetTransaction_getMovementTotalPriceFromCategory
script to get the year to date summed amount of paysheet lines wich category of
category_list parameter is in variation_category_list of the PaySheet line and
wich has a base_contribution in the base_contribution_list
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
    'simulation_state'    : ['confirmed', 'stopped', 'delivered']
}

paysheet_list = [r.getObject() for r in accounting_module.searchFolder(**search_params)]
paysheet_list.append(context)

yearly_amount = 0.

script_params = {'base_contribution': base_contribution,
                 'contribution_share': contribution_share,
                 'no_base_contribution': no_base_contribution,
                 'include_empty_contribution': include_empty_contribution,
                 'excluded_reference_list': excluded_reference_list}

for paysheet in paysheet_list :
  monthly_amount = paysheet.PaySheetTransaction_getMovementTotalPriceFromCategory(**script_params)
  yearly_amount += monthly_amount

return yearly_amount * -1
