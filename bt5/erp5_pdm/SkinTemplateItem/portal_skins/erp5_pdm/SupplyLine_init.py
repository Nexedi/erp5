# XXX Set a resource for the supply line inside a resource
parent_value = context.getParentValue()
if parent_value.getPortalType() in context.getPortalResourceTypeList():
  context.setResourceValue(parent_value)
# Predicate ?
context.setMappedValuePropertyList([
                    'base_price', 'additional_price',
                    'discount_ratio', 'exclusive_discount_ratio',
                    'surcharge_ratio', 'variable_additional_price',
                    'non_discountable_additional_price',
                    'priced_quantity', 'base_unit_price',
                    'quantity_unit',
])
