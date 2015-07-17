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
            <value> <string># It should be ran in an alarm thank to a property sheet constraint.\n
from ZODB.POSException import ConflictError\n
\n
if fixit:\n
  return ["Cannot fix automatically, please do it manually. (Or deactivate the constraint to force upgrade.)"]\n
\n
portal = context.getPortalObject()\n
\n
black_list = getattr(context, "Base_getInstalledBusinessTemplateBlackListForModificationList", lambda: ())()\n
bt_list = [\n
  x.getObject()\n
  for x in portal.portal_catalog(\n
    portal_type="Business Template",\n
    installation_state="installed",\n
  )\n
  if x.getInstallationState() == "installed" and x.getTitle() not in black_list and x.getId() not in black_list\n
]\n
\n
diff_list = []\n
for bt in bt_list:\n
  try:\n
    diff = bt.BusinessTemplate_getDiffWithZODBAsText()\n
    if diff:\n
      diff_list += ["===== %s =====" % bt.getTitle()] + diff.splitlines()\n
  except ConflictError:\n
    raise\n
  except Exception as e:\n
    diff_list += ["===== %s =====" % bt.getTitle(), repr(e)]\n
\n
return diff_list\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>fixit=False, **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Base_reportInstalledBusinessTemplateModification</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
