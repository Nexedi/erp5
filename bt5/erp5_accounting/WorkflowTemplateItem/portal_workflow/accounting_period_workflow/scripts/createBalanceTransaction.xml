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
            <value> <string>"""Create a balance transaction\n
"""\n
accounting_period = sci[\'object\']\n
\n
# we only create a balance transaction for top level accounting periods\n
if accounting_period.getParentValue().getPortalType() == accounting_period.getPortalType():\n
  return\n
\n
portal = accounting_period.getPortalObject()\n
profit_and_loss_account = portal.portal_workflow.getInfoFor(\n
                            accounting_period, \'profit_and_loss_account\')\n
\n
accounting_period.activate(after_method_id=\'unindexObject\').AccountingPeriod_createBalanceTransaction(\n
                       profit_and_loss_account=profit_and_loss_account)\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>sci</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>createBalanceTransaction</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
