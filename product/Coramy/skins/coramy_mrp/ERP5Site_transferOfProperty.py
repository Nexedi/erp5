## Script (Python) "ERP5Site_transferOfProperty"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=to_date
##title=
##
## Warnings:
##  Prints, but never reads 'printed' variable.
##
from Products.ERP5.Document import newTempMovement
from DateTime import DateTime

# Stock sourcing states
source_state_list = ('delivered', 'started', 'stopped', 'invoiced')
coef_marge_coramy = 1.35

# Default date
now_date = DateTime(DateTime().Date())
to_date = "2003/10/31"

# Get inventory list
inventory_list = context.Resource_zGetStockPFInventoryList(calculate_asset=1,
                    node_category='site/Stock_PF', section_category='group/Coramy',
                    collection_url='collection/2004/DIM',
                    group_by_node=0, group_by_section=1,
                    group_by_variation=1, to_date=to_date,
                    section_uid=context.portal_categories.group.Coramy.uid,
                    simulation_state=source_state_list)

# Commit SQL
context.portal_simulation.commitTransaction()

# build a dictionnary of quantity, variation
quantity_dict = {}
price_dict = {}
variation_dict = {}
for inventory_item in inventory_list:
  movement = inventory_item.getObject()
  if movement is not None:
    key = (inventory_item.resource_relative_url, tuple(movement.getVariationCategoryList()))
    if not (key in quantity_dict.keys()) :
      quantity_dict[key] = {}
      price_dict[key] = {}
    quantity_dict[key][inventory_item.section_title] = inventory_item.inventory
    price_dict[key][inventory_item.section_title] = movement.Amount_getPri()*coef_marge_coramy
    variation_dict[key] = movement.getVariationCategoryList()

  else:
      pass
      #LOG('WARNING',0,'None movement found')

# Find out which are the movements to create
to_create = []
for key in quantity_dict.keys() :
  section_list = quantity_dict[key].keys()
  if 'Coramy' in section_list :
    if quantity_dict[key]['Coramy'] > 0 :
      to_create.append(key)

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
    stop_date = to_date

    if resource.getPortalType() in ('Modele', 'Assortiment'):
      source = 'site/Stock_PF/Gravelines'
      source_section = 'group/Coramy'
      destination_section = 'group/Coramy/BLS'
      destination = 'site/Stock_PF/Gravelines'
    else:
      source = source_section = resource.getSource()
      destination_section = 'group/Coramy'
      destination = 'site/Stock_MP/Gravelines'
    movement.edit(target_quantity = quantity_dict[key]['Coramy'],
                  price = price_dict[key]['Coramy'],
                  target_start_date = stop_date,
                  target_stop_date = stop_date,
                  source = source,
                  source_section = source_section,
                  destination_section = destination_section,
                  destination = destination,
                  quantity_unit = resource.getDefaultQuantityUnit())
    print "Order %s %s quantity: %s" % (movement.getResource(), movement.getVariationText(), movement.getNetConvertedTargetQuantity())
    movement_list.append(movement)

# Build Deliveries
root_group = context.portal_simulation.collectMovement(movement_list)
delivery_list = context.portal_simulation.buildDeliveryList(root_group)

# Update deliveries
for delivery in delivery_list :
  # update the state of the created deliveries to 'confirmed'
  delivery.confirm()
  # update local_roles
  delivery.assign_gestionaire_designe_roles(user_name = '')

return delivery_list
