from Products.ERP5Type.Message import translateString

tag = script.getId()

context.serialize()
if context.getPortalObject().portal_activities.countMessageWithTag(tag):
  return context.Base_redirect(form_id,
                  keep_items={'portal_status_message': translateString("Reconciliation already in progress"),})

context.activate(activity='SQLDict', tag=tag).BankReconciliation_selectNonReconciledTransactionListActive(tag=tag)

context.activate(after_tag=tag, activity='SQLQueue').BankReconciliation_notifySelectNonReconciledFinished()

return context.Base_redirect(form_id,
                  keep_items={'portal_status_message': translateString("Reconciliation in progress"),})
