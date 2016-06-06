<?xml version="1.0"?>
<ZopeData>
  <record id="1" aka="AAAAAAAAAAE=">
    <pickle>
      <global name="PythonScript" module="Products.PythonScripts.PythonScript"/>
    </pickle>
    <pickle>
      <dictionary>
        <item>
            <key> <string>Script_magic</string> </key>
            <value> <int>3</int> </value>
        </item>
        <item>
            <key> <string>_bind_names</string> </key>
            <value>
              <object>
                <klass>
                  <global name="NameAssignments" module="Shared.DC.Scripts.Bindings"/>
                </klass>
                <tuple/>
                <state>
                  <dictionary>
                    <item>
                        <key> <string>_asgns</string> </key>
                        <value>
                          <dictionary>
                            <item>
                                <key> <string>name_container</string> </key>
                                <value> <string>container</string> </value>
                            </item>
                            <item>
                                <key> <string>name_context</string> </key>
                                <value> <string>context</string> </value>
                            </item>
                            <item>
                                <key> <string>name_m_self</string> </key>
                                <value> <string>script</string> </value>
                            </item>
                            <item>
                                <key> <string>name_subpath</string> </key>
                                <value> <string>traverse_subpath</string> </value>
                            </item>
                          </dictionary>
                        </value>
                    </item>
                  </dictionary>
                </state>
              </object>
            </value>
        </item>
        <item>
            <key> <string>_body</string> </key>
            <value> <string encoding="cdata"><![CDATA[

# This script returns a list of resources that we can find in a particular stock point.\n
# - vault : the stock we are intested in\n
# - at_date : give the stock for a particular date\n
# - from_date : usefull with at date in order to know the sum of input and output\n
#               between two dates\n
# - excluded_variation_list : Allow to do report with some types of ressources, like\n
#                             [\'cash_status/valid\', \'cash_status/new_not_emitted\']\n
#\n
\n
if dictionaries:\n
  def newTempBase(ignored, object_id, **kw):\n
    kw[\'id\'] = object_id\n
    return kw\n
else:\n
  from Products.ERP5Type.Document import newTempBase\n
\n
#from DateTime import DateTime\n
#begin = DateTime()\n
\n
if from_date is not None:\n
  if from_date == at_date:\n
    from_date=None\n
\n
if only_last_date and vault_report_type==\'history\':\n
  from_date = at_date\n
\n
def getTitleFromCategoryUrl(category):\n
  return context.portal_categories.getCategoryValue(category).getTitle()\n
\n
resource_dict = {}\n
vault_dict = {}\n
vault_inventory_dict = {}\n
\n
portal = context.getPortalObject()\n
\n
\n
\n
vault_url_list = vault\n
if same_type(vault, \'a\'):\n
  vault_url_list = [vault,]\n
#context.log("vault_url_list", vault_url_list)\n
if vault_url_list is None:\n
  raise ValueError, "The vault must be defined"\n
for vault_url in vault_url_list:\n
  vault_dict[vault_url] = 1\n
  vault_inventory_dict[vault_url] = {}\n
 \n
def cartesianProduct(list_of_list):\n
  """\n
    Be carefull : one mathematical property of cartesian product is that\n
    when you do a cartesian products of a set and an empty set, the result\n
    is an empty set.\n
  """\n
  if len(list_of_list) == 0:\n
    return [[]]\n
  result = []\n
  append = result.append\n
  head = list_of_list[0]\n
  tail = list_of_list[1:]\n
  product = cartesianProduct(tail)\n
  for v in head:\n
    for p in product:\n
      append([v] + p)\n
  return result\n
\n
total_inventory_list = []\n
inventory_kw = {}\n
#context.log(\'CounterModule_getVaultTransactionList, vault_report_type\',vault_report_type)\n
if vault_report_type == \'inventory\' and from_date is not None:\n
  raise ValueError, "The from date must be None in the case of inventory"\n
if vault_report_type is None or vault_report_type==\'inventory\':\n
  inventory_kw[\'group_by_variation\'] = 1\n
  inventory_kw[\'group_by_resource\'] = 1\n
# add to get by portal type inventory\n
if kw.has_key("portal_type"):\n
  inventory_kw[\'portal_type\'] = kw[\'portal_type\']\n
if kw.has_key("omit_input"):\n
  inventory_kw[\'omit_input\'] = kw[\'omit_input\']\n
if kw.has_key("omit_output"):\n
  inventory_kw[\'omit_output\'] = kw[\'omit_output\']\n
if kw.has_key("explanation_portal_type"):\n
  inventory_kw[\'explanation_portal_type\'] = kw[\'explanation_portal_type\']\n
if kw.has_key("explanation_uid"):\n
  inventory_kw[\'explanation_uid\'] = kw[\'explanation_uid\']\n
  if len(kw[\'explanation_uid\'])==0:\n
    return total_inventory_list\n
\n
kw_has_cash_status = kw.has_key("cash_status")\n
kw_has_emission_letter = kw.has_key("emission_letter")\n
if kw_has_cash_status or kw_has_emission_letter:\n
  cash_status_list = [None]\n
  emission_letter_list = [None]\n
  if kw_has_cash_status:\n
    cash_status_parameter = kw[\'cash_status\']\n
    if same_type(cash_status_parameter, \'a\'):\n
      cash_status_parameter = [cash_status_parameter]\n
    cash_status_list = ["cash_status/%s%%" % x for x in cash_status_parameter]\n
  if kw_has_emission_letter:\n
    emission_letter_parameter = kw[\'emission_letter\']\n
    if same_type(emission_letter_parameter, \'a\'):\n
      emission_letter_parameter = [emission_letter_parameter]\n
    emission_letter_list = ["emission_letter/%s%%" % x for x in emission_letter_parameter]\n
  full_variation_list_of_list = [cash_status_list, emission_letter_list]\n
  inventory_kw[\'variation_text\'] = []\n
  inv_append = inventory_kw[\'variation_text\'].append\n
  for variation_list in cartesianProduct(full_variation_list_of_list):\n
    variation_text_list = [\'%\']\n
    for variation in variation_list:\n
      if variation is not None:\n
        variation_text_list.append(variation)\n
    variation_text = \'\'.join(variation_text_list)\n
    inv_append(variation_text)\n
\n
if at_date is not None:\n
  # XXX this make sure we look at the end of the day\n
  at_date = at_date + 0.99\n
  inventory_kw[\'at_date\'] = at_date\n
\n
\n
if from_date is not None:\n
  inventory_kw[\'from_date\'] = from_date\n
\n
if column_names == 1:\n
  column_list = [(\'resource\', \'Resource\'), (\'variation_text\', \'Year\')]\n
  column_list.extend([(\'explanation_relative_url\',\'Explanation\')])\n
  for vault in vault_dict.keys():\n
    #context.log(\'getTitleFromCategoryUrl(vault)\',getTitleFromCategoryUrl(vault))\n
    column_list.extend([\n
        (vault + \'_quantity\', getTitleFromCategoryUrl(vault) + \' Quantity\'),\n
        (vault + \'_total_price\', getTitleFromCategoryUrl(vault) + \' TotalPrice\')\n
])\n
  column_list.append((\'general_total_price\', \'General TotalPrice\'))\n
  return column_list\n
\n
#end = DateTime()\n
#context.log(\'before sql time:\',(end-begin)*86400)\n
#context.log(\'node_category\',vault)\n
#context.log(\'inventory_kw\',inventory_kw)\n
display_simulation_state = 0\n
if all_state and vault_report_type==\'history\':\n
  display_simulation_state = 1\n
  vault_inventory_list = context.portal_simulation.getInventoryList( node=vault_url_list\n
                                                                 , ignore_variation=0\n
                                                                 ,**inventory_kw\n
                                                                 )\n
else: \n
  vault_inventory_list = context.portal_simulation.getCurrentInventoryList( node=vault_url_list\n
                                                                 , ignore_variation=0\n
                                                                 ,**inventory_kw\n
                                                                 )\n
#context.log(\'CounterMOdule_getVaultTransactionList, inventory_kw\', inventory_kw)\n
#context.log(\'CounterMOdule_getVaultTransactionList, sql src:\',context.portal_simulation.getCurrentInventoryList( node=vault_url_list\n
#                                                                , ignore_variation=0,src__=1\n
#                                                               ,**inventory_kw\n
#                                                              ))\n
#end = DateTime()\n
#context.log(\'sql request time:\',(end-begin)*86400)\n
\n
if summarise:\n
  total_quantity = 0\n
  total_price = 0\n
  for vault_inventory in vault_inventory_list:\n
    if only_positive:\n
      total_quantity += abs(vault_inventory.total_quantity)\n
      total_price += abs(vault_inventory.total_price)\n
    else:\n
      total_quantity += vault_inventory.total_quantity\n
      total_price += vault_inventory.total_price\n
  return [newTempBase(context, "summary", total_quantity=total_quantity, total_price=total_price), ]\n
\n
explanation_uid_list = []\n
explanation_append = explanation_uid_list.append\n
#context.log(\'len(vault_inventory_list:\',len(vault_inventory_list))\n
for vault_inventory in vault_inventory_list:\n
  node_relative_url = vault_inventory.node_relative_url\n
  if vault_inventory.total_quantity in (0.0,0,None):\n
    continue\n
  #context.log(\'vault_inventory total_quantity\',vault_inventory.total_quantity)\n
  #context.log(\'vault_inventory total_price\',vault_inventory.total_price)\n
  variation_text = vault_inventory.variation_text or \'\'\n
  must_continue = 0\n
  if excluded_variation_list is not None:\n
    for excluded_variation in excluded_variation_list:\n
      if variation_text.find(excluded_variation)>=0:\n
        must_continue = 1\n
        break\n
  if must_continue:\n
    continue\n
  resource = (vault_inventory.resource_relative_url, variation_text)\n
  if vault_report_type==\'history\':\n
    #resource = (vault_inventory.resource_relative_url, vault_inventory.variation_text or \'\',vault_inventory.stock_uid)\n
    explanation_uid = vault_inventory.explanation_uid\n
    explanation_append(explanation_uid)\n
    resource = (vault_inventory.resource_relative_url, variation_text, explanation_uid,\n
                vault_inventory.path)\n
  if not vault_inventory_dict[node_relative_url].has_key(resource):\n
    total_quantity = vault_inventory.total_quantity\n
    if total_quantity is None:\n
      total_quantity = 0\n
    total_price = vault_inventory.total_price\n
    if total_price is None:\n
      total_price = 0\n
    if only_positive:\n
      total_price = abs(total_price)\n
      total_quantity = abs(total_quantity)\n
#     context.log(\'type\',type(total_price))\n
#     context.log(\'sql total_price\',total_price)\n
    vault_inventory_dict[node_relative_url][resource] = {\'quantity\':total_quantity, \'total_price\':total_price,\n
                                                 \'date\':vault_inventory.date}\n
\n
  resource_dict[resource] = 1\n
\n
\n
#end = DateTime()\n
#context.log(\'after first big loop:\',(end-begin)*86400)\n
\n
#context.log(\'resource_dict\',resource_dict)\n
#context.log(\'vault_inventory_dict\',vault_inventory_dict)\n
cache_dict = {}\n
cache_dict[\'cache_explanation\'] = {}\n
\n
if vault_report_type == \'history\':\n
  if len(explanation_uid_list) > 0:\n
    catalog_result_list = context.Base_zGetAllFromCatalog(uid_list=explanation_uid_list)\n
    for line in catalog_result_list:\n
      cache_dict[\'cache_explanation\'][line.uid] = line\n
\n
#end = DateTime()\n
#context.log(\'after getting data into catalog:\',(end-begin)*86400)\n
i = 0\n
\n
append = total_inventory_list.append\n
\n
resource_portal_type_cache_dict = {}\n
for resource in resource_dict.keys():\n
  movement = None\n
  explanation_uid = None\n
  if len(resource)==4: # case of history\n
    #context.log(\'movement uid before error\',resource[2])\n
    #movement = context.portal_catalog.getObject(resource[2])\n
    explanation_uid = resource[2]\n
    movement = resource[3]\n
  resource_url = resource[0]\n
  current_resource_portal_type = resource_portal_type_cache_dict.get(resource_url, None)\n
  if current_resource_portal_type is None:\n
    resource_value = portal.restrictedTraverse(resource_url)\n
    current_resource_portal_type = resource_value.getPortalType()\n
    resource_portal_type_cache_dict[resource_url] = current_resource_portal_type\n
  if current_resource_portal_type not in resource_portal_type:\n
    continue\n
  variation_text = resource[1]\n
  tmp_dict = context.Base_getResourceInformationDictFromUrlAndVariation(\n
           resource_url, variation_text, movement=movement, \n
           display_simulation_state= display_simulation_state,\n
           explanation_uid=explanation_uid,\n
           cache_dict=cache_dict)\n
  #tmp_dict = {}\n
  general_total_price = 0\n
  for vault in vault_dict.keys():\n
    try:\n
      resource_in_vault = vault_inventory_dict[vault][resource]\n
    except KeyError:\n
      # This resource does not exist for this vault\n
      #resource_in_vault = {\'quantity\' : 0,\'total_price\' : 0}\n
      continue\n
    total_quantity = resource_in_vault[\'quantity\']\n
    total_price = resource_in_vault[\'total_price\']\n
    if banknote_quantity_divisor is not None:\n
      if current_resource_portal_type == \'Banknote\':\n
        total_quantity = round(total_quantity / banknote_quantity_divisor,0)\n
        total_price = round(total_price / banknote_quantity_divisor,0)\n
    tmp_dict.update({\'total_quantity\' : total_quantity,\n
        \'quantity\': total_quantity,\n
        \'total_price\' : total_price,})\n
    tmp_dict.update({\'vault\' : vault})\n
    if vault_report_type==\'history\':\n
      tmp_dict.update({\'date\':resource_in_vault[\'date\']})\n
    general_total_price += resource_in_vault[\'total_price\']\n
    tmp_dict[\'general_total_price\'] = general_total_price\n
    #temp_base = newTempBase(context, "new_%03i" % i)\n
    #temp_base = temp_base.asContext(**tmp_dict)\n
    #total_inventory_list.append(temp_base)\n
    #total_inventory_list.append(newTempBase(context, "new_%03i" % i, **tmp_dict))\n
    append(newTempBase(context, "new_%03i" % i, **tmp_dict))\n
    i += 1\n
\n
#end = DateTime()\n
#context.log(\'after second big loop:\',(end-begin)*86400)\n
\n
def sort_base_price(a,b):\n
  return -cmp(a.base_price,b.base_price)\n
\n
#total_inventory_list.sort(sort_base_price)\n
\n
return total_inventory_list\n
\n
\n
return repr([x for x in total_inventory_list])\n


]]></string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>vault=None,at_date=None,from_date=None,vault_report_type=None,column_names=0,resource_portal_type=(\'Banknote\',\'Coin\'), only_positive=0, banknote_quantity_divisor=None, summarise=False, excluded_variation_list=None, all_state=0, only_last_date=0, dictionaries=False, **kw</string> </value>
        </item>
        <item>
            <key> <string>_proxy_roles</string> </key>
            <value>
              <tuple>
                <string>Manager</string>
              </tuple>
            </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>CounterModule_getVaultTransactionList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
