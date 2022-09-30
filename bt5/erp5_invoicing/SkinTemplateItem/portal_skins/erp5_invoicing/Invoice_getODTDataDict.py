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

excluded_portal_type_list = context.getPortalTaxMovementTypeList() \
                            + context.getPortalAccountingMovementTypeList()

def getSubLineList(obj):
  sub_list = []
  for x in obj.contentValues(portal_type=context.getPortalInvoiceMovementTypeList(),
                             sort_on=[('int_index', 'ascending'), ('reference', 'ascending')],):
    if x.getPortalType() in excluded_portal_type_list:
      continue
    sub_list.append(x)
    sub_list.extend(getSubLineList(x))
  return sub_list

data_dict = context.Delivery_getODTDataDict(reference_method, getSubLineList)

bank_account = context.getDestinationPaymentValue(portal_type='Bank Account')
if context.getPortalType() == 'Sale Invoice Transaction':
  bank_account = context.getSourcePaymentValue(portal_type='Bank Account')

if bank_account is not None:
  data_dict.update(
            bank_name=bank_account.getSourceTitle() or bank_account.getTitle(),
            bank_address=bank_account.getSource() and\
                                bank_account.getSourceValue().getDefaultAddressText() or '',
            bank_account_reference=bank_account.getReference(),
            bank_account_description=bank_account.getDescription() or bank_account.getTitle(),)


return data_dict
