# Get all the Business Item object(s) for given Business Manager
# As the items are `Persistent` objects, we can try to display it in ERP5 UI

manager = context
path_item_list = manager.getPathItemList()

return path_item_list
