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

"""\n
  This script adds accounts value, only if they are debtors\n
"""\n
\n
request = context.REQUEST\n
portal = context.getPortalObject()\n
\n
kw = dict(kwd)\n
kw[\'simulation_state\'] = kwd.get(\'simulation_state\', request.get(\'simulation_state\'))\n
kw["section_category"] = kwd.get(\'section_category\', request.get(\'section_category\'))\n
at_date = kwd.get(\'at_date\', request[\'at_date\'])\n
kw[\'at_date\'] = at_date.latestTime()\n
\n
if request.get(\'account_id_list_conversion_script_id\'):\n
  account_id_list_conversion_script = getattr(portal, request[\'account_id_list_conversion_script_id\'])\n
  kw[\'node_category\'] = account_id_list_conversion_script(account_id_list)\n
else:\n
  kw[\'node_category\'] = account_id_list\n
\n
sum = 0.0\n
for inventory in portal.portal_simulation.getInventoryList(\n
                                    group_by_node=1,\n
                                    **kw):\n
  if inventory.total_price > 0:\n
    sum += inventory.total_price\n
return sum\n


]]></string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>account_id_list, **kwd</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>AccountModule_getFiscalReportDebitorNodeBalance</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
