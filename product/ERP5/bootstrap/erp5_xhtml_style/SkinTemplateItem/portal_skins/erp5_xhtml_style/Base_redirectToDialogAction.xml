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

if \'?\' in dialog_action_url:\n
  dialog_action_url = \'%s&form_id=%s\' % (dialog_action_url, form_id)\n
else:\n
  dialog_action_url = \'%s?form_id=%s\' % (dialog_action_url, form_id)\n
\n
\n
if format:\n
  # Add format parameter if not null\n
  dialog_action_url += \'&format=%s\' % (format,)\n
return container.REQUEST.RESPONSE.redirect(dialog_action_url)\n


]]></string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>dialog_action_url, form_id=\'\', format=None</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Base_redirectToDialogAction</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
