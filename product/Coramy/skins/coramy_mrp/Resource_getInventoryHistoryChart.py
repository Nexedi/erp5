## Script (Python) "Resource_getInventoryHistoryChart"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=resource_uid=None, variation_text=None, from_date=None, to_date=None, **kw
##title=
##
# Adapt dates
if from_date is None: from_date =DateTime()
if to_date is None: to_date = from_date + 365

# Get the movement history
inventory_history_list =  context.Resource_getInventoryHistoryList(resource_uid=resource_uid,
                      variation_text=variation_text, from_date=from_date, to_date=to_date, **kw)

# Create table of dates
table = {}
date = DateTime(from_date.Date())
while date < to_date:
  table[date.Date()] = {} # one value per (resource, variation)
  date = date + 1

# Fill existing variables and define resource_list
resource_dict = {}
for inventory in inventory_history_list:
  key = (inventory['resource_relative_url'], inventory['variation_text'])
  table[inventory['stop_date'].Date()][key] = \
    inventory['inventory']
  resource_dict[key] = 1

resource_list = resource_dict.keys()
resource_list.sort()

# Fill holes
date = DateTime((from_date + 1).Date())
while date < to_date:
  current_date_key = date.Date()
  previous_date_key = (date - 1).Date()
  for resource_key in resource_list:
    if not table[previous_date_key].has_key(resource_key):
      # This should not happen
      table[previous_date_key][resource_key] = None
    if not table[current_date_key].has_key(resource_key):
      table[current_date_key][resource_key] = table[previous_date_key][resource_key]
  date = date + 1

# Build List
date = DateTime(from_date.Date())
result = []
while date < to_date:
  current_date_key = date.Date()
  item = [current_date_key]
  for resource_key in resource_list:
    try:
      item += [table[current_date_key][resource_key]]
    except:
      print str(resource_key)
      print current_date_key
      return printed
  result += [item]
  date = date + 1

return result
