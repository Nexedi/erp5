from past.utils import old_div
if base_application in ('base_amount/loyalty_program/using_point', 'base_amount/loyalty_program/coupon'):
  def getBaseAmountQuantity(delivery_amount, base_application, **kw):
    return old_div(delivery_amount.getTotalPrice(), delivery_amount.getExplanationValue().getTotalPrice())
  return getBaseAmountQuantity
