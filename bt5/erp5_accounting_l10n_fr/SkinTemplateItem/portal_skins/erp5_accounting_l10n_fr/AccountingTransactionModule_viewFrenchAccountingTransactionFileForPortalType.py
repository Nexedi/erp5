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
            <value> <string>portal = context.getPortalObject()\n
\n
search_kw = {\n
  \'simulation_state\': simulation_state,\n
  \'accounting_transaction.section_uid\': section_uid_list,\n
  \'operation_date\': {\'query\': (from_date, at_date), \'range\': \'minngt\' },\n
  \'portal_type\': portal_type,\n
}\n
\n
method_kw = {\n
  \'active_process\': this_portal_type_active_process,\n
  \'section_uid_list\': section_uid_list,\n
}\n
\n
activate_kw = {\n
  \'tag\': tag,\n
  \'priority\': priority,\n
}\n
\n
portal.portal_catalog.searchAndActivate(\n
  method_id=\'AccountingTransaction_postFECResult\', \n
  method_kw=method_kw,\n
  activate_kw=activate_kw,\n
  **search_kw)\n
\n
context.activate(tag=aggregate_tag, after_tag=tag, activity=\'SQLQueue\').AccountingTransactionModule_aggregateFrenchAccountingTransactionFileForPortalType(\n
  portal_type=portal_type,\n
  active_process=active_process,\n
  this_portal_type_active_process=this_portal_type_active_process)\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>portal_type, section_uid_list, from_date, at_date, simulation_state, active_process, this_portal_type_active_process, tag, aggregate_tag, priority</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>AccountingTransactionModule_viewFrenchAccountingTransactionFileForPortalType</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
