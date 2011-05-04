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
  Get Person details (i.e. group, site, etc..) from its Career.\n
"""\n
\n
from Products.ERP5Type.Cache import CachingMethod\n
\n
def getPersonCareerDict(user_name):\n
  portal = context.getPortalObject()\n
  result = {\'group_list\': [],\n
            \'site_list\': [],\n
            }\n
  person = portal.ERP5Site_getAuthenticatedMemberPersonValue(user_name=user_name)\n
  if person is None:\n
    return result\n
\n
  group = person.getGroup()\n
  organisation = person.getSubordinationValue()\n
  if group is not None:\n
    result[\'group_list\'] = [group]\n
  if organisation is not None:\n
    result[\'site_list\'] = organisation.getSiteList()\n
  return result\n
\n
getPersonCareerDict = CachingMethod(getPersonCareerDict,\n
                                    ("ERP5Site_getPersonCareerDict",),\n
                                    cache_factory=\'erp5_content_short\')\n
return getPersonCareerDict(user_name)\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>user_name=None</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>ERP5Site_getPersonCareerDict</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
