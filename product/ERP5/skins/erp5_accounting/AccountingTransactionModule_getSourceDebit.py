## Script (Python) "AccountingTransactionModule_getSourceDebit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=brain=None, selection=None, **kw
##title=
##
params = selection.getParams()
kw = {}
kw['section_category'] = params.get('section_category', 'group/nexedi')
kw['stat'] = 1
kw['omit_input'] = 1
kw['transaction'] = context.getUid()

result = context.AccountingTransactionModule_zGetAccountingTransactionList(selection=selection, **kw)
row = result[0]
return '%.02f' % (row.quantity and - row.quantity or 0.0)
