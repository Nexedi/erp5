#if context.getPortalType() == 'Container Line' :
#   category_list = (('variation',),)
#context.log(context.getPath(), base_category)
if base_category != None and base_category in context.getVariationBaseCategoryList():
  variation_list = []
  for category_item in context.getVariationCategoryItemList():
    category = category_item[1]
    title    = category_item[0]
    if same_type(title, ''):
      title = context.Localizer.erp5_ui.gettext(title)
    if category.startswith(base_category + '/'):
      variation_list.append((category, title))
  return variation_list

base_category_list = (('emission_letter',),('variation',),('cash_status',))
variation_category_list = context.getVariationCategoryList()  #('emission/letter/c','cash_status/valid','variation/2003')
cash_line_list = []
for base_category in base_category_list :
  cash_line_list.append([x for x in context.OrderLine_getMatrixItemList(base_category) if x in variation_category_list])
#context.log("cash line list", str((cash_line_list, base_category_list, variation_category_list, context.OrderLine_getMatrixItemList(base_category))))
return cash_line_list
