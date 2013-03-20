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
            <value> <string>request = context.REQUEST\n
site = context.getPortalObject()\n
Base_translateString = site.Base_translateString\n
error_message = None\n
uids = site.portal_selections.getSelectionCheckedUidsFor(selection_name)\n
if len(uids) != 2:\n
  error_message =  Base_translateString("Please select one publication and one subscription.")\n
\n
object_list = [x.getObject() for x in site.portal_catalog(uid=uids)]\n
\n
pub = None\n
sub = None\n
r1 = object_list[0]\n
if r1.getPortalType() == "SyncML Publication":\n
  pub = r1\n
else:\n
  sub = r1\n
\n
r2 = object_list[1]\n
if r2.getPortalType() == "SyncML Publication":\n
  pub = r2\n
else:\n
  sub = r2\n
\n
if not pub or not sub:\n
  error_message =  Base_translateString("Please select one publication and one subscription.")\n
\n
if error_message:\n
  qs = \'?portal_status_message=%s\' % error_message\n
  return request.RESPONSE.redirect( context.absolute_url() + \'/\' + form_id + qs )\n
\n
\n
from DateTime import DateTime\n
\n
callback = "SynchronizationTool_checkPointFixe"\n
active_process_path = site.portal_activities.newActiveProcess(start_date=DateTime(), causality_value=sub).getPath()\n
method_kw = {\n
  "publication_path" : pub.getPath(),\n
  "subscription_path" : sub.getPath(),\n
  "active_process" : active_process_path,\n
}\n
activate_kw = {\n
  "priority" : 3,\n
  "activity" : "SQLQueue",\n
}\n
\n
# Register start of point fixe\n
from Products.CMFActivity.ActiveResult import ActiveResult\n
active_result = ActiveResult()\n
active_result.edit(summary=\'Info\',\n
                   severity=0,\n
                   detail="Point fixe check launched at %r" % (DateTime().strftime("%d/%m/%Y %H:%M"),))\n
sub.activate(active_process=active_process_path,\n
            activity=\'SQLQueue\',\n
            priority=2,).ERP5Site_saveCheckCatalogTableResult(active_result)\n
\n
context.SynchronizationTool_activateCheckPointFixe(callback=callback, method_kw=method_kw, activate_kw=activate_kw)\n
\n
qs = \'?portal_status_message=%s\' % "Point fixe running, active process path is %s" % (active_process_path,)\n
return request.RESPONSE.redirect( context.absolute_url() + \'/\' + form_id + qs )\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>selection_name, form_id</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>SynchronizationTool_launchActivateCheckPointFixe</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
