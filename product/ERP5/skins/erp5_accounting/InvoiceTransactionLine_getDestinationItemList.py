## Script (Python) "InvoiceTransactionLine_getDestinationItemList"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
from Products.ERP5Type.Cache import CachingMethod

category_dict = {'income': 'portal_categories/account_type/expense',
                 'expense': 'portal_categories/account_type/income',
                 'payable': 'portal_categories/account_type/asset/receivable',
                 'receivable': 'portal_categories/account_type/liability/payable',
                 'collected_vat': 'portal_categories/account_type/asset/receivable/refundable_vat',
                 'refundable_vat': 'portal_categories/account_type/liability/payable/collected_vat',
                 'bank': 'portal_categories/account_type/asset/cash',
                 }

if context.id in category_dict:
  category = category_dict[context.id]
else:
  category = 'portal_categories/account_type'

display_dict = {}
def display(x):
  if x not in display_dict:
    pcg_id = x.getPcgId()
    account_title = x.getTitle()
    display_dict[x] = "%s - %s" % (pcg_id, account_title)
  return display_dict[x]

def sort(x,y):
  return cmp(display(x), display(y))

def getItemList(category=None):
  obj = context.restrictedTraverse(category)
  item_list = obj.getCategoryMemberItemList(portal_type='Account', base=0,
                                            display_method=display, sort_method=sort)
  return item_list

getItemList = CachingMethod(getItemList, id=('getInvoiceTransactionLineItemList', 'getItemList'))
return getItemList(category=category)
