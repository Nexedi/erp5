## Script (Python) "Invoice_addSaleInvoice"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=folder, id
##title=
##
product = container.manage_addProduct[ 'ERP5' ]

product.addInvoice(id) 
my_transaction = folder[id]

my_transaction.newContent(portal_type='Sale Invoice Transaction Line',
                          source='account/ventes_composants_storever',
                          id='income')
my_transaction.newContent(portal_type='Sale Invoice Transaction Line',
                          source='account/prestation_service',
                          id='receivable')
my_transaction.newContent(portal_type='Sale Invoice Transaction Line',
                          source='account/tva_collectee_196',
                          id='collected_vat')

return my_transaction
