## Script (Python) "AccountingTransaction_getDestinationPaymentItemList"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
def sort(a, b):
  return cmp(a[0], b[0])

item_list = [['', '']]

organisation = context.getDestinationSectionValue()
if organisation is not None:
  bank_account_list = organisation.contentValues(filter={'portal_type': 'Bank Account'})
  for bank_account in bank_account_list:
    url = bank_account.getRelativeUrl()
    label = bank_account.getIban()
    item_list.append([label, url])

item_list.sort(sort)
return item_list
