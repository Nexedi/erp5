from Products.ERP5Type.Message import translateString
if context.getValidationState() == 'unreachable':
  context.declareReachable(comment=translateString("Assumed reachable after coordinate changed"))
