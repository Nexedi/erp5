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
            <value> <string>"""\n
  Get Person assignment details.\n
"""\n
#For Cloudooo : Proxify it to allow anonymous user to discover metadata of uploaded file\n
\n
from Products.ERP5Type.Cache import CachingMethod\n
\n
portal = context.getPortalObject()\n
result = {\'group_list\': [],\n
          \'site_list\': [],\n
          \'function_list\': [],\n
          \'destination_trade_relative_url\': None}\n
person = portal.ERP5Site_getAuthenticatedMemberPersonValue(user_name=user_name)\n
\n
if person is None:\n
  return result\n
\n
def getAssignmentDict(username):\n
  person = portal.restrictedTraverse(person_relative_url)\n
  assignment_list = person.Person_getAvailableAssignmentValueList()\n
  for assignment in assignment_list:\n
    assignment = assignment.getObject()\n
    result[\'group_list\'].extend(assignment.getGroupList())\n
    result[\'function_list\'].extend(assignment.getFunctionList())\n
    result[\'site_list\'].extend(assignment.getSiteList())\n
    result[\'destination_trade_relative_url\'] = assignment.getDestinationTradeRelativeUrl()\n
  return result\n
\n
person_relative_url = person.getRelativeUrl()\n
getAssignmentDict = CachingMethod(getAssignmentDict,\n
                               ("ERP5Site_getPersonAssignmentDict",),\n
                                cache_factory=\'erp5_ui_short\')\n
return getAssignmentDict(person_relative_url)\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>user_name=None</string> </value>
        </item>
        <item>
            <key> <string>_proxy_roles</string> </key>
            <value>
              <tuple>
                <string>Auditor</string>
              </tuple>
            </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>ERP5Site_getPersonAssignmentDict</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
