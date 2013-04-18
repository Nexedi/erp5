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
            <value> <string>from Products.ERP5Type.Message import translateString\n
portal = context.getPortalObject()\n
\n
person_value = portal.ERP5Site_getAuthenticatedMemberPersonValue()\n
if person_value is None:\n
  portal.changeSkin(None)\n
  return context.Base_redirect(\'view\', keep_items=dict(\n
              portal_status_message=translateString("No person found for your user")))\n
\n
tag = \'AccountingTransactionModule_viewFrenchAccountingTransactionFile\'\n
aggregate_tag = \'%s:aggregate\' % tag\n
\n
if portal.portal_activities.countMessageWithTag(tag) or \\\n
      portal.portal_activities.countMessageWithTag(aggregate_tag):\n
  return context.Base_redirect(form_id, keep_items=dict(\n
              portal_status_message=translateString("Report already in progress.")))\n
\n
  \n
context.activate().AccountingTransactionModule_viewFrenchAccountingTransactionFileActive(\n
  section_category,\n
  section_category_strict,\n
  at_date,\n
  simulation_state,\n
  user_name=person_value.getReference(),\n
  tag=tag,\n
  aggregate_tag=aggregate_tag)\n
\n
return context.Base_redirect(form_id, keep_items=dict(\n
              portal_status_message=translateString("Report Started")))\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>section_category, section_category_strict, at_date, simulation_state, form_id=None, **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>AccountingTransactionModule_viewFrenchAccountingTransactionFile</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
