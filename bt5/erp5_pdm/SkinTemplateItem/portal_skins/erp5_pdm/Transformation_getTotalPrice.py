if selection_name is not None:

  reference_variation_category_list = context.portal_selections.getSelectionParamsFor(selection_name)['reference_variation_category_list']
  tmp_context = context.newContent(
      id="temp_context",
      portal_type="Amount",
      temp_object=True,
      quantity=1.0,
      variation_category_list=reference_variation_category_list,
      resource=context.getRelativeUrl())

  price_currency = context.REQUEST.get('price_currency', None)

  aal = context.getAggregatedAmountList(tmp_context)
  for line in aal:
    resource = line.getResourceValue()
    if resource is not None:
      sender = line.getResourceValue().getPurchaseSupplyLineSource()
      line.setCategoryMembership('source', sender)
    line.setCategoryMembership('price_currency', price_currency)

  result = aal.getTotalPrice()
  return result
