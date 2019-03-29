# This script returns a list of resources that we can find in a particular stock point.
# - vault : the stock we are intested in
# - at_date : give the stock for a particular date
# - from_date : usefull with at date in order to know the sum of input and output
#               between two dates
# - excluded_variation_list : Allow to do report with some types of ressources, like
#                             ['cash_status/valid', 'cash_status/new_not_emitted']
#

if dictionaries:
  def newTempBase(ignored, object_id, **kw):
    kw['id'] = object_id
    return kw
else:
  from Products.ERP5Type.Document import newTempBase

#from DateTime import DateTime
#begin = DateTime()

if from_date is not None:
  if from_date == at_date:
    from_date=None

if only_last_date and vault_report_type=='history':
  from_date = at_date

def getTitleFromCategoryUrl(category):
  return context.portal_categories.getCategoryValue(category).getTitle()

resource_dict = {}
vault_dict = {}
vault_inventory_dict = {}

portal = context.getPortalObject()



vault_url_list = vault
if same_type(vault, 'a'):
  vault_url_list = [vault,]
#context.log("vault_url_list", vault_url_list)
if vault_url_list is None:
  raise ValueError("The vault must be defined")
for vault_url in vault_url_list:
  vault_dict[vault_url] = 1
  vault_inventory_dict[vault_url] = {}
 
def cartesianProduct(list_of_list):
  """
    Be carefull : one mathematical property of cartesian product is that
    when you do a cartesian products of a set and an empty set, the result
    is an empty set.
  """
  if len(list_of_list) == 0:
    return [[]]
  result = []
  append = result.append
  head = list_of_list[0]
  tail = list_of_list[1:]
  product = cartesianProduct(tail)
  for v in head:
    for p in product:
      append([v] + p)
  return result

total_inventory_list = []
inventory_kw = {}
#context.log('CounterModule_getVaultTransactionList, vault_report_type',vault_report_type)
if vault_report_type == 'inventory' and from_date is not None:
  raise ValueError("The from date must be None in the case of inventory")
if vault_report_type is None or vault_report_type=='inventory':
  inventory_kw['group_by_variation'] = 1
  inventory_kw['group_by_resource'] = 1
# add to get by portal type inventory
if kw.has_key("portal_type"):
  inventory_kw['portal_type'] = kw['portal_type']
if kw.has_key("omit_input"):
  inventory_kw['omit_input'] = kw['omit_input']
if kw.has_key("omit_output"):
  inventory_kw['omit_output'] = kw['omit_output']
if kw.has_key("explanation_portal_type"):
  inventory_kw['explanation_portal_type'] = kw['explanation_portal_type']
if kw.has_key("explanation_uid"):
  inventory_kw['explanation_uid'] = kw['explanation_uid']
  if len(kw['explanation_uid'])==0:
    return total_inventory_list

kw_has_cash_status = kw.has_key("cash_status")
kw_has_emission_letter = kw.has_key("emission_letter")
if kw_has_cash_status or kw_has_emission_letter:
  cash_status_list = [None]
  emission_letter_list = [None]
  if kw_has_cash_status:
    cash_status_parameter = kw['cash_status']
    if same_type(cash_status_parameter, 'a'):
      cash_status_parameter = [cash_status_parameter]
    cash_status_list = ["cash_status/%s%%" % x for x in cash_status_parameter]
  if kw_has_emission_letter:
    emission_letter_parameter = kw['emission_letter']
    if same_type(emission_letter_parameter, 'a'):
      emission_letter_parameter = [emission_letter_parameter]
    emission_letter_list = ["emission_letter/%s%%" % x for x in emission_letter_parameter]
  full_variation_list_of_list = [cash_status_list, emission_letter_list]
  inventory_kw['variation_text'] = []
  inv_append = inventory_kw['variation_text'].append
  for variation_list in cartesianProduct(full_variation_list_of_list):
    variation_text_list = ['%']
    for variation in variation_list:
      if variation is not None:
        variation_text_list.append(variation)
    variation_text = ''.join(variation_text_list)
    inv_append(variation_text)

if at_date is not None:
  # XXX this make sure we look at the end of the day
  at_date = at_date + 0.99
  inventory_kw['at_date'] = at_date


if from_date is not None:
  inventory_kw['from_date'] = from_date

if column_names == 1:
  column_list = [('resource', 'Resource'), ('variation_text', 'Year')]
  column_list.extend([('explanation_relative_url','Explanation')])
  for vault in vault_dict.keys():
    #context.log('getTitleFromCategoryUrl(vault)',getTitleFromCategoryUrl(vault))
    column_list.extend([
        (vault + '_quantity', getTitleFromCategoryUrl(vault) + ' Quantity'),
        (vault + '_total_price', getTitleFromCategoryUrl(vault) + ' TotalPrice')
])
  column_list.append(('general_total_price', 'General TotalPrice'))
  return column_list

#end = DateTime()
#context.log('before sql time:',(end-begin)*86400)
#context.log('node_category',vault)
#context.log('inventory_kw',inventory_kw)
display_simulation_state = 0
if all_state and vault_report_type=='history':
  display_simulation_state = 1
  vault_inventory_list = context.portal_simulation.getInventoryList( node=vault_url_list
                                                                 , ignore_variation=0
                                                                 ,**inventory_kw
                                                                 )
else: 
  vault_inventory_list = context.portal_simulation.getCurrentInventoryList( node=vault_url_list
                                                                 , ignore_variation=0
                                                                 ,**inventory_kw
                                                                 )
#context.log('CounterMOdule_getVaultTransactionList, inventory_kw', inventory_kw)
#context.log('CounterMOdule_getVaultTransactionList, sql src:',context.portal_simulation.getCurrentInventoryList( node=vault_url_list
#                                                                , ignore_variation=0,src__=1
#                                                               ,**inventory_kw
#                                                              ))
#end = DateTime()
#context.log('sql request time:',(end-begin)*86400)

