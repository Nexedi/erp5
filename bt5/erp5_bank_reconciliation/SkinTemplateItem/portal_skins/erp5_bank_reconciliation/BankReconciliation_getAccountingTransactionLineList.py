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
            <value> <string>from Products.ZSQLCatalog.SQLCatalog import SimpleQuery, NegatedQuery\n
portal = context.getPortalObject()\n
\n
kw = {\n
  \'section_uid\': context.getSourceSectionUid(),\n
  \'payment_uid\': context.getSourcePaymentUid(),\n
  \'node_category\': \'account_type/asset/cash/bank\',\n
  \'simulation_state\': (\'stopped\', \'delivered\', ),\n
  \'portal_type\': context.getPortalAccountingMovementTypeList(),\n
  \'sort_on\': ((\'date\', \'ASC\'), (\'uid\', \'ASC\'))\n
}\n
\n
\n
if mode == "reconcile":\n
  if context.getStopDate():\n
    kw[\'at_date\'] = context.getStopDate().latestTime()\n
  kw.update({\n
  \'reconciliation_query\': SimpleQuery(\n
      aggregate_bank_reconciliation_date=None),\n
  \'left_join_list\': [\'aggregate_bank_reconciliation_date\'],\n
  \'implicit_join\': False, })\n
else:\n
  assert mode == "unreconcile"\n
  kw[\'aggregate_bank_reconciliation_uid\'] = context.getUid()\n
\n
# Handle search params\n
if listbox_kw.get(\'Movement_getExplanationTitle\'):\n
  kw[\'stock_explanation_title\'] = listbox_kw[\'Movement_getExplanationTitle\']\n
if listbox_kw.get(\'Movement_getExplanationReference\'):\n
  kw[\'stock_explanation_reference\'] = listbox_kw[\'Movement_getExplanationReference\']\n
if listbox_kw.get(\'Movement_getExplanationTranslatedPortalType\'):\n
  kw[\'stock_explanation_translated_portal_type\'] = listbox_kw[\'Movement_getExplanationTranslatedPortalType\']\n
if listbox_kw.get(\'getTranslatedSimulationStateTitle\'):\n
  kw[\'translated_simulation_state_title\'] = listbox_kw[\'getTranslatedSimulationStateTitle\']\n
if listbox_kw.get(\'total_quantity\'):\n
  kw[\'stock.quantity\'] = listbox_kw[\'total_quantity\']\n
if listbox_kw.get(\'Movement_getMirrorSectionTitle\'):\n
  kw[\'stock_mirror_section_title\'] = listbox_kw[\'Movement_getMirrorSectionTitle\']\n
if listbox_kw.get(\'date\'):\n
  kw[\'stock.date\'] = listbox_kw[\'date\']\n
\n
if portal.REQUEST.get(\'reconciled_uid_list\'):\n
  # This is to prevent showing again the lines that we just reconciled\n
  kw[\'workaround_catalog_lag_query\'] = NegatedQuery(SimpleQuery(uid=portal.REQUEST[\'reconciled_uid_list\']))\n
  \n
if context.getSourcePayment():\n
  # As we are showing quantities and not asset prices, we use the precision\n
  # from this bank account currency.\n
  # TODO: This should be defined earlier because it does not apply to fast input fields.\n
  container.REQUEST.set(\'precision\',\n
      context.getQuantityPrecisionFromResource(\n
        context.getSourcePaymentValue().getPriceCurrency()))\n
\n
return context.portal_simulation.getMovementHistoryList(**kw)\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>mode="reconcile", *args, **listbox_kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>BankReconciliation_getAccountingTransactionLineList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
