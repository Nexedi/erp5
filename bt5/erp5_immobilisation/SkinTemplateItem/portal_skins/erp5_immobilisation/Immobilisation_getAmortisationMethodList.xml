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
            <value> <string># Returns a list of tuples (region, Folder) representing amortisation methods,\n
# deducted from available methods\n
return_list = []\n
\n
# Find the accounting regions\n
skin_dir_list = context.portal_skins.objectValues()\n
for skin_dir in skin_dir_list:\n
  id = skin_dir.getId()\n
  id_tokens = id.split(\'_\')\n
  if len(id_tokens) == 3 and id_tokens[:2] == [\'erp5\',\'accounting\']:\n
    region = id_tokens[2]\n
    # Determine amortisation methods available in this region\n
    for subfolder in skin_dir.objectValues():\n
      if "ratioCalculation" in map(lambda o: o.getId(), subfolder.objectValues()):\n
        return_list.append((region,subfolder))\n
\n
return return_list\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Immobilisation_getAmortisationMethodList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
