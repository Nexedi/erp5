# Compute the list of columns to display in the fast input
request = context.REQUEST

resource = request.get('resource',None)
if resource in (None,'None'):
  resource = request.get('field_my_resource',None)
return_list = []
return_list.append(['quantity','Quantity'])
item_model = context.getPortalObject().restrictedTraverse(resource)
if item_model.getPortalType()== 'Check Model':
  if item_model.isAccountNumberEnabled():
    return_list.append(['destination_payment_reference','Account Reference'])
  #if item_model.isQuantityRequired():
  #  return_list.append(['price','Amount'])
  #  return_list.append(['price_currency','Currency'])
  if len(item_model.getVariationRangeCategoryList())>0:
    return_list.append(['check_type','Check Value'])
  return_list.append(['reference_range_min','Start Number'])
  return_list.append(['reference_range_max','Stop Number'])

if item_model.getPortalType()== 'Checkbook Model':
  return_list.append(['destination_payment_reference','Account Reference'])
  return_list.append(['check_amount','Type of Checkbook'])
  return_list.append(['reference_range_min','Start Number'])
  return_list.append(['reference_range_max','Stop Number'])
return return_list
