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
search_kw = dict(\n
  parent_portal_type=\'Payment Transaction\',\n
  limit=None,\n
  simulation_state=(\'delivered\', \'stopped\'),\n
  section_uid=context.getSourceSectionUid(),\n
  payment_uid=context.getSourcePaymentUid(),\n
  resource_uid=context.getPriceCurrencyUid(),\n
  node_category=\'account_type/asset/cash/bank\',\n
#  group_by=(\'parent_uid\', ), # The limit is not applied on the number of payment transactions, but on the number of lines (to simplify setting aggregate relation).\n
\n
  # we have \'aggregate/payment_transaction_module/xxx\' in sub_variation_text if the line is already grouped.\n
  sub_variation_text=\'\',\n
)\n
\n
if context.getPaymentMode():\n
  search_kw[\'payment_transaction_line_payment_mode_uid\'] = context.getPaymentModeUid()\n
\n
if limit:\n
  search_kw[\'limit\'] = limit\n
\n
if start_date_range_max:\n
  search_kw[\'at_date\'] = start_date_range_max.latestTime()\n
if start_date_range_min:\n
  search_kw[\'from_date\'] = start_date_range_min\n
\n
if sign in (\'outgoing\', \'out\'):\n
  search_kw[\'omit_asset_increase\'] = True\n
elif sign in (\'incoming\', \'in\'):\n
  search_kw[\'omit_asset_decrease\'] = True\n
\n
movement_history_list = portal.portal_simulation.getMovementHistoryList(**search_kw)\n
\n
# XXX this will be read by PaymentTransactionGroup_statGroupablePaymentTransactionLineList\n
# ( we could be using getInventoryStat there but this does not support limit\n
# parameter )\n
stat_total_quantity = 0\n
if movement_history_list:\n
  stat_total_quantity = movement_history_list[-1].running_total_quantity\n
container.REQUEST.set(\n
  \'PaymentTransactionGroup_statGroupablePaymentTransactionLineList.total_quantity\',\n
  stat_total_quantity)\n
\n
return movement_history_list\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>limit=None, start_date_range_min=None, start_date_range_max=None, sign=None, **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>PaymentTransactionGroup_getGroupablePaymentTransactionLineList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
