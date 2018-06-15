item = state_change['object']
item_new_reference_item = item.getPredecessorValue()

if item_new_reference_item:
  item_new_reference_item_path = item_new_reference_item.getItemPath()
  if item.getItemPath() != item_new_reference_item_path:
    item.setItemPath(item_new_reference_item_path)

  if not item.getItemPatchBehaviour():
    item.setItemPatchBehaviour('force_apply')
