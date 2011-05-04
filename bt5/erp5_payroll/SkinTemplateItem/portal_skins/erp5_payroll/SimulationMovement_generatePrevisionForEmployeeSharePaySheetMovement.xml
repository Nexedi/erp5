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
            <value> <string>category_list = []\n
for base_category in context.getSourceArrowBaseCategoryList():\n
  if base_category == "source_section":\n
    category = "source_section/"+movement.getDefaultAcquiredCategoryMembership("destination", base=0)\n
  else:\n
    category = context.getDefaultAcquiredCategoryMembership(base_category, base=1) # This should be moved to degault implementation of business path - XXX-JPS\n
  \n
  if category is None:\n
    category = movement.getDefaultAcquiredCategoryMembership(base_category, base=1)\n
\n
  if category:\n
    category_list.append(category)\n
\n
return category_list\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>movement</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>SimulationMovement_generatePrevisionForEmployeeSharePaySheetMovement</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
