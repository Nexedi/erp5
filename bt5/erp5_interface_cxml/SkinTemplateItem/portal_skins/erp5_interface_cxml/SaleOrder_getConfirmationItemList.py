from collections import OrderedDict
item_dict = OrderedDict()
for line in context.objectValues(sort_on=[('int_index', 'ascending')],
                                 portal_type='Sale Order Line',
                                 checked_permission='View'):
  if line.SaleOrderLine_isConfirmationItem():
    line_list = item_dict.setdefault(line.getIntIndex(), [])
    line_list.append(line.getObject())

return [{'index': k,
         'order_quantity': v[0].SaleOrderLine_getCxmlOrderQuantity(),
         'line_list': v} for k, v in item_dict.items()]
