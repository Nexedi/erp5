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
            <value> <string>if account is None:\n
  account = context\n
\n
gap_id = account.Account_getGapId(gap_root=gap_root)\n
title  = account.getTranslatedTitle()\n
\n
if gap_id:\n
  title = "%s - %s" % (gap_id, title)\n
\n
return title\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>account=None, gap_root=None</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Account_getFormattedTitle</string> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string>Format the title of an account properly</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
