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

#For Cloudooo : Proxify it to allow anonymous user to discover metadata of uploaded file\n
current_date=DateTime()\n
assignment_list = []\n
for assignment in context.contentValues(portal_type=\'Assignment\'):\n
  if assignment.getValidationState() == \'open\':\n
    start_date = assignment.getStartDate()\n
    stop_date = assignment.getStopDate()\n
    if start_date is not None and stop_date is not None and start_date <= current_date < stop_date:\n
      assignment_list.append(assignment)\n
    elif start_date is not None and stop_date is None and start_date <= current_date:\n
      assignment_list.append(assignment)\n
    elif stop_date is not None and start_date is None and current_date < stop_date:\n
      assignment_list.append(assignment)\n
    elif start_date is None and stop_date is None:\n
      assignment_list.append(assignment)\n
return assignment_list\n


]]></string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>_proxy_roles</string> </key>
            <value>
              <tuple>
                <string>Manager</string>
              </tuple>
            </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Person_getAvailableAssignmentValueList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
