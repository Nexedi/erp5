## Script (Python) "AppliedRule_cleanOrphanedOrder"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
# Use this script to test if simulation state is acceptable

def hasDelivery(ps_item):
  for m in ps_item.objectValues():
    if len(m.getCategoryMembershipList('delivery')) > 0:
      return 1
    for a in m.objectValues():
      if hasDelivery(a):
        return 1
  return 0

def getDeliveryList(ps_item):
  result = {}
  for m in ps_item.objectValues():
    for d in m.getDeliveryValueList():
      if d is not None:
        result[d.getRelativeUrl()] = 1
    for a in m.objectValues():
      result.update( getDeliveryList(a))
  return result

# ----------------------------------------------------------
# First make sure all simulation movements point to an order

ar = context
r = ar.getSpecialiseValue() 
if r is not None:
 if r.getPortalType() == "Order Rule":
  if ar.getCausalityValue() is None:
    # Additional test need to check this is an order rule
    print "    Applied Rule %s has no order" % ar.getId()
    print "      Previously was: %s" % ar.getCausality()
    if hasDelivery(ar):
         print "      Applied Rule %s has some delivered movements" % ar.getId()
         print "        deliveries: %s" % ' '.join(getDeliveryList(ar).keys())
    elif ar.getId() not in ('zero_stock', ):
         print "      Delete %s" % ar.getId()
         context.portal_simulation.deleteContent(ar.getId())

return printed
