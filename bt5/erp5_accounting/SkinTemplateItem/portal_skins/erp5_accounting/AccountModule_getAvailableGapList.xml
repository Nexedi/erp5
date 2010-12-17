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
            <value> <string># Return the list of gap roots that can be used.\n
# gap category is typically organized such as : \n
#  gap / country / gap_name\n
# so we always use as "root" the category of depth 2.\n
\n
results = []\n
countries = context.portal_categories.gap.objectValues()\n
for country in countries : \n
  for gap in country.objectValues() :\n
    title = gap.getParentValue().getTitle() + \'/\'+ gap.getTitle()\n
    path = gap.getRelativeUrl()\n
    if not include_gap_in_path : \n
      path = path.replace(\'gap/\', \'\')\n
\n
    results += [(title, path)]\n
\n
if include_empty_item == 1:\n
  results = [(\'\', \'\')] + results\n
\n
return results\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>include_gap_in_path=1, include_empty_item=0</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>AccountModule_getAvailableGapList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
