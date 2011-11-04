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

"""\n
  Return list of blocked user logins in a \'listbox\' format\n
"""\n
from DateTime import DateTime\n
from Products.ZSQLCatalog.SQLCatalog import Query\n
from Products.ERP5Type.Document import newTempBase\n
\n
portal = context.getPortalObject()\n
portal_preferences = portal.portal_preferences\n
\n
blocked_user_login_list = []\n
all_blocked_user_login_dict = {}\n
\n
now = DateTime()\n
one_second = 1/24.0/60.0/60.0\n
check_duration = portal_preferences.getPreferredAuthenticationFailureCheckDuration()\n
max_authentication_failures = portal_preferences.getPreferredMaxAuthenticationFailure()\n
check_time = now - check_duration*one_second\n
\n
kw = {\'portal_type\': \'Authentication Event\',\n
      \'creation_date\': Query(creation_date = check_time,\n
                             range=\'min\'),\n
      \'validation_state\' : \'confirmed\'}\n
failure_list = portal.portal_catalog(**kw)\n
for failure in failure_list:\n
  person = failure.getDestinationValue()\n
  if person not in all_blocked_user_login_dict.keys():\n
    all_blocked_user_login_dict[person] = []\n
  all_blocked_user_login_dict[person].append(failure)\n
\n
# leave only ones that are blocked:\n
for person, failure_list in all_blocked_user_login_dict.items():\n
  if len(failure_list) >= max_authentication_failures:\n
    blocked_user_login_list.append(newTempBase(portal, \n
                                               person.getTitle(), \n
                                               **{\'title\': person.getTitle(),\n
                                                  \'count\':len(failure_list),\n
                                                  \'reference\': person.getReference(),\n
                                                  \'url\': person.absolute_url()}))\n
return blocked_user_login_list\n


]]></string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>**kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>SystemEventModule_getBlockedUserLoginList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
