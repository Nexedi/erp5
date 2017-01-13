"""Returns Accounting Transactions related to the Ticket.
"""
return context.getPortalObject().accounting_module.searchFolder(
  strict_causality_uid=context.getUid(),
  )
