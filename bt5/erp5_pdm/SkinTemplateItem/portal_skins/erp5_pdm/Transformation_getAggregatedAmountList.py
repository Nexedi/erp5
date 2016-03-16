from Products.ERP5Type.Document import newTempAmount
tmp_context = newTempAmount(context, "temp_context",
                            quantity=1.0,
                            variation_category_list=reference_variation_category_list,
                            resource=context.getRelativeUrl()) 
price_currency = kw.get('price_currency', None)

result = context.getAggregatedAmountList(tmp_context)
final_result = []
for line in result:
  resource = line.getResourceValue()
  sender_value = None
  if resource is not None:
    sender = line.getResourceValue().getPurchaseSupplyLineSource()
  line.setCategoryMembership('source', sender)
  line.setCategoryMembership('price_currency', price_currency)

return result
