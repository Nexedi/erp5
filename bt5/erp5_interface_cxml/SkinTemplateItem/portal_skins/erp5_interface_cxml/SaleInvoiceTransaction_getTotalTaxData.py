total_quantity=0
total_price=0
for tax in line_tax:
  total_quantity+=tax["total_quantity"]
  total_price+=tax["total_price"]
  base_price=tax["base_price"]
return [{"total_quantity":total_quantity,
        "total_price":total_price,
        "base_price":base_price}]
