packing_list = context
related_order = packing_list.getCausalityValue()

if packing_list.getSimulationState() == 'draft':
  packing_list.edit(
    comment = related_order.getComment(),
    title = related_order.getTitle()
  )
