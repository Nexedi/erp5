packing_list = context
related_order = packing_list.getCausalityValue()

if packing_list.getSimulationState() == 'draft':
  packing_list.edit(
    comment = related_order.getComment(),
    title = related_order.getTitle()
  )

# copy order's payment conditions
payment_condition_copy_id_list = related_order.contentIds(filter={'portal_type':'Payment Condition'})
if len(payment_condition_copy_id_list) > 0:
  clipboard = related_order.manage_copyObjects(
      ids=payment_condition_copy_id_list)
  packing_list.manage_pasteObjects(clipboard)
