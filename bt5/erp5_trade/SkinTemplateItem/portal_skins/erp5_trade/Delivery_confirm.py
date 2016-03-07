if REQUEST is not None:
  from zExceptions import Unauthorized
  raise Unauthorized(script.id)

if context.getSimulationState() == "draft":
  from Products.ERP5Type.Message import translateString
  context.confirm(comment=translateString('Initialised by Delivery Builder.'))
