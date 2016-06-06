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
# Update selected uids. Required when the user select lines from different pages\n
portal.portal_selections.updateSelectionCheckedUidList(list_selection_name, listbox_uid, uids)\n
selection_uid_list = portal.portal_selections.getSelectionCheckedUidsFor(list_selection_name)\n
\n
if mode == \'reconcile\':\n
  for uid in selection_uid_list:\n
    line = portal.portal_catalog.getObject(uid)\n
    if line.getAggregate(portal_type=\'Bank Reconciliation\'):\n
      return context.Base_redirect(dialog_id,\n
                  abort_transaction=True,\n
                  keep_items={\'portal_status_message\': translateString("Line Already Reconciled"),\n
                              \'reset\': 1,\n
                              \'cancel_url\': cancel_url,\n
                              \'mode\': mode,\n
                              \'field_your_mode\': mode})\n
    line.AccountingTransactionLine_setBankReconciliation(context,\n
      message=translateString("Reconciling Bank Line"))\n
  return context.Base_redirect(dialog_id, keep_items={\n
      \'portal_status_message\': translateString("Line Reconciled"),\n
      \'reset\': 1,\n
      \'cancel_url\': cancel_url,\n
      \'field_your_mode\': mode,\n
      \'mode\': mode,\n
      \'reconciled_uid_list\': selection_uid_list})\n
\n
assert mode == \'unreconcile\'\n
for uid in selection_uid_list:\n
  line = portal.portal_catalog.getObject(uid)\n
  line.AccountingTransactionLine_setBankReconciliation(None,\n
    message=translateString("Reconciling Bank Line"))\n
\n
return context.Base_redirect(dialog_id, keep_items={\n
    \'portal_status_message\': translateString("Lines Unreconciled"),\n
    \'reset\': 1,\n
    \'cancel_url\': cancel_url,\n
    \'field_your_mode\': mode,\n
    \'mode\': mode,\n
    \'reconciled_uid_list\': selection_uid_list})\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>mode="reconcile", list_selection_name="", uids=(), listbox_uid=(), dialog_id=None, cancel_url=None, **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>BankReconciliation_reconcileTransactionList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
