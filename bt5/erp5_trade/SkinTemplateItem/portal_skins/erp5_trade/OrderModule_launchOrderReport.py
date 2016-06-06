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
            <value> <string># Run a first batch of calcul in activity\n
# Then call the report in a deferred mode\n
from json import dumps\n
from Products.CMFActivity.ActiveResult import ActiveResult\n
portal = context.getPortalObject()\n
N_ = portal.Base_translateString\n
# Check deferred style is present\n
if not \'Deferred\' in portal.portal_skins.getSkinSelections():\n
  return context.Base_redirect(\'view\', keep_items=dict(\n
              portal_status_message=N_("Deferred style must be installed to run this report")))\n
  \n
person_value = portal.ERP5Site_getAuthenticatedMemberPersonValue()\n
if person_value is None:\n
  portal.changeSkin(None)\n
  return context.Base_redirect(\'view\', keep_items=dict(\n
              portal_status_message=N_("No person found for your user")))\n
\n
if person_value.getDefaultEmailText(\'\') in (\'\', None):\n
  portal.changeSkin(None)\n
  return context.Base_redirect(\'view\', keep_items=dict(\n
              portal_status_message=N_("You haven\'t defined your email address")))\n
\n
parameter_dict, stat_columns, selection_columns = context.OrderModule_getOrderReportParameterDict()\n
\n
active_process = context.OrderModule_activateGetOrderStatList(tag=script.id, **parameter_dict)\n
\n
# Create a result to store computed parameter for later\n
active_process.postResult(ActiveResult(\n
  sevrity=1,\n
  detail=dumps({\n
      \'type\' : \'parameters\',\n
      \'params\' : parameter_dict,\n
      \'stat_columns\' : stat_columns,\n
      \'selection_columns\' : selection_columns,\n
      })\n
      ))\n
\n
request = context.REQUEST\n
context.getPortalObject().portal_skins.changeSkin("Deferred")\n
request.set(\'portal_skin\', "Deferred")\n
assert deferred_portal_skin is not None, "No deferred portal skin found in parameters"\n
request.set(\'deferred_portal_skin\', deferred_portal_skin)\n
\n
kw[\'deferred_style\'] = 1\n
kw[\'active_process\'] = active_process.getPath()\n
request.set(\'active_process\', active_process.getPath())\n
kw.update(parameter_dict)\n
kw.pop(\'format\',None)\n
return context.Base_activateReport(\n
  form = getattr(context, report_method_id),\n
  after_tag=script.id,\n
  **kw\n
  )\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>report_method_id, deferred_portal_skin, *args, **kw</string> </value>
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
            <value> <string>OrderModule_launchOrderReport</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
