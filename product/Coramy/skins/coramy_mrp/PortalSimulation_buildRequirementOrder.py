## Script (Python) "PortalSimulation_buildRequirementOrder"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=resource=None
##title=
##

from Products.ERP5Type.Document import newTempMovement
from DateTime import DateTime

# Stock sourcing states
#source_state_list = ('auto_planned', 'planned', 'ordered', 'confirmed', 'getting_ready', 'ready', 'delivered', 'started', 'stopped', 'invoiced')
source_state_list = None

# Default date
now_date = DateTime()

# Get inventory list
inventory_list = context.SimulationTool_getGroupFutureInventoryList(resource=resource, simulation_state=source_state_list)
# Commit SQL
# context.portal_simulation.commitTransaction()

# First, find out which resources are missing
# and build a dictionnary of quantity, variation
quantity_dict = {}
variation_dict = {}
for inventory_item in inventory_list:
  if inventory_item.inventory < 0 and inventory_item.inventory is not None:
    # Only source negative stock
    movement = inventory_item.getObject()
    if movement is not None:
      key = (inventory_item.resource_relative_url, tuple(movement.getVariationCategoryList()))
      quantity_dict[key] = - inventory_item.inventory
      variation_dict[key] = movement.getVariationCategoryList()
    else:
        pass
        #LOG('ZeroStockRule WARNING',0,'None movement found')

# Commit SQL
# context.portal_simulation.commitTransaction()

# A list of resources to create
to_create = quantity_dict.keys()
movement_list = []

new_id = 0
# Create movements which are needed
for relative_url, variation_category_list in to_create:
  # CHECK IF EXISTING ID
  key = (relative_url, variation_category_list)
  new_id += 1
  movement = newTempMovement( context.portal_simulation , str(new_id) )
  movement.edit( resource=relative_url )
  movement.setVariationCategoryList( variation_category_list )
  resource = movement.getResourceValue()

  if resource is not None:
    # Only order existing resources
    stop_date = resource.getNextNegativeInventoryDate(variation_text = movement.getVariationText())
    if stop_date is None: # This happens if we have a negative stock already
      stop_date = now_date

    if resource.getPortalType() in ('Modele',):
      source = 'site/Piquage'
      source_section = 'group/Coramy'
      destination_section = 'group/Coramy'
      destination = 'site/Stock_PF/Gravelines'
    else:
      source = source_section = resource.getSource()
      destination_section = 'group/Coramy'
      destination = 'site/Stock_MP/Gravelines'
    movement.edit(target_quantity = quantity_dict[key],
                  target_start_date = stop_date,
                  target_stop_date = stop_date,
                  source = source,
                  source_section = source_section,
                  destination_section = destination_section,
                  destination = destination,
                  quantity_unit = resource.getDefaultQuantityUnit())
    print "Order %s %s quantity: %s" % (movement.getResource(), movement.getVariationText(), movement.getNetConvertedTargetQuantity())
    movement_list.append(movement)

# Build Order
root_group = context.portal_simulation.collectMovement(movement_list)
order_list = context.portal_simulation.buildOrderList(root_group)

# Update orders
for order in order_list:
  print "Confirm Order %s" % order.getRelativeUrl()
  order.autoPlan()
  order.purchase_order_apply_condition()

return printed