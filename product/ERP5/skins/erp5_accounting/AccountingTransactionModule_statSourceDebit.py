## Script (Python) "AccountingTransactionModule_statSourceDebit"
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
kw['omit_input'] = 1

result = context.AccountingTransactionModule_zGetAccountingTransactionList(**kw)
row = result[0]
return '%.02f' % (row.quantity and - row.quantity or 0.0)
