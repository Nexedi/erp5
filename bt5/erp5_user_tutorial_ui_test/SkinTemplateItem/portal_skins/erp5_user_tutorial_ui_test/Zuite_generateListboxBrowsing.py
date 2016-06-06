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

selenium_code = \\\n
"""\\\n
<tr>\n
  <td>clickAndWait</td>\n
  <td>//button[@name="Folder_show:method"]</td>\n
  <td></td>\n
</tr>\n
"""\n
\n
for selection in listbox_selection:\n
  selenium_code += \\\n
"""\\\n
<tr>\n
  <td>type</td>\n
  <td>//tr[@class=\'listbox-search-line\']/th[@class="listbox-table-filter-cell"]/input[@name=\'listbox_%s\']</td>\n
  <td>%s</td>\n
</tr>\n
""" % (selection[0], selection[1])\n
\n
  \n
selenium_code += \\\n
"""\\\n
<tr>\n
  <td>clickAndWait</td>\n
  <td>//input[@name=\\"Base_doSelect:method\\"]</td>\n
  <td></td>\n
</tr>\n
"""\n
\n
if enter_object:\n
  selenium_code += \\\n
"""\\\n
<tr>\n
  <td>clickAndWait</td>\n
  <td>link=%s</td>\n
  <td></td>\n
</tr>\n
""" % listbox_selection[0][1]\n
\n
\n
return selenium_code\n


]]></string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>listbox_selection, enter_object=False</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Zuite_generateListboxBrowsing</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
