## Script (Python) "Inventory_launchTissuInventoryBuilder"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
request = context.REQUEST
supplier_list = context.zGetTissuSupplierList()
cr = '\r'
tab = '\t'
report = "Création d'inventaires en cours pour :" + cr

for supplier_item in supplier_list :
  supplier = supplier_item.getObject()
  if supplier is not None :
    supplier.activate().Inventory_tissuInventoryBuilder(supplier_list=[supplier.getTitle(),])
    report += supplier.getTitle()+cr

return report
