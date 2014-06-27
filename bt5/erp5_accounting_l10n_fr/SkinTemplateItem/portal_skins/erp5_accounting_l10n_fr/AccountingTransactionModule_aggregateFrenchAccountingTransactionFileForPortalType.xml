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
            <value> <string>from Products.CMFActivity.ActiveResult import ActiveResult\n
portal = context.getPortalObject()\n
portal_type = portal.portal_types[portal_type]\n
active_process = portal.restrictedTraverse(active_process)\n
this_portal_type_active_process = portal.restrictedTraverse(this_portal_type_active_process)\n
\n
# XXX we need proxy role for this\n
result_list = this_portal_type_active_process.getResultList()\n
\n
if result_list:\n
  journal_fragment = context.AccountingTransactionModule_viewJournalAsFECXML(\n
      portal_type=portal_type,\n
      result_list=result_list)\n
  \n
  active_process.postResult(ActiveResult(detail=journal_fragment.encode(\'utf8\').encode(\'zlib\')))\n
\n
# delete no longer needed active process\n
this_portal_type_active_process.getParentValue().manage_delObjects(ids=[this_portal_type_active_process.getId()])\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>portal_type, active_process, this_portal_type_active_process</string> </value>
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
            <value> <string>AccountingTransactionModule_aggregateFrenchAccountingTransactionFileForPortalType</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
