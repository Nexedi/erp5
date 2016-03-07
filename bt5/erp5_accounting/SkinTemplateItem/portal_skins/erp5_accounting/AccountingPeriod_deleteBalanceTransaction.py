assert context.getSimulationState() == 'started' and context.getPortalType() == 'Accounting Period'
id_list = []
for balance_transaction in context.getCausalityRelatedValueList(
                     portal_type='Balance Transaction'):
  id_list.append(balance_transaction.getId())
  assert balance_transaction.getParentValue().getId() == 'accounting_module'

if id_list:
  balance_transaction.getParentValue().manage_delObjects(id_list)
