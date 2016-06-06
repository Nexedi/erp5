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

from DateTime import DateTime\n
from Products.ERP5Type.Document import newTempBase\n
\n
portal = context.getPortalObject()\n
selection_params = portal.portal_selections.getSelectionParamsFor(selection_name)\n
get_inventory_kw = {\n
    \'section_category\': selection_params.get(\'section_category\')\n
  , \'simulation_state\': selection_params.get(\'simulation_state\')\n
  , \'node_category\'   : selection_params.get(\'gap_root\')\n
  , \'omit_simulation\' : True\n
  , \'where_expression\': " section.portal_type = \'Organisation\' "\n
}\n
\n
at_date   = selection_params.get(\'at_date\', None)\n
from_date = selection_params.get(\'from_date\', None)\n
\n
getInventory = portal.portal_simulation.getInventoryAssetPrice\n
\n
# FIXME: Here we do not want to sum all movement < 0, but sum the balances\n
#        of all nodes whose which have a < 0 balance...\n
opening_debit_balance  = 0.0\n
opening_credit_balance = 0.0\n
closing_debit_balance  = 0.0\n
closing_credit_balance = 0.0\n
if from_date not in (None, \'\'):\n
  opening_debit_balance = getInventory( at_date     = from_date\n
                                      , omit_output = True\n
                                      , **get_inventory_kw\n
                                      )\n
  opening_credit_balance = - getInventory( at_date    = from_date\n
                                         , omit_input = True\n
                                         , **get_inventory_kw\n
                                         )\n
closing_debit_balance = getInventory( at_date     = at_date\n
                                    , omit_output = True\n
                                    , **get_inventory_kw\n
                                    )\n
closing_credit_balance = - getInventory( at_date    = at_date\n
                                       , omit_input = True\n
                                       , **get_inventory_kw\n
                                       )\n
\n
list_item = newTempBase(portal, \'xxx\')\n
list_item.setUid(\'new_000\')\n
list_item.edit(** {\n
    \'total_opening_debit_balance\' : opening_debit_balance\n
  , \'total_closing_debit_balance\' : closing_debit_balance\n
  , \'total_opening_credit_balance\': opening_credit_balance\n
  , \'total_closing_credit_balance\': closing_credit_balance\n
  })\n
\n
return [list_item]\n


]]></string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>selection, selection_name, **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>AccountModule_getTrialBalanceSummary</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
