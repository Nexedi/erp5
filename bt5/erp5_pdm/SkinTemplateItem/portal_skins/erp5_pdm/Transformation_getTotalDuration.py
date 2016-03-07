if selection_name is not None:

  reference_variation_category_list = context.portal_selections.getSelectionParamsFor(selection_name)['reference_variation_category_list']
  from Products.ERP5Type.Document import newTempAmount
  tmp_context = newTempAmount(context, "temp_context",
                              quantity=1.0,
                              variation_category_list=reference_variation_category_list,
                              resource=context.getRelativeUrl()) 
   
  aal = context.getAggregatedAmountList(tmp_context)

  result = aal.getTotalDuration()
  return result


else:
  return None
