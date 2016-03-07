"""
  Find the list of objects to synchronize by calling the catalog.

  Possibly look up a single object based on its ID, GID
"""

payment_transaction_list = []
payment_transaction_append = payment_transaction_list.append

if gid:
  return []

if full:
  return context.getPortalObject().organisation_module.contentValues()

if not id:
  # first get the related integration site
  while context_document.getParentValue().getPortalType() != "Synchronization Tool":
    context_document = context_document.getParentValue()
  site = [x for x in context_document.Base_getRelatedObjectList(portal_type="Integration Module")][0].getParentValue()
  context.log("site %s" % site)

  # then browse list of stc related to the site one
  default_stc = site.getSourceTradeValue()
  for document in default_stc.Base_getRelatedObjectList(portal_type="Sale Trade Condition",
                                                        validation_state="validated"):
    for payment_transaction in document.Base_getRelatedObjectList(portal_type="Payment Transaction",
                                                        simulation_state="confirmed"):
      transaction = payment_transaction.getObject()
      payment_transaction_append(transaction)
else:
  # work on defined payment transaction (id is not None)
  payment_transaction = getattr(context.accounting_module, id)
  if payment_transaction.getSimulationState() != 'confirmed':
    payment_transaction_append(payment_transaction)

return payment_transaction_list
