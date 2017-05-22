from Products.ERP5Type.Message import translateString

for line in listbox:
  if len(line['item_reference_list']) == 0:
    continue
  movement = context.restrictedTraverse(line['listbox_key'])
  movement.DeliveryLine_createItemFreeForm(type=line['type'], item_reference_list=line['item_reference_list'])

return context.Base_redirect(form_id, keep_items=dict(
    portal_status_message=translateString('Items created')))
