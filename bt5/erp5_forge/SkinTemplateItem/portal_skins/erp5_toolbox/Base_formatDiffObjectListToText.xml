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
            <value> <string>def sortDiffObjectList(diff_object_list):\n
  return sorted(diff_object_list, key=lambda x: (x.object_state, x.object_class, x.object_id))\n
\n
for diff_object in sortDiffObjectList(diff_object_list):\n
  print("%s (%s) - %s" % (diff_object.object_state, diff_object.object_class, diff_object.object_id))\n
  if getattr(diff_object, "error", None) is not None:\n
    if detailed:\n
      print("  %s" % diff_object.error)\n
    print("")\n
  else:\n
    if detailed and getattr(diff_object, "data", None) is not None:\n
      print("%s" % diff_object.data.lstrip())\n
    print("")\n
\n
return printed\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>diff_object_list, detailed=True</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Base_formatDiffObjectListToText</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
