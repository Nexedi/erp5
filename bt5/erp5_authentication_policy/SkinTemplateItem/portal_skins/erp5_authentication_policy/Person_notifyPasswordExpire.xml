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
  File a password expire event.\n
"""\n
from DateTime import DateTime\n
from Products.ZSQLCatalog.SQLCatalog import Query\n
from Products.ERP5Type.DateUtils import addToDate\n
\n
portal = context.getPortalObject()\n
portal_preferences = portal.portal_preferences\n
\n
if not portal_preferences.isAuthenticationPolicyEnabled() or \\\n
   not portal.portal_preferences.isPreferredSystemRecoverExpiredPassword():\n
  # no policy, no sense to file expire at all or symply system do not configured to\n
  return 0\n
\n
# Prevent creating new recovery if one was recently created\n
recovery_list = portal.portal_catalog(\n
  portal_type="Credential Recovery",\n
  reference=context.getReference(),\n
  default_destination_decision_uid=context.getUid(),\n
  creation_date=Query(range="min", creation_date=addToDate(DateTime(), {\'day\': -1})),\n
  limit=1)\n
if (len(recovery_list) > 0):\n
  return 0\n
\n
module = portal.getDefaultModule(portal_type=\'Credential Recovery\')\n
credential_recovery = module.newContent(\n
                               portal_type="Credential Recovery",\n
                               reference=context.getReference(),\n
                               destination_decision_value=context,\n
                               language=portal.Localizer.get_selected_language(),\n
                               activate_kw={\'tag\': tag})\n
# immediate reindex allowed because it is a new object\n
credential_recovery.immediateReindexObject()\n
context.serialize()\n
credential_recovery.submit()\n


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
                <string>Owner</string>
              </tuple>
            </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Person_notifyPasswordExpire</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
