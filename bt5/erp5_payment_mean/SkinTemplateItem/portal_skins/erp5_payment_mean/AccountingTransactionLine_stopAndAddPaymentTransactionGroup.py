from Products.ERP5Type.Message import translateString
portal = context.getPortalObject()
payment_transaction_group = portal.restrictedTraverse(aggregate)

payment_transaction = context.getParentValue()
payment_transaction.setDefaultActivateParameterDict({"activate_kw": activate_kw})
if payment_transaction.getSimulationState() == 'planned':
  payment_transaction.Base_workflowStatusModify(
      workflow_action='confirm_action',
      batch_mode=True,
  )

if payment_transaction.getSimulationState() == 'confirmed':
  payment_transaction.Base_workflowStatusModify(
      workflow_action='start_action',
      batch_mode=True,
  )
  payment_transaction.Base_workflowStatusModify(
      workflow_action='stop_action',
      comment=translateString(
          "Posted automatically with payment transaction group ${payment_transaction_group_reference}",
          mapping={'payment_transaction_group_reference': payment_transaction_group.getReference()}),
      batch_mode=True,
  )
  if payment_transaction.getSimulationState() == 'stopped':
    context.AccountingTransactionLine_addPaymentTransactionGroup(
        aggregate=aggregate,
        activate_kw=activate_kw,
    )
