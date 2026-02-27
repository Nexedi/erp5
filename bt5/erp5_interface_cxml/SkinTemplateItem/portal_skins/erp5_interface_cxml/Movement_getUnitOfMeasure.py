order = context.getParentValue().Order_getRelatedOrderRequestValue()
line_dict = order.getLinePropertyDict()[context.getIntIndex()]
return line_dict['cxml_quantity_unit']

#default = "EA"
#mapping_dict = {
#  "unit/piece": "EA"
#}
#quanity_unit = context.getQuantityUnit()
#return mapping_dict.get(quanity_unit, default)
