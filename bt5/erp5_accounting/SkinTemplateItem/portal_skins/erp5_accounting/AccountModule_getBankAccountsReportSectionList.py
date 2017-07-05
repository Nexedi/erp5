"""
Bank accounts.
"""

from Products.ERP5Form.Report import ReportSection

request = context.REQUEST
to_date = request['to_date']
transaction_section_category = request['transaction_section_category']
transaction_simulation_state = request['transaction_simulation_state']
from_date = request.get('from_date', None)

result = []
params =  {
    'to_date': to_date,
    'section_category': transaction_section_category,
    'simulation_state': transaction_simulation_state,
    'accounting_transaction_line_currency': None,
    'report_depth': 5
}

if from_date:
  params['from_date'] = from_date

groupCategory = context.portal_categories.restrictedTraverse(transaction_section_category)
entities = groupCategory.getGroupRelatedValueList(portal_type = ('Organisation', 'Person'))

entity_columns = (
    ('title', 'Title'),
    ('getStopDate', 'Date'),
    ('reference', 'Invoice No'),
    ('getDestinationSectionTitle', 'Third Party'),
    ('source_reference', 'Reference'),
    ('simulation_state', 'State'),
    ('source_debit', 'Debit'),
    ('source_credit', 'Credit'),
    ('source_balance', 'Balance'),
)

for entity in entities :
  result.append(
      ReportSection(
          path=context.getPhysicalPath(),
          title='Bank accounts for %s'%entity.getTitle(),
          level=1,
          form_id=None) )

  for bank in entity.searchFolder(portal_type='Bank Account'):
    o = bank.getObject()
    result.append(
        ReportSection(
            title='%s (%s)'%(o.getTitle(), entity.getTitle()),
            level=2,
            path=o.getPhysicalPath(),
            form_id='BankAccount_viewAccountingTransactionList',
            ##  XXX Here we must use accounting_selection, because stat scripts read this selection
            selection_name = 'accounting_selection',
            selection_params = params,
            selection_columns = entity_columns,))

return result
