from Products.ERP5Type.Message import translateString
types_tool = context.getPortalObject().portal_types
movement_type_list = context.getPortalMovementTypeList()
type_set = {}

for type_name in types_tool.getTypeInfo(context).getTypeAllowedContentTypeList():
  for line_type_name in types_tool.getTypeInfo(type_name).getTypeAllowedContentTypeList():
    if line_type_name in movement_type_list:
      type_set[line_type_name] = 1
    for cell_type_name in types_tool.getTypeInfo(line_type_name).getTypeAllowedContentTypeList():
      if cell_type_name in movement_type_list:
        type_set[cell_type_name] = 1

return [(translateString(t), t) for t in list(type_set.keys())]
