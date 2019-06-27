from math import log

result = context.getPriceParameterDict(context=movement, **kw)
# XXX: Add "stepped_price" in calculation
# sliced_base_price = {'price': 10.0, 'sliced_range': (1, None)}

# Calculate
#     ((base_price + SUM(additional_price) +
#     variable_value * SUM(variable_additional_price)) *
#     (1 - MIN(1, MAX(SUM(discount_ratio) , exclusive_discount_ratio ))) +
#     SUM(non_discountable_additional_price)) *
#     (1 + SUM(surcharge_ratio))
#     Or, as (nearly) one single line :
#     ((bp + S(ap) + v * S(vap))
#       * (1 - m(1, M(S(dr), edr)))
#       + S(ndap))
#     * (1 + S(sr))
# Variable value is dynamically configurable through a python script.
# It can be anything, depending on business requirements.
# It can be seen as a way to define a pricing model that not only
# depends on discrete variations, but also on a continuous property
# of the object
if result["sliced_base_price"]:
  total_price = 0.
  quantity = movement.getQuantity()
  sliced_base_price_list = zip(result["sliced_base_price"], result["sliced_range"])
  for slice_price, slice_range in sliced_base_price_list:
    slice_min, slice_max = slice_range
    if slice_max is None:
      slice_max = quantity + 1
    if slice_min is None:
      slice_min = 1
    priced_quantity = min(slice_max - 1, quantity) - (slice_min - 1)
    total_price += priced_quantity * slice_price
  result["base_price"] = round(total_price / quantity, int(round(- log(result['base_unit_price'], 10),0)))

base_price = result["base_price"]
if base_price in (None, ""):
  # XXX Compatibility
  # base_price must not be defined on resource
  base_price = context.getBasePrice()
  if base_price in (None, ""):
    return {"price": default,
            "base_unit_price": result.get('base_unit_price')}

for x in ("additional_price",
          "variable_additional_price",
          "discount_ratio",
          "non_discountable_additional_price",
          "surcharge_ratio"):
  result[x] = sum(result[x])

unit_base_price = result["variable_additional_price"]
if unit_base_price:
  method = None if movement is None else \
           movement.getTypeBasedMethod("getPricingVariable")
  if method is None:
    method = context.getTypeBasedMethod("getPricingVariable")
  if method is None:
    unit_base_price = 0
  else:
    unit_base_price *= method()

unit_base_price += base_price + result["additional_price"]

# Discount
d_ratio = max(result["discount_ratio"], result['exclusive_discount_ratio'] or 0)
if d_ratio > 0:
  unit_base_price *= max(0, 1 - d_ratio)

# Sum non discountable additional price
unit_base_price += result['non_discountable_additional_price']

# Surcharge ratio
unit_base_price *= 1 + result["surcharge_ratio"]

# Divide by the priced quantity
priced_quantity = result['priced_quantity']
if priced_quantity:
  unit_base_price /= priced_quantity

result["price"] = unit_base_price
return result
