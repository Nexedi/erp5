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

from DateTime import DateTime\n
from Products.ERP5Security.ERP5UserManager import getUserByLogin\n
\n
person_list = getUserByLogin(context, login)\n
if not person_list:\n
  return False, []\n
\n
person = person_list[0]\n
if person.getPassword(format=\'palo_md5\') != password:\n
  return False, []\n
\n
now = DateTime()\n
group_set = set()\n
for assignment in person.contentValues(portal_type=\'Assignment\'):\n
  if assignment.getValidationState() == \'open\' and (\n
    assignment.getStartDate() is None or\n
    assignment.getStartDate() <= now <= assignment.getStopDate()):\n
\n
    # XXX below is sample implementation, as it must match the groups defined in PALO\n
    if assignment.isMemberOf("function/palo"):\n
      group_set.add(assignment.getGroupReference())\n
\n
    if assignment.isMemberOf("function/palo_admin"):\n
      group_set.add("admin")\n
\n
return True, list(group_set)\n


]]></string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>login, password</string> </value>
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
            <value> <string>ERP5Site_authenticatePaloUser</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
