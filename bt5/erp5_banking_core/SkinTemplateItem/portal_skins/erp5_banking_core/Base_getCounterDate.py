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
            <value> <string># Retrieve the last counter date for a given date\n
\n
from DateTime import DateTime\n
if start_date is None:\n
  start_date = DateTime()\n
\n
counter_date_list = context.portal_catalog(portal_type=\'Counter Date\', \n
                site_uid=site_uid, \n
                start_date={\'query\':start_date,\'range\':\'ngt\'},\n
                sort_on=[(\'start_date\',\'descending\')], limit=1)\n
counter_date = None\n
if len(counter_date_list)==1:\n
  counter_date = counter_date_list[0]\n
return counter_date\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>site_uid=None, start_date=None</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Base_getCounterDate</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
