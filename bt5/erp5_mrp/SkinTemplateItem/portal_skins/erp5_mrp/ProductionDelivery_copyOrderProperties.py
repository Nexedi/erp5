if context.getSimulationState() == 'draft':
  order = context.getCausalityValue()
  context.edit(
    comment=order.getComment(),
    title=order.getTitle(),
  )

context.Delivery_confirm()
