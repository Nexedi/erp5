from Products.ERP5Type.Message import translateString
obj = state_change['object']
if obj.getValidationState() == 'validated':
  obj.modify()
  container.REQUEST.set(
      'portal_status_message',
      translateString("Errors found in source code"))
  container.REQUEST.set('portal_status_level', 'warning')
