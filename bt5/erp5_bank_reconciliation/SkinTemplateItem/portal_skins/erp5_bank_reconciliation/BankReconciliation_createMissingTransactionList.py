"""
Runs Payment Transaction builder.
"""

portal = context.getPortalObject()

payment_transaction_builder_value = portal.restrictedTraverse("portal_deliveries/bank_reconciliation_payment_transaction_builder", None)
if payment_transaction_builder_value is None:
  return context.Base_redirect("view", {
    "portal_status_message": context.Base_translateString("Unable to create Payment Transactions from Bank Reconciliation."),
    "portal_status_level": "error",
  })

payment_transaction_builder_value.build()

return context.Base_redirect("view", {
  "portal_status_message": context.Base_translateString("Payment Transaction creation started in the background."),
})
