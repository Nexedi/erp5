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

from Products.PythonScripts.standard import Object\n
from json import loads\n
\n
portal = context.getPortalObject()\n
\n
request = container.REQUEST\n
report_group_by = request.get(\'group_by\', None)\n
active_process_path = request.get(\'active_process\')\n
\n
# We have to sum product_dict and client_dict from the results of active process\n
def _addDict(global_dict, local_dict, only_amount=False):\n
  if report_group_by == "both" and not only_amount:\n
    # we have client -> product -> period -> amount\n
    for local_title, local_product_dict in local_dict.iteritems():\n
      product_dict = global_dict.setdefault(local_title, {})\n
      for local_product, local_period_dict in local_product_dict.iteritems():\n
        period_dict = product_dict.setdefault(local_product, {})\n
        for period, local_amount_dict in local_period_dict.iteritems():\n
          amount_dict = period_dict.setdefault(period, {\'amount\' : 0, \'quantity\' : 0, \'quantity_unit\' : \'\'})\n
          amount_dict[\'amount\'] = amount_dict[\'amount\'] + local_amount_dict[\'amount\']\n
          amount_dict[\'quantity\'] = amount_dict[\'quantity\'] + local_amount_dict[\'quantity\']\n
          amount_dict[\'quantity_unit\'] = local_amount_dict[\'quantity_unit\']\n
  else:\n
    # We have client or product -> period -> amount\n
    for local_title, local_period_dict in local_dict.iteritems():\n
      period_dict = global_dict.setdefault(local_title, {})\n
      for period, local_amount_dict in local_period_dict.iteritems():\n
        amount_dict = period_dict.setdefault(period, {\'amount\' : 0, \'quantity\' : 0, \'quantity_unit\' : \'\'})\n
        amount_dict[\'amount\'] = amount_dict[\'amount\'] + local_amount_dict[\'amount\']\n
        if not only_amount:\n
          amount_dict[\'quantity\'] = amount_dict[\'quantity\'] + local_amount_dict[\'quantity\']\n
          amount_dict[\'quantity_unit\'] = local_amount_dict[\'quantity_unit\']\n
\n
product_dict = {}\n
client_dict = {}\n
if active_process_path:\n
  active_process = portal.restrictedTraverse(active_process_path)\n
  for result in active_process.getResultList():\n
    if result.summary:\n
      continue\n
    detail = loads(result.detail)\n
    if detail[\'type\'] == "result":\n
      result_product_dict = detail[\'product_dict\']\n
      result_client_dict = detail["client_dict"]  \n
    else:\n
      continue\n
    if not len(client_dict) and len(result_client_dict):\n
      client_dict = result_client_dict.copy()\n
    else:\n
      _addDict(client_dict, result_client_dict, only_amount=True)\n
    \n
    if not len(product_dict) and len(result_product_dict):\n
      product_dict = result_product_dict.copy()\n
    else:\n
      _addDict(product_dict, result_product_dict)\n
else:\n
  raise ValueError("No active process found to process report")\n
\n
def sortProduct(a, b):\n
  return cmp(a[\'product\'], b[\'product\'])\n
\n
period_counter_dict = {}\n
line_list = []\n
append = line_list.append\n
extend = line_list.extend\n
# we build lines for listbox\n
if len(client_dict):\n
  # third party or third party + products\n
  for client_title in client_dict.keys():\n
    # lines for third party\n
    obj = Object(uid="new_")\n
    obj[\'client\'] = client_title\n
    line_total_amount = 0\n
    for period in period_list:\n
      # client -> period\n
      if client_dict[client_title].has_key(period):\n
        obj[\'Amount %s\' %(period)] = round(client_dict[client_title][period][\'amount\'], 2)\n
        line_total_amount += client_dict[client_title][period][\'amount\']\n
        if report_group_by == "client":\n
          if period_counter_dict.has_key(\'Amount %s\' %(period)):\n
            period_counter_dict[\'Amount %s\' %(period)] = period_counter_dict[\'Amount %s\' %(period)] + client_dict[client_title][period][\'amount\']\n
          else:\n
            period_counter_dict[\'Amount %s\' %(period)] = client_dict[client_title][period][\'amount\']\n
      else:\n
        obj[\'Amount %s\' %(period)] = 0\n
    obj[\'total amount\'] = round(line_total_amount, 2)\n
    if report_group_by == "client":\n
      if period_counter_dict.has_key(\'total amount\'):\n
        period_counter_dict[\'total amount\'] = period_counter_dict[\'total amount\'] + line_total_amount\n
      else:\n
        period_counter_dict[\'total amount\'] = line_total_amount\n
\n
    append(obj)\n
    if report_group_by == "both":\n
      product_lines_list = []\n
      # one line per product\n
      if product_dict.has_key(client_title):\n
        line_product_dict = product_dict[client_title]\n
        for product_title in line_product_dict.keys():\n
          obj = Object(uid="new_")\n
          obj[\'product\'] = product_title\n
          line_total_amount = 0\n
          line_total_quantity = 0\n
          for period in period_list:\n
            if line_product_dict[product_title].has_key(period):\n
              obj[\'Amount %s\' %(period)] = round(line_product_dict[product_title][period][\'amount\'], 2)\n
              obj[\'Quantity %s\' %(period)] = line_product_dict[product_title][period][\'quantity\']\n
              obj[\'Quantity Unit %s\' %(period)] = line_product_dict[product_title][period][\'quantity_unit\']\n
              # total columns\n
              line_total_amount += line_product_dict[product_title][period][\'amount\']\n
              line_total_quantity += line_product_dict[product_title][period][\'quantity\']\n
              # counter for stat line\n
              if period_counter_dict.has_key(\'Amount %s\' %(period)):\n
                period_counter_dict[\'Amount %s\' %(period)] = period_counter_dict[\'Amount %s\' %(period)] + \\\n
                                                             line_product_dict[product_title][period][\'amount\']\n
              else:\n
                period_counter_dict[\'Amount %s\' %(period)] = line_product_dict[product_title][period][\'amount\']\n
              \n
            else:\n
              obj[\'Amount %s\' %(period)] = 0\n
              obj[\'Quantity %s\' %(period)] = 0\n
              obj[\'Quantity Unit %s\' %(period)] = ""\n
          \n
          obj[\'total quantity\'] = line_total_quantity\n
          obj[\'total amount\'] = round(line_total_amount, 2)\n
          # total for stat line\n
          if period_counter_dict.has_key(\'total amount\'):\n
            period_counter_dict[\'total amount\'] = period_counter_dict[\'total amount\'] + line_total_amount\n
          else:\n
            period_counter_dict[\'total amount\'] = line_total_amount\n
\n
          product_lines_list.append(obj)\n
      # sort product list\n
      product_lines_list.sort(sortProduct)\n
      extend(product_lines_list)\n
else:\n
  # products\n
  if report_group_by == "product":\n
    for product_title in product_dict.keys():\n
      obj = Object(uid="new_")\n
      obj[\'product\'] = product_title\n
      line_total_amount = 0\n
      line_total_quantity = 0    \n
      for period in period_list:\n
        if product_dict[product_title].has_key(period):\n
          obj[\'Amount %s\' %(period)] = round(product_dict[product_title][period][\'amount\'],2)\n
          obj[\'Quantity %s\' %(period)] = product_dict[product_title][period][\'quantity\']\n
          obj[\'Quantity Unit %s\' %(period)] = product_dict[product_title][period][\'quantity_unit\']\n
          # total column\n
          line_total_amount += product_dict[product_title][period][\'amount\']\n
          line_total_quantity += product_dict[product_title][period][\'quantity\']\n
          # counter for stat line\n
          if period_counter_dict.has_key(\'Amount %s\' %(period)):\n
            period_counter_dict[\'Amount %s\' %(period)] = period_counter_dict[\'Amount %s\' %(period)] + product_dict[product_title][period][\'amount\']\n
          else:\n
            period_counter_dict[\'Amount %s\' %(period)] = product_dict[product_title][period][\'amount\']\n
        else:\n
          obj[\'Amount %s\' %(period)] = 0\n
          obj[\'Quantity %s\' %(period)] = 0\n
          obj[\'Quantity Unit %s\' %(period)] = ""\n
\n
      obj[\'total quantity\'] = line_total_quantity\n
      obj[\'total amount\'] = round(line_total_amount,2)\n
      # total for stat line\n
      if period_counter_dict.has_key(\'total amount\'):\n
        period_counter_dict[\'total amount\'] = period_counter_dict[\'total amount\'] + line_total_amount\n
      else:\n
        period_counter_dict[\'total amount\'] = line_total_amount\n
      append(obj)\n
\n
    line_list.sort(sortProduct)\n
\n
obj = Object(uid="new_")\n
obj["client"] = \'Total\'\n
for k,v in period_counter_dict.items():\n
  if "mount" in k:\n
    v = round(v, 2)\n
  obj[k] = v\n
\n
request.set(\'stat_line\', [obj,])\n
\n
return line_list\n


]]></string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>period_list, report_type, doc_portal_type, line_portal_type, simulation_state,**kw</string> </value>
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
            <value> <string>OrderModule_getOrderStatList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
