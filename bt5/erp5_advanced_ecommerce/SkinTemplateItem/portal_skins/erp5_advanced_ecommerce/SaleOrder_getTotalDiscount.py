return round(sum([i.getTotalPrice() for i in context.getAggregatedAmountList(rounding=True)
                       if "base_amount/loyalty_program/discount" in i.getBaseApplicationList() or "base_amount/loyalty_program/coupon" in i.getBaseApplicationList()]), 2)
