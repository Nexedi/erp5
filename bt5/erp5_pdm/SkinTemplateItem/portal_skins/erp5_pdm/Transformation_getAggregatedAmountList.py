tmp_context = context.newContent(
    id="temp_context",
    portal_type="Amount",
    temp_object=True,
    quantity=1.0,
    variation_category_list=reference_variation_category_list,
    resource=context.getResource())
price_currency = kw.get('price_currency', None)

result = context.getAggregatedAmountList(tmp_context)
for line in result:
  resource = line.getResourceValue()
  if resource is not None:
    sender = line.getResourceValue().getPurchaseSupplyLineSource()
    line.setCategoryMembership('source', sender)
  line.setCategoryMembership('price_currency', price_currency)

return result
