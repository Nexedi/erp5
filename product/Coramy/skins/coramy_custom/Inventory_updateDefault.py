## Script (Python) "Inventory_updateDefault"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
for o in context.inventaire_mp.objectValues():
  print "Inventory copy default %s" % o.getRelativeUrl()
  o.activate(priority=3).Inventory_copyDefault()

for o in context.inventaire_pf.objectValues():
  print "Inventory copy default %s" % o.getRelativeUrl()
  o.activate(priority=3).Inventory_copyDefault()

return printed
