if kw.get('created_by_builder', 0):
  return

preference_tool = context.getPortalObject().portal_preferences
context.setSourceSection(preference_tool.getPreferredAccountingTransactionSourceSection())
context.setResource(preference_tool.getPreferredAccountingTransactionCurrency())

context.newContent(portal_type='Accounting Transaction Line',
                   id='receivable')
context.newContent(portal_type='Accounting Transaction Line',
                   id='payable')
context.newContent(portal_type='Accounting Transaction Line',
                   id='bank')
