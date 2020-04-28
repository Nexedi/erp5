if base_application in ('base_amount/loyalty_program/using_point'):
  def getBaseAmountQuantity(delivery_amount, base_application, **kw):
    return 1
  return getBaseAmountQuantity
