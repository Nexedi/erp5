## Script (Python) "PackingList_cleanupAssortiment"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
# This script cleans packing lists we deffective quantities equal to 0.0 by resetting quantities
# to values in the simulation

for movement_brain in context.PackingList_searchAssortiment():
  movement = movement_brain.getObject()
  if movement.getQuantity() == 0.0:
    if movement.getRelatedQuantity() is not None:
      print "Fix movement %s from %s to %s" % (movement.getRelativeUrl(), movement.getQuantity(), movement.getRelatedQuantity())
      #movement.setQuantity(movement.getRelatedQuantity())
    else:
      print "### Error movement %s has no simulation" % movement.getRelativeUrl()
  else:
    print "### NONSENSE on %s" % movement.getRelativeUrl()

return printed
