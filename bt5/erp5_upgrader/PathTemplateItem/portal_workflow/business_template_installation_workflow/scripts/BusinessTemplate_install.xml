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

business_template = state_change[\'object\']\n
listbox = state_change.kwargs.get(\'listbox\')\n
update_catalog = state_change.kwargs.get(\'update_catalog\')\n
update_translation = state_change.kwargs.get(\'update_translation\')\n
workflow_action = state_change.kwargs.get(\'workflow_action\')\n
\n
object_to_update = {}\n
if listbox is not None and len(listbox) > 0:\n
  for item in listbox:\n
    if item[\'choice\']:\n
      # Choice parameter is now selected with a MultiCheckBoxField with only one element\n
      # Business Template need to get a string and not a list\n
      object_to_update[item[\'listbox_key\']] = item[\'choice\'][0]\n
    else:\n
      object_to_update[item[\'listbox_key\']] = "nothing"\n
\n
if workflow_action == \'install_action\':\n
  business_template.install(force=0, object_to_update=object_to_update, \\\n
                            update_catalog=update_catalog, update_translation=update_translation)\n
elif workflow_action == \'reinstall_action\':\n
  business_template.reinstall(force=0, object_to_update=object_to_update, \\\n
                              update_catalog=update_catalog, update_translation=update_translation)\n


]]></string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>state_change</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>BusinessTemplate_install</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
