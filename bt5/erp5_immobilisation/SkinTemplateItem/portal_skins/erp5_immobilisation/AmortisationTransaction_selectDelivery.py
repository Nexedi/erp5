kw = { 'portal_type':'Amortisation Transaction',
       'simulation_state': context.getPortalUpdatableAmortisationTransactionStateList() }

return_list = [line.getObject() for line in context.portal_catalog(**kw)]
#for line in return_list:
#  t = line.getObject()
#context.log('return_list',return_list)
return return_list
