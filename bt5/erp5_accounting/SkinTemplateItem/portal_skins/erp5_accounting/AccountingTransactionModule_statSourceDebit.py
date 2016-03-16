params = context.portal_selections.getSelectionParamsFor(selection_name)

params['stat'] = 1
params['omit_output'] = 1
params['omit_input'] = 0

if (params.get('operation_date') or {}).get('query'):
  buildSQLQuery = context.portal_catalog.buildSQLQuery
  params['source_section_where_expression'] = buildSQLQuery(
            **{'delivery.start_date': params['operation_date']})['where_expression']
  params['destination_section_where_expression'] = buildSQLQuery(
            **{'delivery.stop_date': params['operation_date']})['where_expression']
  del params['operation_date']

result = context.AccountingTransactionModule_zGetAccountingTransactionList(
                selection=selection, selection_params = params, **params)
row = result[0]
return float('%.02f' % (row.total_price or 0.0))
# vim: syntax=python
