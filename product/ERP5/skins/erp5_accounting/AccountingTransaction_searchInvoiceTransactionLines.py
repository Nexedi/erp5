## Script (Python) "AccountingTransaction_searchInvoiceTransactionLines"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=**kw
##title=
##
sort_dict = { 'income': '\0\0',
              'expense': '\0\0',
              'receivable': '\0\1',
              'payable': '\0\1',
              'collected_vat': '\0\2',
              'refundable_vat': '\0\3' }

def sortInvoiceTransactionLine(a, b):
  a_id = a.getId()
  if a_id in sort_dict:
    a_id = sort_dict[a_id]
  b_id = b.getId()
  if b_id in sort_dict:
    b_id = sort_dict[b_id]
  return cmp(a_id, b_id)

object_list = []

for o in context.searchFolder(**kw):
  obj = o.getObject()
  object_list.append(obj)

object_list.sort(sortInvoiceTransactionLine)
return object_list
