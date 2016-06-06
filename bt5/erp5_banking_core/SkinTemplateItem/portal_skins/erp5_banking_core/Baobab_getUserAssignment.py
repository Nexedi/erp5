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

if user_id is None:\n
  user_id = context.portal_membership.getAuthenticatedMember().getUserName()\n
person_list = context.acl_users.erp5_users.getUserByLogin(user_id)\n
if not person_list:\n
  return None\n
assignment_list = person_list[0].contentValues(filter={\'portal_type\': \'Assignment\'})\n
if not assignment_list:\n
  return None\n
valid_assignment = None\n
now = DateTime()\n
for assignment in assignment_list:\n
  if assignment.getValidationState() == \'open\':\n
    stop = assignment.getStopDate()\n
    start = assignment.getStartDate()\n
    if (stop is None or stop > now) and (start is None or start < now):\n
      if valid_assignment is not None:\n
        raise ValueError(\'There are too many valid assignments for user %r\' % (user_id, ))\n
      valid_assignment = assignment\n
return valid_assignment\n


]]></string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>user_id=None</string> </value>
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
            <value> <string>Baobab_getUserAssignment</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
