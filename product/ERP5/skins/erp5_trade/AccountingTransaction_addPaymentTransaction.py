## Script (Python) "AccountingTransaction_addPaymentTransaction"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=folder, id
##title=
##
product = container.manage_addProduct[ 'ERP5' ]

product.addAccountingTransaction(id) 
my_transaction = folder[id]

my_transaction.newContent(portal_type='Accounting Transaction Line',
                          source='account/prestation_service',
                          id='receivable')
my_transaction.newContent(portal_type='Accounting Transaction Line',
                          source='account/achat_pc_storever',
                          id='payable')
my_transaction.newContent(portal_type='Accounting Transaction Line',
                          source='account/banques_etablissements_financiers',
                          id='bank')

return my_transaction
