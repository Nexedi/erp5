if kw.get('created_by_builder', 0):
  return

preference_tool = context.getPortalObject().portal_preferences
context.setDestinationSection(preference_tool.getPreferredAccountingTransactionSourceSection())
context.setResource(preference_tool.getPreferredAccountingTransactionCurrency())

if 'Invoice Line' in context.getVisibleAllowedContentTypeList():
  return

context.newContent(portal_type='Purchase Invoice Transaction Line',
                   id='expense', )
context.newContent(portal_type='Purchase Invoice Transaction Line',
                   id='payable', )
context.newContent(portal_type='Purchase Invoice Transaction Line',
                   id='refundable_vat', )
