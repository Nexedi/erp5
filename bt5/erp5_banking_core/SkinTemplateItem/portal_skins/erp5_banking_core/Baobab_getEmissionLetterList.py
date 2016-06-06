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
            <value> <string>emission_letter_dict = {}\n
\n
for a in site_list:\n
  if not a.startswith(\'site\'):\n
    a = \'site/\' + a\n
  site_codification = context.portal_categories.getCategoryValue(a).getCodification()\n
  if site_codification not in (\'\', None):\n
    lower_letter = site_codification[0].lower()\n
    if lower_letter == \'z\':\n
      lower_letter = \'k\'\n
    emission_letter_dict[lower_letter] = 1\n
\n
return emission_letter_dict.keys()\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>site_list</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Baobab_getEmissionLetterList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
