item_list = context.objectValues()

# Re-build the sub-objects
for item in item_list:
  item.build(context)
