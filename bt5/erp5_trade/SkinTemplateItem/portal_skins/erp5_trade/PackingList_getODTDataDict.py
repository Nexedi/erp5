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
            <value> <string>def getSourceReference(line):\n
  category_list = line.getAcquiredCategoryList()\n
  portal_type_list = (\'Purchase Packing List Line\',\n
                      \'Purchase Packing List Cell\',\n
                      \'Sale Packing List Line\',\n
                      \'Sale Packing List Cell\',)\n
  tmp_context = line.asContext(context=line, categories=category_list)\n
  predicate_list = context.portal_domains.searchPredicateList(tmp_context, portal_type=portal_type_list)\n
  for predicate in predicate_list:\n
    source_reference = predicate.getSourceReference()\n
    if source_reference:\n
     return source_reference\n
  return \'\'\n
\n
def getSubLineList(obj):\n
  sub_list = []\n
  for x in obj.contentValues(portal_type=context.getPortalDeliveryMovementTypeList(),\n
      sort_on=[(\'int_index\', \'ascending\'), (\'reference\', \'ascending\')]):\n
    if x.getPortalType() in obj.getPortalTaxMovementTypeList():\n
      continue\n
    sub_list.append(x)\n
    sub_list.extend(getSubLineList(x))\n
  return sub_list\n
\n
data_dict = context.Delivery_getODTDataDict(getSourceReference, getSubLineList)\n
order = context.getCausalityValue(portal_type=(\'Sale Order\', \'Purchase Order\'))\n
if order is not None:\n
  order_date = order.getStopDate()\n
  if context.getPortalType().startswith(\'Sale\'):\n
    order_date = order.getStartDate()\n
  data_dict.update(order_reference=order.getReference(),\n
                   order_date=order_date)\n
return data_dict\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>PackingList_getODTDataDict</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
