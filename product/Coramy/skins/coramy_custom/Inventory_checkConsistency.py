## Script (Python) "Inventory_checkConsistency"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
olist = list(context.inventaire_mp.objectValues()) + list(context.inventaire_pf.objectValues())

for o in olist:
 for l in o.objectValues(spec=('CORAMY Inventory Line','ERP5 Inventory Line')):
  if l.hasCellContent():
    for c in l.objectValues(spec=('CORAMY Inventory Cell','ERP5 Inventory Cell')):
      inventory = getattr(c, 'inventory', 0.0) # We have no acquisition here (None at class level ?)
      line_inventory = getattr(l, 'inventory', 0.0)
      if line_inventory is None: line_inventory = 0.0
      if inventory == 0.0 and line_inventory != 0.0 and len(l.objectValues(spec=('CORAMY Inventory Cell','ERP5 Inventory Cell'))) == 1:
        print "Fixing Error on %s" % c.getRelativeUrl()
        c.edit(inventory = line_inventory, force_update =1 )

return printed
