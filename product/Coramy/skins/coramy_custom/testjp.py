## Script (Python) "testjp"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
context.SimulationTool_buildRequirementOrder(
       resource="composant/B4002",
       node_category="site/Stock_MP",
       section_category="group/Coramy"
        )

return "Done"


#

if len(context.getCausalityRelatedValueList()) == 1:
  # Only applied rule
  context.activate().buildDeliveryList()
else:
  return "causality is not 1"

return "Done"

#

context.SimulationTool_buildRequirementOrder(resource='composant/VIDJL')
return None

#
context.buildDeliveryList()
return "Done"

##

movement_list = []
order = context

if order.getPortalType() == 'Purchase Order' :
  filter_dict = {'portal_type': 'Purchase Order Line'}
else :
  filter_dict = {'portal_type': 'Sales Order Line'}

movement_list += order.getOrderRelatedValueList(portal_type = 'Simulation Movement')
for order_line in order.contentValues(filter=filter_dict) :
  movement_list += order_line.getOrderRelatedValueList(portal_type = 'Simulation Movement')
  for cell in order_line.contentValues(filter={'portal_type': 'Delivery Cell'}) :
     movement_list += cell.getOrderRelatedValueList(portal_type = 'Simulation Movement')

root_group = context.portal_simulation.collectMovement(movement_list)
delivery_list = context.portal_simulation.buildDeliveryList(root_group)

# what's the gestionaire of this order
user_name = ''
# are we on a sales order or puchase order ?
if order.getPortalType() == 'Sales Order' :
  user_name = order.getSourceAdministrationTitle().replace(' ','_')
elif order.getPortalType() == 'Purchase Order' :
  user_name = order.getDestinationAdministrationPersonTitle().replace(' ','_')

for delivery in delivery_list :
  # update the state of the created deliveries to 'confirmed'
  delivery.confirm()
  # update local_roles
  delivery.assign_gestionaire_designe_roles(user_name = user_name)

return str(delivery_list)


#

context.buildDeliveryList()
return None

#

for l in context.objectValues():
  print l.getRelativeUrl(), l.getInventoriatedQuantity()
  for c in l.objectValues():
    print c.getRelativeUrl(), c.getInventoriatedQuantity()

return printed


#
context.buildInvoiceList()
return "Done"

#

return str(context.getConvertedQuantity() is not None)

#

for l in context.objectValues():
  l.immediateReindexObject()  
  for c in l.objectValues():
    try:
      c.immediateReindexObject()  
    except:
      print c.getRelativeUrl()

return printed

#-

return str(context.getCausalityValueList())

#-

context.expand(applied_rule_id = '2308')
return "Done"

#- 

for l in context.objectValues():
  if l.isDivergent():
    print "Divergent", l.getRelativeUrl(), str(l.getDeliveryRelatedValueList())
  for c in l.objectValues():
    if not c.isSimulated():
      print "Not simulated", c.getRelativeUrl(), str(c.getDeliveryRelatedValueList())
    elif c.isDivergent():
      print "Divergent", c.getRelativeUrl(), str(c.getDeliveryRelatedValueList())


print 'OK'
return printed

#-

context.updateAppliedRule()
return "Done"

#¬
return context.portal_simulation.updateAssetPrice(
	 	'assortiment/751H402_12P_H', '',
		"group/Coramy",
		"site/Stock_PF"
        )

return context.portal_simulation.updateAssetPrice(
	 	'composant/AN014', 'variante/composant/AN014/bronze blanc',
		"group/Coramy",
		"site/Stock_MP"
        )

return context.portal_simulation.updateAssetPrice(
	 	'modele/067E402', 'coloris/modele/067E402/0_noir_blanc\nmorphologie/modele/067E402/C\ntaille/adulte/48',
		"group/Coramy",
		"site/Stock_PF"
        )




#-

context.buildInvoiceList()
return "Done"




t = context.getDefaultCausalityValue()
return t.getId()


#-

return str(context.getAggregatedAmountList(
                        categories = "taille/adulte/40\ncoloris/modele/058B406/2"))
#--

print context.getQLineItemList()
print context.getQColumnItemList()
print context.getQTabItemList()
print context.getVLineItemList()
print context.getVColumnItemList()
print context.getVTabItemList()

return printed

#--

return context.buildInvoiceList()

#-

return str(hasattr(context, 'inventory'))

#--


return str(context.getInventory())

#--

