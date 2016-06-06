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
            <value> <string>portal_selection = getattr(context,\'portal_selections\')\n
params = portal_selection.getSelectionParamsFor(selection_name)\n
rss_read_item_list = params.get(\'rss_read_item_list\', [])\n
params[\'rss_read_item_list\'] = rss_read_item_list\n
if item not in rss_read_item_list:\n
  rss_read_item_list.append(item)\n
portal_selection.setSelectionParamsFor(selection_name, params)\n
return item\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>selection_name,item</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Base_setRssItemReadInSelection</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
