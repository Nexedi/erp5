## Script (Python) "AccountingTransactionModule_statSourceCredit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=**kw
##title=
##
kw['selection_params'] = kw
kw['section_category'] = kw.get('section_category', 'group/nexedi')
kw['stat'] = 1
kw['omit_output'] = 1

result = context.AccountingTransactionModule_zGetAccountingTransactionList(**kw)
row = result[0]
return '%.02f' % (row.quantity or 0.0)
