## Script (Python) "PortalSimulation_rescueOrphaned"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
exception_order = ['303',]

orphaned_delivery_related_list = {}
orphaned_delivery_related_quantity = {}
exception_order = ['303',]

orphaned_delivery_related_list = {}
has_delivery_rule_related_list = {}
orphaned_delivery_related_quantity = {}
orphaned_delivery_related_target_quantity = {}
orphaned_delivery_list = {}
orphaned_delivery_quantity = {}
orphaned_delivery_target_quantity = {}
build_delivery_list = []

m_list = list(context.Delivery_zGetOrphanedProductionMovementList()) + list(context.Delivery_zGetOrphanedMovementList())
#m_list = context.Delivery_zGetOrphanedProductionMovementList()
#m_list = context.Delivery_zGetOrphanedMovementList()
for b in m_list:
  m = b.getObject()
  if m.getDeliveryValue() is None:
    # Only process orphaned
    if m.getNetConvertedTargetQuantity() is None:
      return "Error for target_quantity on %s" % m.getRelativeUrl()
    if m.getNetConvertedQuantity() is None:
      return "Error for quantity on %s" % m.getRelativeUrl()
    ra = m.getRootAppliedRule()
    order = ra.getCausalityValue() # Order
    if order is not None:
      order_id = order.getId()
      order_relative_url = order.getRelativeUrl()
    else:
      order_id = 'UNKNOWN ORDER'
      order_relative_url = None
    if order_id not in exception_order:
      print "Trying to fix order %s: %s" % (order_relative_url , b.path)
      candidates = context.Movement_search(resource_uid = b.resource_uid, variation_text = b.variation_text,
                                        source_uid = m.getSourceUid(), destination_uid = m.getDestinationUid())
      found_candidate = 0
      if len(candidates) > 0:
        for dm in candidates:
          dm_object = dm.getObject()
          if dm_object is not None:
            if order_relative_url in dm_object.getDeliveryValue().getCausalityList():
              is_orphaned = not dm_object.isSimulated()
              quantity_difference =  dm_object.getNetConvertedQuantity() -  m.getNetConvertedQuantity()
              target_quantity_difference =  dm_object.getNetConvertedTargetQuantity() -  m.getNetConvertedTargetQuantity()
              is_identical = quantity_difference  ==  0
              # We must test here is this object has a delivery rule attached to
              # we may have to remove some delivery rules...
              simulation_m = dm_object.getDeliveryRelatedValueList()
              if len(simulation_m) == 1:
                if simulation_m[0].getRootAppliedRule().getDefaultCausalityValue().getPortalType() == "Delivery Rule":
                  has_delivery_rule = 0
                else:
                  has_delivery_rule = 1
              else:
                has_delivery_rule = 0
              print "  found related %s orphaned: %s order: %s identical: %s drule: %s delivery q/t: %s %s simulation q/t: %s %s" % (
                                                  dm_object.getRelativeUrl(),
                                                  is_orphaned,
                                                  dm_object.getCausalityList(),
                                                  is_identical,
                                                  has_delivery_rule,
                                                  dm_object.getNetConvertedQuantity(),
                                                  dm_object.getNetConvertedTargetQuantity(),
                                                  m.getNetConvertedQuantity(),
                                                  m.getNetConvertedTargetQuantity(), )
              if is_orphaned or has_delivery_rule:
                # Only orphaned movements are good candidates
                found_candidate = 1
                # Build dm_object to m mapping
                if not orphaned_delivery_related_list.has_key(dm_object):
                  orphaned_delivery_related_list[dm_object] = []
                  has_delivery_rule_related_list[dm_object] = []
                  orphaned_delivery_related_quantity[dm_object] = 0.0
                  orphaned_delivery_related_target_quantity[dm_object] = 0.0
                if m not in orphaned_delivery_related_list[dm_object]:
                  # Do not count twice
                  orphaned_delivery_related_list[dm_object].append(m)
                  if has_delivery_rule: has_delivery_rule_related_list[dm_object].append(m)
                  orphaned_delivery_related_quantity[dm_object] = orphaned_delivery_related_quantity[dm_object] + m.getNetConvertedQuantity()
                  orphaned_delivery_related_target_quantity[dm_object] = orphaned_delivery_related_target_quantity[dm_object] + \
                                                                         m.getNetConvertedTargetQuantity()
                # Build m to dm_object mapping
                if not orphaned_delivery_list.has_key(m):
                  orphaned_delivery_list[m] = []
                  orphaned_delivery_quantity[m] = 0.0
                  orphaned_delivery_target_quantity[m] = 0.0
                if dm_object not in orphaned_delivery_list[m]:
                  # Do not count twice
                  orphaned_delivery_list[m].append(dm_object)
                  orphaned_delivery_quantity[m] = orphaned_delivery_quantity[m] + dm_object.getNetConvertedQuantity() # Quantity is likely 0
                  orphaned_delivery_target_quantity[m] = orphaned_delivery_target_quantity[m] + \
                                          dm_object.getNetConvertedTargetQuantity() # Quantity is likely 0
      if not found_candidate:
        # Best solution is probably to create a new delivery
        if order is not None:
          for delivery in order.getCausalityRelatedValueList(portal_type=("Sales Packing List", "Purchase Packing List",
                            "Production Report", "Production Packing List", "Sale Packing List" )):
            print "  portential delivery %s" % delivery.getRelativeUrl()
        else:
          print "  no order found"
        build_delivery_list.append(m)

