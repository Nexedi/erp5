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
            <value> <string>resource_uid = context.getResourceUid()\n
\n
# XXX Currently sale trade condition is hardcoded by specialise category and\n
# cannot switch it by a period of time.\n
\n
def iterate(trade_condition, trade_condition_list):\n
  if trade_condition is None:\n
    return\n
  elif trade_condition in trade_condition_list:\n
    return\n
  else:\n
    trade_condition_list.append(trade_condition)\n
    for next_trade_condition in trade_condition.getSpecialiseValueList():\n
      iterate(next_trade_condition, trade_condition_list)\n
\n
sale_trade_condition_list = []\n
iterate(context.getSpecialiseValue(), sale_trade_condition_list)\n
\n
for sale_trade_condition in sale_trade_condition_list:\n
  for periodicity_line in sale_trade_condition.objectValues(portal_type=\'Periodicity Line\'):\n
    if periodicity_line.getResourceUid()==resource_uid:\n
      return [periodicity_line]\n
\n
raise RuntimeError, \'Cannot find an appropriate Periodicity Line for the movement: %s\' % context.getRelativeUrl()\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>schedule_start_date, schedule_stop_date</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>OpenSaleOrderLine_getPeriodicityLineValueList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
