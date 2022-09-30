if selection_name is not None:
  reference_variation_category_list = context.portal_selections.getSelectionParamsFor(selection_name)['reference_variation_category_list']
  tmp_context = context.newContent(
      id="temp_context",
      portal_type="Amount",
      temp_object=True,
      quantity=1.0,
      variation_category_list=reference_variation_category_list,
      resource=context.getRelativeUrl())
  aal = context.getAggregatedAmountList(tmp_context)
  result = aal.getTotalDuration()
  return result
