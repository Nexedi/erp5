portal = context.getPortalObject()
validation_state = context.getValidationState()

if validation_state == "awaiting":
  # Create new Invoice
  connector_value = context.getSourceValue()
  transaction_value = connector_value.getTypeBasedMethod("createInvoice")(
    electronic_invoice=context.getRelativeUrl(),
    destination_section=context.getDestinationSection(),
    reference=context.getTitle(),
    aggregate=context.getRelativeUrl(),
  )
  if context.getAggregate():
    context.getAggregateValue().setFollowUpValue(transaction_value)
  transaction_value.autoPlan()
  context.confirm()
elif validation_state == "confirmed":
  # Sync with Invoice object
  transaction_value = context.getAggregateRelatedValue()
  transaction_value.PurchaseInvoiceTransaction_updateSellerCoordinates()
  if transaction_value.getSimulationState() in portal.getPortalAccountedTransactionStateList():
    context.acknowledge()
  #elif transaction_value.getSimulationState() == "cancelled":
  #  context.reject()
