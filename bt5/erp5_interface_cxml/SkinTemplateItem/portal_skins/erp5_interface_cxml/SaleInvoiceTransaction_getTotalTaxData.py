total_quantity=0
total_price=0
description_text=''
for tax in line_tax:
  total_quantity+=tax["total_quantity"]
  total_price+=tax["total_price"]
  base_price=tax["base_price"]
  description_text=tax["description_text"] or description_text
return [{"total_quantity":total_quantity,
        "total_price":total_price,
        "base_price":base_price,
        "description_text":description_text}]
