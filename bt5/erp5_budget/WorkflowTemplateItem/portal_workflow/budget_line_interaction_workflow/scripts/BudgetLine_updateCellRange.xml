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
            <value> <string>line = state_change[\'object\']\n
\n
base_id = \'cell\'\n
line.updateCellRange(base_id=base_id)\n
\n
# also update membership criterion category list on line\n
if line.getMembershipCriterionBaseCategoryList():\n
  line.setMembershipCriterionCategoryList([])\n
  budget_line_category_list = line.getCategoryList()\n
  for variation in budget_line_category_list:\n
    if not variation:\n
      continue\n
    base, category = variation.split(\'/\', 1)\n
    if base in line.getMembershipCriterionBaseCategoryList():\n
      line.setMembershipCriterionCategoryList(\n
            [variation,] + line.getMembershipCriterionCategoryList())\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>state_change</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>BudgetLine_updateCellRange</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
