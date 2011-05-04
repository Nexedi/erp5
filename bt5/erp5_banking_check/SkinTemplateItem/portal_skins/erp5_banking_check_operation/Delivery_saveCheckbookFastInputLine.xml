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

counter_line = 0\n
result = []\n
resultContainer = {}\n
result_line = []\n
\n
if listbox is None:\n
  listbox = []\n
\n
# remove existing lines\n
old_line = [x.getObject() for x in context.objectValues(portal_type=[\'Checkbook Delivery Line\'])]\n
if len(old_line)>0:\n
  for object_list in old_line:\n
    context.deleteContent(object_list.getId())\n
\n
cash_item_item_dict = {}\n
# construct dict of selected item\n
for listbox_line in listbox:\n
  if listbox_line[\'selection\']==1:\n
    item = context.portal_catalog(uid=listbox_line[\'listbox_key\'])[0].getObject()\n
    delivery_line = context.newContent(portal_type=\'Checkbook Delivery Line\')\n
    item_dict = {}\n
    reference_range_min = None\n
    reference_range_max = None\n
    if item.getPortalType()==\'Check\':\n
      reference_range_min = reference_range_max = item.getReference()\n
    elif item.getPortalType()==\'Checkbook\':\n
      reference_range_min = item.getReferenceRangeMin()\n
      reference_range_max = item.getReferenceRangeMax()\n
    item_dict[\'reference_range_min\'] = reference_range_min\n
    item_dict[\'reference_range_max\'] = reference_range_max\n
    item_dict[\'destination_trade\'] = item.getDestinationTrade()\n
    item_dict["resource_value"] = item.getResourceValue()\n
    item_dict["check_amount"] = item.getCheckAmount()\n
    item_dict["check_type"] = item.getCheckType()\n
    item_dict["price_currency"] = item.getPriceCurrency()\n
    item_dict["aggregate_value"] = item\n
    item_dict["quantity"] = 1\n
    delivery_line.edit(**item_dict)\n
\n
\n
request  = context.REQUEST\n
redirect_url = \'%s/view?%s\' % ( context.absolute_url()\n
                                , \'portal_status_message=done\'\n
                                )\n
request[ \'RESPONSE\' ].redirect( redirect_url )\n


]]></string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>listbox=None, **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Delivery_saveCheckbookFastInputLine</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
