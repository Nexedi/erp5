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
params = portal.portal_selections.getSelectionParamsFor(selection_name)\n
cell_index = params.get(\'cell_index\')\n
engaged_budget = params.get(\'engaged_budget\')\n
\n
query_dict = context.BudgetLine_getInventoryQueryDictForCellIndex(\n
                  cell_index=cell_index,\n
                  engaged_budget=engaged_budget)\n
\n
query_dict[\'omit_asset_decrease\'] = True\n
return portal.portal_simulation.getInventoryAssetPrice(**query_dict)\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>selection_name, **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>BudgetLine_statDebitPrice</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
