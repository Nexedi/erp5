from Products.ERP5Type.Message import translateString
if listbox is not None:
  for line in listbox:
    context.restrictedTraverse(line['listbox_key']).DeliveryLine_createItemFreeForm(type=type, item_reference_list=line['item_reference_list'])
else:
  listbox = []
  for num, item_reference in enumerate(item_reference_list):
    if not item_reference:
      continue
    listbox.append({
      'listbox_key': str(num),
      'title': item_reference,
      'reference': item_reference,
      'quantity': 1.0  # XXX: Hardcoded resource.base_quantity_unit
    })
  context.DeliveryLine_createItemList(form_id=form_id, dialog_id=dialog_id, type=type, listbox=listbox, *args, **kwargs)
return context.Base_redirect(form_id, keep_items=dict(
      portal_status_message=translateString('Items created')))
