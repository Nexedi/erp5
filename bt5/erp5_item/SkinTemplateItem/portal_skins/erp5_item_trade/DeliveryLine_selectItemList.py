from Products.ERP5Type.Message import translateString
item_list = []
portal = context.getPortalObject()
getObject = portal.portal_catalog.getObject
selection_tool = portal.portal_selections

line_portal_type = context.getPortalType()

if line_portal_type == 'Sale Packing List Line':
  cell_portal_type = 'Sale Packing List Cell'
elif line_portal_type == 'Sale Order Line':
  cell_portal_type = 'Sale Order Cell'
elif line_portal_type == 'Purchase Packing List Line':
  cell_portal_type = 'Purchase Packing List Cell'
elif line_portal_type == 'Inventory Line':
  cell_portal_type = 'Inventory Cell'
elif line_portal_type == 'Internal Packing List Line':
  cell_portal_type = 'Internal Packing List Cell'
else:
  raise NotImplementedError('Unknown line type %s' % line_portal_type)


# update selected uids 
selection_tool.updateSelectionCheckedUidList(
    list_selection_name, uids=uids, listbox_uid=listbox_uid, REQUEST=None)
uids = selection_tool.getSelectionCheckedUidsFor(list_selection_name)

resource_uid_list = []
message = None
if not context.getResource():
  # Delivery line doesn't have resource defined yet.
  # Iterate over all selected items then check if they all
  # share the same resource. If not return to the dialog with warning message
  # otherwise edit the Delivery Line (context) with resource of all items.
  for item_uid in uids:
    item = getObject(item_uid)
    resource_item = item.Item_getResourceValue()
    if resource_item is None:
      message = portal.Base_translateString('Selected ${translated_portal_type} has no resource defined',
                                            mapping={'translated_portal_type': item.getTranslatedPortalType().lower()})
      break
    if not resource_uid_list:
      # first item
      resource_uid_list.append(resource_item.getUid())
    elif resource_item.getUid() not in resource_uid_list:
      message = portal.Base_translateString('Selected ${translated_portal_type} does not share the same resource',
                                            mapping={'translated_portal_type': item.getTranslatedPortalType().lower()})
      break
  if resource_uid_list and not message:
    # set resource on Delivery Line
    context.setResourceUid(resource_uid_list[0])
if message:
  # means that resource consistency fails.
  # One of Items does not have resource or Items does not share same resource
  # Script stop here
  context.Base_updateDialogForm(listbox=listbox,update=1, kw=kw)
  REQUEST = portal.REQUEST
  REQUEST.set('portal_status_message', message)
  return getattr(context, REQUEST.form['dialog_id'])(listbox=listbox, kw=kw)

for item_uid in uids:
  item = getObject(item_uid)
  item_variation = \
      item.Item_getVariationCategoryList(at_date=context.getStartDate())
  # if we have variation, find matching cell to add this item to the cell
  if item_variation:
    cell_found = None
    for cell in context.getCellValueList(base_id='movement'):
      if cell.getVariationCategoryList() == item_variation:
        cell_found = cell
        break
    if cell_found is not None:
      movement_to_update = cell_found
    else:
      if not context.hasInRange(base_id='movement', *item_variation):
        # update line variation category list, if not already containing this one
        variation_category_list = context.getVariationCategoryList()
        for variation in item_variation:
          if variation not in variation_category_list:
            variation_category_list.append(variation)
        context.setVariationCategoryList(variation_category_list)

      movement_to_update = context.newCell(base_id='movement',
                                           portal_type=cell_portal_type,
                                           *item_variation)
      movement_to_update.edit(mapped_value_property_list=('quantity', 'price'),
                              variation_category_list=item_variation,)
  else:
    # no variation, we'll update the line itself
    movement_to_update = context

  movement_to_update.setAggregateValueSet(
      movement_to_update.getAggregateValueList() + [item])

return context.Base_redirect(form_id, keep_items=dict(
       portal_status_message=translateString('Items aggregated')))
