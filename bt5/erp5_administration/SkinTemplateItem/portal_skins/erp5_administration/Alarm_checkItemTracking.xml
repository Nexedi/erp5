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
            <value> <string>"""Check the tracking history of all items.\n
"""\n
\n
item_portal_type_list = context.getProperty(\'item_portal_type_list\')\n
\n
if item_portal_type_list:\n
  active_process = context.newActiveProcess().getRelativeUrl()\n
\n
  context.getPortalObject().portal_catalog.searchAndActivate(\n
     method_id=\'Item_checkTrackingList\',\n
     method_kw=dict(fixit=fixit, active_process=active_process),\n
     activate_kw=dict(tag=tag, priority=5),\n
     portal_type=item_portal_type_list)\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>tag, fixit=0, **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Alarm_checkItemTracking</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
