def getSourceReference(line):
  category_list = line.getAcquiredCategoryList()
  portal_type_list = ('Purchase Supply Line',
                      'Purchase Supply Cell',
                      'Sale Supply Line',
                      'Sale Supply Cell',)
  tmp_context = line.asContext(context=line, categories=category_list)
  predicate_list = context.portal_domains.searchPredicateList(tmp_context, portal_type=portal_type_list)
  for predicate in predicate_list:
    source_reference = predicate.getSourceReference()
    if source_reference:
      return source_reference
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

data_dict = context.Delivery_getODTDataDict(getSourceReference, getSubLineList)
order = context.getCausalityValue(portal_type=('Sale Order', 'Purchase Order'))
if order is not None:
  order_date = order.getStopDate()
  if context.getPortalType().startswith('Sale'):
    order_date = order.getStartDate()
  data_dict.update(order_reference=order.getReference(),
                   order_date=order_date)
return data_dict
