## Script (Python) "Folder_addSaleInvoice"
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

context.portal_types.constructContent(type_name= 'Sale Invoice Transaction Line',
                           container=my_transaction,
                           id='income')
context.portal_types.constructContent(type_name= 'Sale Invoice Transaction Line',
                           container=my_transaction,
                           id='receivable')
context.portal_types.constructContent(type_name= 'Sale Invoice Transaction Line',
                           container=my_transaction,
                           id='collected_vat')
income=my_transaction.income
receivable=my_transaction.receivable
collected_vat=my_transaction.collected_vat

return my_transaction
