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
            <value> <string>from Products.ZSQLCatalog.SQLCatalog import Query\n
from Products.ERP5Type.DateUtils import addToDate\n
from DateTime import DateTime\n
\n
portal = context.getPortalObject()\n
\n
portal.portal_catalog.searchAndActivate(\n
  portal_type="One Time Restricted Access Token",\n
  validation_state="validated",\n
  creation_date=Query(creation_date=addToDate(DateTime(), to_add={\'day\': -1}), range="max"),\n
  method_id=\'invalidate\',\n
  method_kw={"comment": "Unused for 1 day."},\n
  activate_kw={\'tag\': tag},\n
)\n
\n
context.activate(after_tag=tag).getId()\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>tag, fixit, params</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Alarm_garbageCollectOneTimeRestrictedAccessToken</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
