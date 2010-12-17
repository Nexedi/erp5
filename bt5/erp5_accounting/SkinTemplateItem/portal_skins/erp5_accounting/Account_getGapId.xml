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
            <value> <string># This script returns the gap id for this account according to the current gap\n
# XXX This script is badly name, as it does not truly return a category ID.\n
# XXX Instead, the purpose of this script is more to return an account number to display\n
\n
preference_tool = context.getPortalObject().portal_preferences\n
\n
number_method = preference_tool.getPreferredAccountNumberMethod()\n
\n
if number_method == \'account_reference\' and not gap_root:\n
  reference = context.getReference()\n
  if reference:\n
    return reference\n
\n
## elif number_method == \'gap_id\':\n
# GAP id is the default rendering\n
current_gap = gap_root or preference_tool.getPreferredAccountingTransactionGap() or \'\'\n
for gap in context.getGapValueList(): \n
  if current_gap in gap.getPath(): \n
    return gap.getReference() or gap.getId()\n
return \'\'\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>gap_root=None</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Account_getGapId</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
