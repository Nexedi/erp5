## Script (Python) "PortalSimulation_updateInventory"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
for b in context.SimulationTool_zGetSortedInventoryList():
  print "#### Indexing Inventory %s ####" % b.relative_url
  o = b.getObject()
  if o is not None: o.activate(priority=4).recursiveImmediateReindexObject()

return printed
