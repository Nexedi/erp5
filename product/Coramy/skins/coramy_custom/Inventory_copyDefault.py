## Script (Python) "Inventory_copyDefault"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
for l in context.objectValues(spec=('CORAMY Inventory Line','ERP5 Inventory Line')):
  if l.hasCellContent():
    for c in l.objectValues(spec=('CORAMY Inventory Cell','ERP5 Inventory Cell')):
      inventory = getattr(c, 'inventory', 0.0) # We have acquisition here
      if inventory is None: inventory=0.0
      print "Update Cell %s %s" % (getattr(c, 'inventory', 0.0), inventory)
      if inventory == 0.0: c.edit(inventory = inventory, force_update=1) # Only update if 0.0
  else:
    inventory = getattr(l, 'inventory', 0.0)
    if inventory is None: inventory=0.0
    print "Update Line %s %s" % (getattr(l, 'inventory', 0.0), inventory)
    if inventory == 0.0: l.edit(inventory = inventory, force_update=1) # Only update if 0.0

return printed
