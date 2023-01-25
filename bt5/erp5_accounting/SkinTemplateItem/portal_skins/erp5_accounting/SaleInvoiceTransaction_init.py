if kw.get('created_by_builder', 0):
  return

preference_tool = context.getPortalObject().portal_preferences
context.setSourceSection(preference_tool.getPreferredAccountingTransactionSourceSection())
context.setResource(preference_tool.getPreferredAccountingTransactionCurrency())

if 'Invoice Line' in context.getVisibleAllowedContentTypeList():
  return

context.newContent(portal_type='Sale Invoice Transaction Line',
                   id='income',)
context.newContent(portal_type='Sale Invoice Transaction Line',
                   id='receivable', )
context.newContent(portal_type='Sale Invoice Transaction Line',
                   id='collected_vat',)
