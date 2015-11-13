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
solver_process = context.getSolverValueList()[-1]\n
solver_decision_uid = int(solver_decision_uid)\n
solver_decision = None\n
for solver_decision in solver_process.objectValues(portal_type="Solver Decision"):\n
  if solver_decision.getUid() == solver_decision_uid:\n
    break\n
assert solver_decision is not None, \\\n
  "unable to find solver decision with uid : %r on %r" % (\n
    solver_decision_uid, solver)\n
solver_value = None\n
if solver:\n
  solver_value = portal.restrictedTraverse(solver)\n
  solver_decision.setSolverValue(solver_value)\n
else:\n
  solver_decision.setSolverList([])\n
\n
#return solver_decision.Delivery_viewSolveDivergenceDialog.listbox_solver_configuration.widget.render(\n
return solver_decision.SolverDecision_renderSolverConfiguration(context)\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>solver=None, solver_decision_uid=None</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Delivery_getSolveDivergenceDialogParameterFormBox</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
