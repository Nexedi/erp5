## Script (Python) "Resource_getFutureHistoryList"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=from_date=None, to_date=None, node_uid=None, section_uid=None, **kw
##title=
##
# context is the resource which we call this method on
resource = context

# Initialize some parameters which we do not know yet where to get from
# XXX TO BE DONE TO CONVERT OBJECTS / URLS to UIDS

# Get the inventory at from_date
if from_date is not None:
  initial_inventory_list = resource.Resource_zGetInventoryList(resource_uid = resource.getUid(), 
                             to_date = from_date, node_uid = node_uid, section_uid=section_uid, **kw)
  if len(initial_inventory_list) > 0:
    initial_inventory_list = initial_quantity_list[0].inventory
  else:
    initial_inventory  = 0.0
else:
  initial_inventory = 0.0

# Get the movement history
quantity_history_list = resource.Resource_zGetMovementHistoryList(resource_uid = resource.getUid(), 
                             from_date = from_date, to_date=to_date, node_uid = node_uid, section_uid=section_uid, **kw)

# Calculate the integral
result = []
current_date = from_date
has_quantity_item = 0
for quantity_item in quantity_history_list:
  has_quantity_item = 1
  if quantity_item.start_date != current_date and current_date is not None:
    result = [{'start_date': current_date, 'inventory': initial_inventory}]
  if quantity_item.start_date != current_date:
    current_date = quantity_item.start_date
  initial_inventory += quantity_item.quantity
if has_quantity_item:
  result += [ {'start_date': current_date, 'inventory': initial_inventory} ]

return result