print "======================================================="
print "N to 1 aggregates"
for dm_object in orphaned_delivery_related_list.keys():
  if dm_object.getNetConvertedQuantity() == orphaned_delivery_related_quantity[dm_object]:
    print "  Found matching N(%s) quantity to 1 quantity aggregate for %s" % (
              len(orphaned_delivery_related_list[dm_object]), dm_object.getRelativeUrl())
    for m in orphaned_delivery_related_list[dm_object]:
      print "  #### attaching %s to %s" % (m.getRelativeUrl() , dm_object.getRelativeUrl())
      #m.setDeliveryValue(dm_object)
      del orphaned_delivery_list[m] # Not needed anylonger since we found a solution
      del orphaned_delivery_quantity[m] # Not needed anylonger since we found a solution
  elif dm_object.getNetConvertedTargetQuantity() == orphaned_delivery_related_target_quantity[dm_object]:
    print "  Found matching N(%s) target_quantity to 1 target_quantity aggregate for %s" % (
                len(orphaned_delivery_related_list[dm_object]), dm_object.getRelativeUrl())
    print "  #### updating quantity of %s" % dm_object.getRelativeUrl()
    #dm_object.setNetConvertedQuantity(orphaned_delivery_related_quantity[dm_object]) # Update quantity to meet simulation
    for m in orphaned_delivery_related_list[dm_object]:
      print "  #### attaching %s to %s" % (m.getRelativeUrl() , dm_object.getRelativeUrl())
      #m.setDeliveryValue(dm_object)
      del orphaned_delivery_list[m] # Not needed anylonger since we found a solution
      del orphaned_delivery_quantity[m] # Not needed anylonger since we found a solution
  elif dm_object.getNetConvertedQuantity() == 0 and dm_object.getNetConvertedTargetQuantity() != 0:
    # Probably delivery relation renamed at some point
    print "  Found zeroed N(%s) to 1 aggregate for %s" % (
                len(orphaned_delivery_related_list[dm_object]), dm_object.getRelativeUrl())
    print "  #### updating quantity of %s" % dm_object.getRelativeUrl()
    #dm_object.setNetConvertedQuantity(orphaned_delivery_related_quantity[dm_object]) # Update quantity to meet simulation
    for m in orphaned_delivery_related_list[dm_object]:
      print "  #### attaching %s to %s" % (m.getRelativeUrl() , dm_object.getRelativeUrl())
      #m.setDeliveryValue(dm_object)
      del orphaned_delivery_list[m] # Not needed anylonger since we found a solution
      del orphaned_delivery_quantity[m] # Not needed anylonger since we found a solution
  else:
    print "  Found non matching N(%s) to 1 aggregate for %s delivery q/t: %s %s simulation q/t: %s %s" % (
                    len(orphaned_delivery_related_list[dm_object]),
                    dm_object.getRelativeUrl(),
                    dm_object.getNetConvertedQuantity(), dm_object.getNetConvertedTargetQuantity(),
                    orphaned_delivery_related_quantity[dm_object], orphaned_delivery_related_target_quantity[dm_object])
    print "  #### updating quantity of %s" % dm_object.getRelativeUrl()
    #dm_object.setNetConvertedQuantity(orphaned_delivery_related_quantity[dm_object]) # Update quantity to meet simulation
    for m in orphaned_delivery_related_list[dm_object]:
      print "  #### attaching %s to %s" % (m.getRelativeUrl() , dm_object.getRelativeUrl())
      #m.setDeliveryValue(dm_object)
      del orphaned_delivery_list[m] # Not needed anylonger since we found a solution
      del orphaned_delivery_quantity[m] # Not needed anylonger since we found a solution

print "======================================================="
print "1 to N > 1 aggregates"
for m in orphaned_delivery_list.keys():
  if len(orphaned_delivery_list[m]) > 1:
    # 1 to 1 should be already processed at this point
    if m.getNetConvertedQuantity() == orphaned_delivery_target_quantity[m]:
      print "  Found matching 1 to N(%s) aggregate for %s" % (len(orphaned_delivery_list[m]), m.getRelativeUrl())
      dm_object = orphaned_delivery_list[m][0]
      print "  #### attaching %s to %s q/t: %s %s" % (m.getRelativeUrl(), dm_object.getRelativeUrl(),
                                                      dm_object.getNetConvertedQuantity(), dm_object.getNetConvertedTargetQuantity())
      # XXX What about quantity_unit
