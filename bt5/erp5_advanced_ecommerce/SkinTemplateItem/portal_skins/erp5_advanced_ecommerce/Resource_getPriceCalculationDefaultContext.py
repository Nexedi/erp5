"""
  Create a temporary movement with properties and categories
  needed to provide a default price for a given resource

  TODO:
  - add support to input parameters (**kw) so that it
    is possible specialize price calculation
  - support alt default currency
"""

# Try to find out the current web site
web_site_value = context.REQUEST.get('current_web_site', None)
if web_site_value is None:
  web_site_value = context.getWebSiteValue()

# If this resource is variated, initialize the default
# variation context
variation_dict = {}
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

if date is None:
  variation_dict["start_date"] = DateTime()
  variation_dict["stop_date"] = DateTime()+0.00001
else:
  variation_dict["start_date"] = date
  variation_dict["stop_date"] = date+0.00001

price_currency_value = web_site_value.WebSite_getShoppingCartDefaultCurrency()

movement = context.newContent(
    temp_object=True,
    portal_type='Movement',
    id="temp_pricing_movement", resource_value=context,
                           price_currency_value=price_currency_value,
                           **variation_dict)
return movement
