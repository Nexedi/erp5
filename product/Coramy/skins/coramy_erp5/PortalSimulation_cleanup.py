## Script (Python) "PortalSimulation_cleanup"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
process = context.portal_activities.newActiveProcess()
base_url = '/'.join(context.portal_url.getPortalObject().getPhysicalPath())

# ----------------------------------------------------------
# First make sure all simulation movements point to an order

print "-- Checking simulation"
for id in context.portal_simulation.objectIds():
  print "  AppliedRule_cleanOrphadedOrder %s" % id
  context.portal_activities.newMessage('SQLDict', '%s/portal_simulation/%s' % (base_url, id), process, {}, 'AppliedRule_cleanOrphanedOrder')

# ----------------------------------------------------------
# Next make sure all orders in > planned state have at most one applied rule

for module_id in ('ordre_fabrication','commande_achat','commande_vente',):
  for id in context[module_id].objectIds():
    print "  Order_cleanDuplicates %s/%s" % (module_id , id)
    context.portal_activities.newMessage('SQLDict', '%s/%s/%s' % (base_url, module_id, id), process, {}, 'Order_cleanDuplicates')

# ----------------------------------------------------------
# Next make sure all movements in a delivery of material point to simulation


# ----------------------------------------------------------
# Next make sure all movements in a delivery of material point to simulation

return printed
