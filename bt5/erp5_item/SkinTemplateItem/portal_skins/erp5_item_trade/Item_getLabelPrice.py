def getContext(context):
  from Products.ERP5Type.Document import newTempMovement
  # If this resource is variated, initialize the default
  # variation context
  variation_dict = {
    'start_date': DateTime(),
    'stop_date': DateTime() + 0.00001
  }

  if len(context.getVariationRangeCategoryList()):
    request = context.REQUEST
    # Set each category of variation either to the default value
    # or to the value provided by the REQUEST object
    for variation_base_category in context.getVariationBaseCategoryList():
      default_variation = context.getVariationCategoryList(base_category_list=[variation_base_category])
      # circumvent inconsistency for individual variations
      default_variation = default_variation or \
        context.getVariationRangeCategoryList(base_category_list=[variation_base_category])
      if len(default_variation):
        default_variation = default_variation[0]
        variation_category = request.get(variation_base_category, default_variation)
        variation_dict[variation_base_category] = variation_category

  price_currency_value = context.getPriceCurrencyValue()
  movement = newTempMovement(context, "temp_pricing_movement", resource_value=context,
                           price_currency_value=price_currency_value,
                           **variation_dict)
  return movement

price = resource.getPrice(context=getContext(resource), supply_path_type=supply_path_type)
currency = resource.restrictedTraverse(resource.getSaleSupplyLinePriceCurrency()).getReference()

size_title = ""
variation_range_list = context.Item_getVariationRangeCategoryItemList()

for variation in context.Item_getVariationCategoryList():
  if variation.startswith("size"):
    variation_title_list = [i[0] for i in variation_range_list if i[1] == variation]
    if len(variation_title_list):
      size_title = variation_title_list[0]
      break

if price is not None:
  price_label = '%s %s' % (price, currency)
else:
  price_label = ""

total = len(price_label) + 9 + len(size_title)

return price_label[0:len(price_label)*24 / total ] + ' - SIZE: ' +  size_title[0:len(size_title)*24 / total ]