if summarise:
  total_quantity = 0
  total_price = 0
  for vault_inventory in vault_inventory_list:
    if only_positive:
      total_quantity += abs(vault_inventory.total_quantity)
      total_price += abs(vault_inventory.total_price)
    else:
      total_quantity += vault_inventory.total_quantity
      total_price += vault_inventory.total_price
  return [newTempBase(context, "summary", total_quantity=total_quantity, total_price=total_price), ]

explanation_uid_list = []
explanation_append = explanation_uid_list.append
#context.log('len(vault_inventory_list:',len(vault_inventory_list))
for vault_inventory in vault_inventory_list:
  node_relative_url = vault_inventory.node_relative_url
  if vault_inventory.total_quantity in (0.0,0,None):
    continue
  #context.log('vault_inventory total_quantity',vault_inventory.total_quantity)
  #context.log('vault_inventory total_price',vault_inventory.total_price)
  variation_text = vault_inventory.variation_text or ''
  must_continue = 0
  if excluded_variation_list is not None:
    for excluded_variation in excluded_variation_list:
      if variation_text.find(excluded_variation)>=0:
        must_continue = 1
        break
  if must_continue:
    continue
  resource = (vault_inventory.resource_relative_url, variation_text)
  if vault_report_type=='history':
    #resource = (vault_inventory.resource_relative_url, vault_inventory.variation_text or '',vault_inventory.stock_uid)
    explanation_uid = vault_inventory.explanation_uid
    explanation_append(explanation_uid)
    resource = (vault_inventory.resource_relative_url, variation_text, explanation_uid,
                vault_inventory.path)
  if not vault_inventory_dict[node_relative_url].has_key(resource):
    total_quantity = vault_inventory.total_quantity
    if total_quantity is None:
      total_quantity = 0
    total_price = vault_inventory.total_price
    if total_price is None:
      total_price = 0
    if only_positive:
      total_price = abs(total_price)
      total_quantity = abs(total_quantity)
#     context.log('type',type(total_price))
#     context.log('sql total_price',total_price)
    vault_inventory_dict[node_relative_url][resource] = {'quantity':total_quantity, 'total_price':total_price,
                                                 'date':vault_inventory.date}

  resource_dict[resource] = 1


#end = DateTime()
#context.log('after first big loop:',(end-begin)*86400)

#context.log('resource_dict',resource_dict)
#context.log('vault_inventory_dict',vault_inventory_dict)
cache_dict = {}
cache_dict['cache_explanation'] = {}

if vault_report_type == 'history':
  if len(explanation_uid_list) > 0:
    catalog_result_list = context.Base_zGetAllFromCatalog(uid_list=explanation_uid_list)
    for line in catalog_result_list:
      cache_dict['cache_explanation'][line.uid] = line

#end = DateTime()
#context.log('after getting data into catalog:',(end-begin)*86400)
i = 0

append = total_inventory_list.append

resource_portal_type_cache_dict = {}
for resource in resource_dict.keys():
  movement = None
  explanation_uid = None
  if len(resource)==4: # case of history
    #context.log('movement uid before error',resource[2])
    #movement = context.portal_catalog.getObject(resource[2])
    explanation_uid = resource[2]
    movement = resource[3]
  resource_url = resource[0]
  current_resource_portal_type = resource_portal_type_cache_dict.get(resource_url, None)
  if current_resource_portal_type is None:
    resource_value = portal.restrictedTraverse(resource_url)
    current_resource_portal_type = resource_value.getPortalType()
    resource_portal_type_cache_dict[resource_url] = current_resource_portal_type
  if current_resource_portal_type not in resource_portal_type:
    continue
  variation_text = resource[1]
  tmp_dict = context.Base_getResourceInformationDictFromUrlAndVariation(
           resource_url, variation_text, movement=movement, 
           display_simulation_state= display_simulation_state,
           explanation_uid=explanation_uid,
           cache_dict=cache_dict)
  #tmp_dict = {}
  general_total_price = 0
  for vault in vault_dict.keys():
    try:
      resource_in_vault = vault_inventory_dict[vault][resource]
    except KeyError:
      # This resource does not exist for this vault
      #resource_in_vault = {'quantity' : 0,'total_price' : 0}
      continue
    total_quantity = resource_in_vault['quantity']
    total_price = resource_in_vault['total_price']
    if banknote_quantity_divisor is not None:
      if current_resource_portal_type == 'Banknote':
        total_quantity = round(total_quantity / banknote_quantity_divisor,0)
        total_price = round(total_price / banknote_quantity_divisor,0)
    tmp_dict.update({'total_quantity' : total_quantity,
        'quantity': total_quantity,
        'total_price' : total_price,})
    tmp_dict.update({'vault' : vault})
    if vault_report_type=='history':
      tmp_dict.update({'date':resource_in_vault['date']})
    general_total_price += resource_in_vault['total_price']
    tmp_dict['general_total_price'] = general_total_price
    #temp_base = newTempBase(context, "new_%03i" % i)
    #temp_base = temp_base.asContext(**tmp_dict)
    #total_inventory_list.append(temp_base)
    #total_inventory_list.append(newTempBase(context, "new_%03i" % i, **tmp_dict))
    append(newTempBase(context, "new_%03i" % i, **tmp_dict))
    i += 1

#end = DateTime()
#context.log('after second big loop:',(end-begin)*86400)

def sort_base_price(a,b):
  return -cmp(a.base_price,b.base_price)

#total_inventory_list.sort(sort_base_price)

return total_inventory_list


return repr([x for x in total_inventory_list])
