def getSourceReference(line):
  return ""
  category_list = line.getAcquiredCategoryList()
  portal_type_list = ('Purchase Order Line',
                      'Purchase Order Cell',)
  tmp_context = line.asContext(context=line, categories=category_list)
  predicate_list = context.portal_domains.searchPredicateList(tmp_context, portal_type=portal_type_list)
  for predicate in predicate_list:
    source_reference = predicate.getSourceReference()
    if source_reference:
     return source_reference
  return ''

def getDestinationReference(line):
  return ""
  category_list = line.getAcquiredCategoryList()
  portal_type_list = ('Sale Order Line',
                      'Sale Order Cell',)
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

excluded_portal_type_list = context.getPortalTaxMovementTypeList() \
                            + context.getPortalAccountingMovementTypeList()

def getSubLineList(obj):
  sub_list = []
  for x in obj.contentValues(portal_type=context.getPortalOrderMovementTypeList(),
                             sort_on=[('int_index', 'ascending'), ('reference', 'ascending')],
                             checked_permission='View'):
    if x.getPortalType() in excluded_portal_type_list:
      continue
    sub_list.append(x)
    sub_list.extend(getSubLineList(x))
  return sub_list

data_dict = context.Delivery_getODTDataDict(reference_method, getSubLineList)

data_dict["total_discount"] = context.SaleOrder_getTotalDiscount()

data_dict["total_price_with_discount"] = context.SaleOrder_getFinalPrice()

return data_dict
