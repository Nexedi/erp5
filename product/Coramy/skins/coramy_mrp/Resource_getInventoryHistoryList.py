## Script (Python) "Resource_getInventoryHistoryList"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=resource_uid=None, variation_text=None, from_date=None, to_date=None, **kw
##title=
##
# Get the movement history
# BEWARE: if called in context of portal_categories, will include id 'resource' in context
quantity_history_list = context.Resource_zGetMovementHistoryList(resource_uid=resource_uid,
                    variation_text=variation_text, from_date=from_date, to_date=to_date, **kw)

# Calculate the integral as a list of tuples (date, resource, variation, inventory)
# Init integral
result = []
initial_inventory = {} # one value for each resource variation
current_date = {} # one value for each resource variation
last_movement = {}
initial_date = None
if from_date is not None: initial_date = from_date
for quantity_item in quantity_history_list:
  if initial_date is None: initial_date = quantity_item.stop_date
  key = (quantity_item.resource_uid, quantity_item.variation_text)
  # Do we have a quantity ?
  if not initial_inventory.has_key(key):
    # Calculate inventory at initial_date
    inventory = context.Resource_zGetInventory(resource_uid=[quantity_item.resource_uid],
                          to_date=initial_date,variation_text=quantity_item.variation_text, **kw)
    if len(initial_inventory) > 0:
      inventory = inventory[0].inventory
      if inventory is None: inventory = 0.0 # There are no movements at this time
    else:
      inventory = 0.0
    initial_inventory[key] = inventory
    current_date[key] = initial_date
  if quantity_item.stop_date != current_date[key]:
    result += [{'stop_date': current_date[key], 'resource_relative_url': quantity_item.resource_relative_url,
               'variation_text':quantity_item.variation_text, 'inventory': initial_inventory[key]}]
    current_date[key] = quantity_item.stop_date
  if quantity_item.quantity is not None:
    initial_inventory[key] = initial_inventory[key] + quantity_item.quantity
  last_movement[key] = quantity_item

for key in initial_inventory.keys():
  quantity_item = last_movement[key]
  result += [{'stop_date': current_date[key], 'resource_relative_url': quantity_item.resource_relative_url,
               'variation_text':quantity_item.variation_text, 'inventory': initial_inventory[key]}]

return result
