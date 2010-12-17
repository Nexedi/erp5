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
            <value> <string># Usage: .../Base_jumpToAccountingTransaction?from_entity=1\n
#\n
# Use from_account to display only transaction related to the account you come from, and from_entity if you come from an organisation or person\n
\n
redirect_kw = dict(reset=1,\n
                   ignore_hide_rows=True)\n
\n
if from_account:\n
  redirect_kw[\'node\'] = [context.getRelativeUrl()]\n
elif from_entity:\n
  redirect_kw[\'entity\'] = context.getRelativeUrl()\n
\n
return context.getPortalObject().accounting_module.Base_redirect(\n
              \'view\', keep_items=redirect_kw)\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>from_account=None, from_entity=None</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Base_jumpToAccountingTransaction</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
