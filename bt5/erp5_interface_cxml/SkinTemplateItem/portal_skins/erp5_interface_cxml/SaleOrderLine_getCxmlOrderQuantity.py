order = context.getParentValue().Order_getRelatedOrderRequestValue()
line_dict = order.getLinePropertyDict()[context.getIntIndex()]
return line_dict['quantity']
