def getSourceReference(line):
  return ''

def getSubLineList(obj):
  sub_list = []
  for x in obj.contentValues(portal_type=context.getPortalDeliveryMovementTypeList(),
      sort_on=[('int_index', 'ascending'), ('reference', 'ascending')]):
    if x.getPortalType() in obj.getPortalTaxMovementTypeList():
      continue
    sub_list.append(x)
    sub_list.extend(getSubLineList(x))
  return sub_list

return context.Delivery_getODTDataDict(getSourceReference, getSubLineList)
