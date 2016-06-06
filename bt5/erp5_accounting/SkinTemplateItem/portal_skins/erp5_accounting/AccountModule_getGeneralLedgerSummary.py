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
            <value> <string>from Products.PythonScripts.standard import Object\n
getInventoryAssetPrice = context.getPortalObject().portal_simulation.getInventoryAssetPrice\n
\n
inventory_kw = dict(section_uid=section_uid,\n
                    simulation_state=simulation_state,\n
                    at_date=at_date,\n
                    portal_type=context.getPortalAccountingMovementTypeList(),\n
                    )\n
if function_category:\n
  inventory_kw[\'function_category\'] = function_category\n
if function_uid:\n
  inventory_kw[\'function_uid\'] = function_uid\n
if funding_category:\n
  inventory_kw[\'funding_category\'] = funding_category\n
if funding_uid:\n
  inventory_kw[\'funding_uid\'] = funding_uid\n
if project_uid:\n
  inventory_kw[\'project_uid\'] = project_uid\n
if mirror_section_category:\n
  inventory_kw[\'mirror_section_category\'] = mirror_section_category\n
if mirror_section_uid:\n
  inventory_kw[\'mirror_section_uid\'] = mirror_section_uid\n
\n
if node_category:\n
  # XXX if node category is passed, income or balance accounts are not\n
  # calculated differently. As a result, the summary doesn\'t take from_date\n
  # into account for income accounts.\n
  return [Object(\n
            debit_price=getInventoryAssetPrice(omit_asset_decrease=1,\n
                               node_category=node_category,\n
                               precision=precision,\n
                               **inventory_kw),\n
            credit_price=-getInventoryAssetPrice(omit_asset_increase=1,\n
                               node_category=node_category,\n
                               precision=precision,\n
                                **inventory_kw) or 0 ) ]\n
\n
income_node_category = [\'account_type/income\', \'account_type/expense\']\n
balance_node_category = [\'account_type/equity\', \'account_type/asset\',\n
                         \'account_type/liability\']\n
\n
debit = getInventoryAssetPrice(omit_asset_decrease=1,\n
                               from_date=period_start_date,\n
                               node_category=income_node_category,\n
                               precision=precision,\n
                               **inventory_kw)\n
\n
credit = - getInventoryAssetPrice(omit_asset_increase=1,\n
                               from_date=period_start_date,\n
                               node_category=income_node_category,\n
                               precision=precision,\n
                                **inventory_kw) or 0\n
\n
debit += getInventoryAssetPrice(omit_asset_decrease=1,\n
                               node_category=balance_node_category,\n
                               precision=precision,\n
                               **inventory_kw)\n
\n
credit -= getInventoryAssetPrice(omit_asset_increase=1,\n
                               node_category=balance_node_category,\n
                               precision=precision,\n
                                **inventory_kw) or 0\n
\n
return [Object(debit_price=debit, credit_price=credit)]\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>section_uid, simulation_state, at_date, period_start_date, precision, node_category=None, function_category=None, function_uid=None, funding_category=None, funding_uid=None, project_uid=None, from_date=\'ignored\', mirror_section_category=None, mirror_section_uid=None, **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>AccountModule_getGeneralLedgerSummary</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
