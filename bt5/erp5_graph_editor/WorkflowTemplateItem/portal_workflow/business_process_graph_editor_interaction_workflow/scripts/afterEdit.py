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
            <value> <string>import json\n
business_process = sci[\'object\']\n
graph = business_process.getProperty(\'jsplumb_graph\')\n
\n
assert graph\n
\n
if graph:\n
  portal = business_process.getPortalObject()\n
  trade_state_dict = dict(start=None, end=None)\n
  for trade_state in portal.portal_categories.trade_state.getCategoryChildValueList():\n
    # XXX I hope no duplicates\n
    trade_state_dict[trade_state.getReference() or trade_state.getId()] = trade_state\n
\n
  graph = json.loads(graph)[\'graph\']\n
  for edge_data in graph[\'edge\'].values():\n
    # Create the business link if it does not exist yet.\n
    if not edge_data.get(\'business_link_url\'):\n
      business_link = business_process.newContent(\n
        portal_type=\'Business Link\',\n
        predecessor_value=trade_state_dict[edge_data[\'source\']],\n
        successor_value=trade_state_dict[edge_data[\'destination\']],\n
      )\n
    else:\n
  # XXX Zope does not like to traverse unicode ...\n
      business_link = portal.restrictedTraverse(str(edge_data[\'business_link_url\']))\n
    business_link.edit(\n
        title=edge_data.get(\'name\'),\n
  # XXX Zope does not like to traverse unicode ...\n
        trade_phase=str(edge_data.get(\'trade_phase\', \'\')),\n
    )\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>sci</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>afterEdit</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
