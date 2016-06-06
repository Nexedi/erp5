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
solver_process = portal.portal_solver_processes.newSolverProcess(context)\n
solver_decision, = [x for x in solver_process.objectValues()\n
  if x.getCausalityValue().getTestedProperty() == property]\n
solver_decision.setSolverValue(portal.portal_solvers[\'Unify Solver\'])\n
solver_decision.updateConfiguration(tested_property_list=[property], value=value)\n
solver_process.buildTargetSolverList()\n
solver_process.solve()\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>property, value</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>SalePackingList_solveForTesting</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
