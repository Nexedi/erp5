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
            <value> <string>line = context.getParentValue()\n
budget = line.getParentValue()\n
budget_model = budget.getSpecialiseValue(portal_type=\'Budget Model\')\n
if budget_model is None:\n
  kw = {}\n
else:\n
  kw = budget_model.getInventoryQueryDict(context)\n
\n
if from_date:\n
  kw[\'from_date\'] = from_date\n
if at_date:\n
  kw[\'at_date\'] = at_date\n
\n
portal = budget.getPortalObject()\n
kw.setdefault(\'stock_explanation_simulation_state\',\n
              portal.getPortalReservedInventoryStateList() +\n
              portal.getPortalCurrentInventoryStateList() +\n
              portal.getPortalTransitInventoryStateList())\n
\n
# XXX use getBudgetConsumptionMethod ?\n
if src__:\n
  return \'-- %s\\n%s\' % (kw, portal.portal_simulation.getCurrentInventoryAssetPrice(src__=src__, **kw))\n
return (portal.portal_simulation.getInventoryAssetPrice(**kw) or 0) * line.BudgetLine_getConsumptionSign()\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>src__=0, from_date=None, at_date=None</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>BudgetCell_getEngagedBudget</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
