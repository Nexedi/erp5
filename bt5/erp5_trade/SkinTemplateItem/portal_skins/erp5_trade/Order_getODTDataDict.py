def getSourceReference(line):
  category_list = line.getAcquiredCategoryList()
  portal_type_list = ('Purchase Supply Line',
                      'Purchase Supply Cell',)
  tmp_context = line.asContext(context=line, categories=category_list)
  predicate_list = context.portal_domains.searchPredicateList(tmp_context, portal_type=portal_type_list)
  for predicate in predicate_list:
    source_reference = predicate.getSourceReference()
    if source_reference:
      return source_reference
  return ''

def getDestinationReference(line):
  category_list = line.getAcquiredCategoryList()
  portal_type_list = ('Sale Supply Line',
                      'Sale Supply Cell',)
  tmp_context = line.asContext(context=line, categories=category_list)
  predicate_list = context.portal_domains.searchPredicateList(tmp_context, portal_type=portal_type_list)
  for predicate in predicate_list:
    destination_reference = predicate.getDestinationReference()
    if destination_reference:
      return destination_reference
  return ''

#if context.getPortalType() in context.getPortalSaleTypeList():
if 'Sale' in context.getPortalType():
  reference_method = getDestinationReference
else:
  reference_method = getSourceReference

def getSubLineList(obj):
  sub_list = []
  for x in obj.contentValues(portal_type=context.getPortalOrderMovementTypeList(),
                             sort_on=[('int_index', 'ascending'), ('reference', 'ascending')]):
    if x.getPortalType() in obj.getPortalTaxMovementTypeList():
      continue
    sub_list.append(x)
    sub_list.extend(getSubLineList(x))
  return sub_list

return context.Delivery_getODTDataDict(reference_method, getSubLineList)
