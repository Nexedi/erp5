portal = context.getPortalObject()
validation_state = context.getValidationState()

if validation_state == "awaiting":
  # Create new Invoice
  connector_value = context.getSourceValue()
  connector_value.getTypeBasedMethod("createInvoice")(
    electronic_invoice=context.getRelativeUrl(),
    source_section=context.getSourceSection(),
    destination_section=context.getDestinationSection(),
    reference=context.getTitle(),
    aggregate=context.getRelativeUrl(),
  )
  context.confirm()
elif validation_state == "confirmed":
  # Sync with Invoice object
  transaction_value = context.getAggregateRelatedValue()
  if not context.hasSourceSection() and \
      transaction_value.hasSourceSection():
    context.setSourceSection(transaction_value.getSourceSection())

  if transaction_value.getSimulationState() in portal.getPortalAccountedTransactionStateList():
    context.acknowledge()
  #elif transaction_value.getSimulationState() == "cancelled":
  #  context.reject()
