## Script (Python) "Order_cleanDuplicates"
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

of = context
if of.getSimulationState() not in ('draft', 'cancelled', 'auto_planned'):
    ps = of.getCausalityRelatedValueList(portal_type="Applied Rule")
    if len(ps) == 0:
      print "    Missing PS for Order %s of type %s" % (of.getId(), of.getPortalType())
      print "      Reexpand order %s" % of.getId()
      of.edit()
    elif len(ps) > 1:
      print "    Too many PS for Order %s of type %s" % (of.getId(), of.getPortalType())
      no_delivery = []
      delivery = []
      for ps_item in ps:
        if hasDelivery(ps_item):
          print "      PS %s has some delivered movements" % ps_item.getId()
          delivery.append(ps_item)
        else:
          print "      PS %s has no delivered movements" % ps_item.getId()
          no_delivery.append(ps_item)
      # manage_delObjects
      if len(delivery) > 0:
        # Only erase no_delivery if one item has delivery
        for ps_item in no_delivery:
          print "      Delete PS %s" % ps_item.getId()
          parent = ps_item.aq_parent
          parent.deleteContent(ps_item.getId())
      else:
        # Keep at least one
        for ps_item in no_delivery[1:]:
          print "      Delete PS %s" % ps_item.getId()
          id = ps_item.getId()
          parent = ps_item.aq_parent
          parent.deleteContent(ps_item.getId())
      if len(delivery) > 1:
        # We erase the Applied Rule but keep 
        # some excessive packing lists which may have been generated
        # THIS BREAKS CONSISTENCY 
        for ps_item in delivery[1:]:
          print "      Delete PS %s with BREAKS CONSISTENCY" % ps_item.getId()
          id = ps_item.getId()
          parent = ps_item.aq_parent
          #parent.deleteContent(ps_item.getId())

return printed
