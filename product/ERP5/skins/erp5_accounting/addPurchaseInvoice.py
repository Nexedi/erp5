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
                           id='l0')
context.portal_types.constructContent(type_name= 'Purchase Invoice Transaction Line',
                           container=my_transaction,
                           id='l1')
context.portal_types.constructContent(type_name= 'Purchase Invoice Transaction Line',
                           container=my_transaction,
                           id='l2')
fournisseur=my_transaction.l0
charge=my_transaction.l1
tva=my_transaction.l2

#fournisseur.setSource('account/capital')

return my_transaction
