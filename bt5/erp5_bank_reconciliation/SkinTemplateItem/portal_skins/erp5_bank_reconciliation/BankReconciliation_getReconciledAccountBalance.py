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

from Products.ZSQLCatalog.SQLCatalog import SimpleQuery, NegatedQuery\n
portal = context.getPortalObject()\n
\n
kw = {\n
  \'section_uid\': context.getSourceSectionUid(),\n
  \'payment_uid\': context.getSourcePaymentUid(),\n
  \'node_category\': \'account_type/asset/cash/bank\',\n
  \'simulation_state\': (\'stopped\', \'delivered\', ),\n
  \'portal_type\': portal.getPortalAccountingMovementTypeList(),\n
}\n
\n
if not at_date and context.getStopDate():\n
  at_date = context.getStopDate().latestTime()\n
  \n
if at_date:\n
  kw[\'at_date\'] = at_date\n
  kw[\'reconciliation_query\'] = SimpleQuery(\n
      aggregate_bank_reconciliation_date=kw[\'at_date\'], comparison_operator="<=")\n
\n
if portal.REQUEST.get(\'reconciled_uid_list\'):\n
  # This is to take into account lines we just reconciled.\n
  # We sum all reconciled lines execpt those we just reconciled + those we just\n
  # reconciled without applying the criterion on reconcilation \n
  kw[\'workaround_catalog_lag_query\'] = NegatedQuery(SimpleQuery(uid=portal.REQUEST[\'reconciled_uid_list\']))\n
  previously_reconciled = portal.portal_simulation.getInventory(**kw)\n
  \n
  kw.pop(\'workaround_catalog_lag_query\')\n
  kw.pop(\'reconciliation_query\')\n
  kw[\'uid\'] = portal.REQUEST[\'reconciled_uid_list\']\n
  return previously_reconciled + portal.portal_simulation.getInventory(**kw)\n
  \n
return context.portal_simulation.getInventory(**kw)\n


]]></string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>at_date=None, *args, **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>BankReconciliation_getReconciledAccountBalance</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
