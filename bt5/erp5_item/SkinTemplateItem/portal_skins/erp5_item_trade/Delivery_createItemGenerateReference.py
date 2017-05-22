from Products.ERP5Type.Message import translateString

for line in listbox:
  movement = context.restrictedTraverse(line['listbox_key'])
  movement.DeliveryLine_createItemGenerateReference(type=line['type'])

return context.Base_redirect(form_id, keep_items=dict(
    portal_status_message=translateString('Items created')))