#       m.edit(
#                target_start_date = dm_object.getTargetStartDate(),
#                target_stop_date = dm_object.getTargetStopDate(),
#                start_date = dm_object.getStartDate(),
#                stop_date = dm_object.getStopDate(),
#                quantity = dm_object.getQuantity(),
#                target_quantity = dm_object.getTargetQuantity(),
#                delivery = dm_object.getRelativeUrl(),
#        )
      for i in range(len(orphaned_delivery_list[m]) - 1):
        new_id = "%s_fixsplit_%s" % (m.getId(), i)
        dm_object = orphaned_delivery_list[m][i+1]
        print "  #### creating new simulation movement %s attached to %s q/t: %s %s" % (new_id, dm_object.getRelativeUrl(),
                                                                         dm_object.getNetConvertedQuantity(),
                                                                         dm_object.getNetConvertedTargetQuantity())
        # XXX What about quantity_unit
#         new_movement = m.aq_parent.newContent(portal_type = "Simulation Movement",
#                                             id = new_id,
#                                             efficiency = m.getEfficiency(),
#                                             target_efficiency = m.getTargetEfficiency(),
#                                             target_start_date = dm_object.getTargetStartDate(),
#                                             target_stop_date = dm_object.getTargetStopDate(),
#                                             start_date = dm_object.getStartDate(),
#                                             stop_date = dm_object.getStopDate(),
#                                             quantity = dm_object.getQuantity(),
#                                             target_quantity = dm_object.getTargetQuantity(),
#                                             delivery = dm_object.getRelativeUrl(),
#                                             source = m.getSource(),
#                                             destination = m.getDestination(),
#                                             source_section = m.getSourceSection(),
#                                             destination_section =  m.getDestinationSection(),
#                                             order = m.getOrder()
#                                           )
    else:
      print "  Found non matching 1 to N(%s) aggregate for %s delivery q/t: %s %s simulation q/t: %s %s" % (
                      len(orphaned_delivery_list[m]), m.getRelativeUrl(),
                      orphaned_delivery_quantity[m], orphaned_delivery_target_quantity[m],
                      m.getNetConvertedQuantity(), m.getNetConvertedTargetQuantity(),
                      )
      dm_object = orphaned_delivery_list[m][0]
      print "  #### attaching %s to %s q/t: %s %s" % (m.getRelativeUrl(), dm_object.getRelativeUrl(),
                                                      dm_object.getNetConvertedQuantity(), dm_object.getNetConvertedTargetQuantity())
      # XXX What about quantity_unit
#       m.edit(
#                target_start_date = dm_object.getTargetStartDate(),
#                target_stop_date = dm_object.getTargetStopDate(),
#                start_date = dm_object.getStartDate(),
#                stop_date = dm_object.getStopDate(),
#                quantity = dm_object.getQuantity(),
#                target_quantity = dm_object.getTargetQuantity(),
#                delivery = dm_object.getRelativeUrl(),
#        )
      for i in range(len(orphaned_delivery_list[m]) - 1):
        new_id = "%s_fixsplit_%s" % (m.getId(), i)
        dm_object = orphaned_delivery_list[m][i+1]
        print "  #### creating new simulation movement %s attached to %s q/t: %s %s" % (new_id, dm_object.getRelativeUrl(),
                                                                         dm_object.getNetConvertedQuantity(),
                                                                         dm_object.getNetConvertedTargetQuantity())
        # XXX What about quantity_unit
#         new_movement = m.aq_parent.newContent(portal_type = "Simulation Movement",
#                                             id = new_id,
#                                             efficiency = m.getEfficiency(),
#                                             target_efficiency = m.getTargetEfficiency(),
#                                             target_start_date = dm_object.getTargetStartDate(),
#                                             target_stop_date = dm_object.getTargetStopDate(),
#                                             start_date = dm_object.getStartDate(),
#                                             stop_date = dm_object.getStopDate(),
#                                             quantity = dm_object.getQuantity(),
#                                             target_quantity = dm_object.getTargetQuantity(),
#                                             delivery = dm_object.getRelativeUrl(),
#                                             source = m.getSource(),
#                                             destination = m.getDestination(),
#                                             source_section = m.getSourceSection(),
#                                             destination_section =  m.getDestinationSection(),
#                                             order = m.getOrder()
#                                           )

print "======================================================="
print "New deliveries"

#root_group = context.portal_simulation.collectMovement(build_delivery_list)
#delivery_list = context.portal_simulation.buildDeliveryList(root_group)
#for delivery in delivery_list:
#  print "New delivery %s for causality %s" % (delivery.getRelativeUrl(), ' '.join(delivery.getCausalityList()))

print '\n'.join(map(lambda x:x.getRelativeUrl(), build_delivery_list))

print "======================================================="
print "Reexpand delivery rules (and delete duplicate delivery relations)"
for arb in context.portal_rules.default_delivery_rule.getSpecialiseRelatedValueList():
  ar = arb.getObject()
  before = len(ar.objectIds())
  #ar.expand()
  after = len(ar.objectIds())
  print "  reexpand %s before: %s after: %s" % (ar.getRelativeUrl(), before, after)


print "======================================================="
print "TODO"

print "  compare quantities in simulation and deliveries"



return printed
