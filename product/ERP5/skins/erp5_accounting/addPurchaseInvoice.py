## Script (Python) "addPurchaseInvoice"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=folder, id
##title=
##
product = container.manage_addProduct[ 'ERP5' ]

product.addTransaction(id) 
my_transaction = folder[id]

product = my_transaction.manage_addProduct[ 'ERP5' ]

context.portal_types.constructContent(type_name= 'Purchase Invoice Transaction Line',
                           container=my_transaction,
                           id='expense')
context.portal_types.constructContent(type_name= 'Purchase Invoice Transaction Line',
                           container=my_transaction,
                           id='payable')
context.portal_types.constructContent(type_name= 'Purchase Invoice Transaction Line',
                           container=my_transaction,
                           id='collected_vat')
context.portal_types.constructContent(type_name= 'Purchase Invoice Transaction Line',
                           container=my_transaction,
                           id='refundable_vat')
expense=my_transaction.expense
payable=my_transaction.payable
collected_vat=my_transaction.collected_vat
refundable_vat=my_transaction.refundable_vat

return my_transaction
