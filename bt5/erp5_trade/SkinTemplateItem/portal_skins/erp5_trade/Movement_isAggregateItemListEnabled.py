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
            <value> <string>"""This script is an helper to replace complex TALES expression\n
for Base_viewTradeFieldLibrary/my_view_mode_aggregate_title_list.enable\n
"""\n
\n
# If the resource accepts items, and the context is a movements (ie. not a line \n
# already containing cells or line that has variations but not cells yet)\n
if context.getResource() and context.getResourceValue().getAggregatedPortalTypeList()\\\n
   and context.isMovement()\\\n
   and ((\'Cell\' in context.getPortalType()) or not context.getVariationCategoryList()):\n
  return True\n
  \n
# If the movement already has an aggregate, display it.\n
if context.getAggregate():\n
  return True\n
\n
# If there\'s not resource yet, we give a chance to set an item.\n
if context.getResource() is None and context.getPortalItemTypeList():\n
  return True\n
\n
return False\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Movement_isAggregateItemListEnabled</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