resource_list = context.PortalSimulation_zGetResourceList()
context.portal_simulation.commitTransaction()

commit = 100
for b in resource_list :
  relative_url =  b.resource_relative_url
  variation_text = b.variation_text
  if relative_url is not None:
    if relative_url.find('modele') >= 0:
      if variation_text not in (None, ''):
        #print "##Calculate price for %s %s" % (b.resource_relative_url, b.variation_text)
        context.portal_simulation.activate(activity='SQLQueue', priority=3).updateAssetPrice(
	 	relative_url, variation_text,
		"group/Coramy",
		"site/Stock_PF"
        )
      else:
        print "###Error variation for modele" % variation_text
    commit = commit  -1
    if commit == 0:
      context.portal_simulation.commitTransaction()
      commit = 100

return printed

##

result = context.portal_simulation.updateAssetPrice(
		"tissu/TI012",
		"""coloris/tissu/TI012/Serenity 6025""",
		"group/Coramy",
		"site/Stock_MP"
	)

for i in result:
  print ' '.join(map(lambda x:str(x), i))

return printed


#--

result = context.portal_simulation.updateAssetPrice(
		"modele/417P401",
		"""coloris/modele/417P401/1_espace_stuc
taille/enfant/10 ans""",
		"group/Coramy",
		"site/Stock_PF"

	)

for i in result:
  print ' '.join(map(lambda x:str(x), i))

return printed

#-

context.restrictedTraverse("modele/537C419GLC/3").updateRelatedContent('modele/537C419GLC/2','modele/537C419GLC/3')
return 'Done'

#-

olist = context.portal_catalog(simulation_state="auto_planned", parent_uid=[context.ordre_fabrication.getUid(),context.commande_achat.getUid()])
return map(lambda x:x.path, olist)

#-

return str(context.contentValues())

modele_prix = context.restrictedTraverse('modele/417P401/pri_0_0')
modele =  context.restrictedTraverse('modele/417P401')

return str(modele.getIndustrialPrice(context=context))
return str(modele_prix.test(context.asContext()))

#--

return str(context.isMemberOf('site/Piquage'))

context.restrictedTraverse('portal_simulation/3078/2').setDelivery('livraison_vente/364/1')
context.restrictedTraverse('portal_simulation/3083/2').setDelivery('livraison_vente/366/1')

return "Done"


#-


return context.buildDeliveryList()
#return context.getMovementList()
#return context.updateAppliedRule()


return len(context.Resource_zGetMovementHistoryList(resource=("modele/417P401",),
		variation_text="""coloris/modele/417P401/1_espace_stuc
taille/enfant/10 ans""",
                strict_membership=0,
		section_category="group/Coramy",
		node_category="site/Stock_PF",
                simulation_state=('delivered', 'started', 'stopped', 'invoiced')))
#--------------------

for m in context.getMovementList():
  if not m.isSimulated():
    print "Not simumlated: %s" % m.getRelativeUrl()

return printed

#--------------------

dest = context.getDestinationValue(portal_type=['Organisation']).getTitle()
return dest


movement_list = context.getOrderRelatedMovementList()
movement_uid_list = map(lambda o:o.getUid(), movement_list)
return movement_uid_list 
return map(lambda x: (x.path, x.quantity, x.target_quantity),list(context.ProductionOrder_getAggregatedMaterialConsumptionList()))

return context.updateAppliedRule()

return '/'.join(context.getPhysicalPath())

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

print "-- Checking simulation"
for ar in context.portal_simulation.objectValues():
  if ar.getCausalityValue() is None:
    print "    Applied Rule %s has no order" % ar.getId()
    print "      Previously was: %s" % ar.getCausality()
    if hasDelivery(ar):
          print "      Applied Rule %s has some delivered movements" % ar.getId()
          print "        deliveries: %s" % ' '.join(getDeliveryList(ar).keys())
    elif ar.getId() not in ('zero_stock', ):
          print "      Delete %s" % ar.getId()
          context.portal_simulation.deleteContent(ar.getId())

# ----------------------------------------------------------
# Next make sure all orders in > planned state have at most one applied rule

order_list = context.ordre_fabrication.objectValues() + context.commande_achat.objectValues() + context.commande_vente.objectValues()

for of in order_list:
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
          parent.deleteContent(ps_item.getId())


# ----------------------------------------------------------
# Next make sure all movements in a delivery of material point to simulation


# ----------------------------------------------------------
# Next make sure all movements in a delivery of material point to simulation


return printed
