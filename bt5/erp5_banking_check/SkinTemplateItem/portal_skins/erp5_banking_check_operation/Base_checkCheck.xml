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
            <value> <string>from Products.ERP5Type.Message import Message\n
from Products.DCWorkflow.DCWorkflow import ValidationFailed\n
\n
# Check that a check exists for given bank account and reference.\n
if check is None:\n
  check = context.Base_checkOrCreateCheck(reference=reference, \n
                                         bank_account=bank_account,\n
                                         resource=resource)\n
\n
bad_simulation_state_dict = {\'draft\': \'The check is not issued yet.\',\n
                             \'cancelled\': \'The check has been stopped.\',\n
                             \'delivered\': \'The check has already been cashed.\',\n
                             \'stopped\': \'The check is stopped.\'}\n
\n
simulation_state = check.getSimulationState()\n
if simulation_state != \'confirmed\':\n
  if simulation_state in bad_simulation_state_dict:\n
    msg = Message(domain=\'ui\', message=bad_simulation_state_dict[simulation_state])\n
  else:\n
    msg = \'Invalid and unhandled simulation state: %s\' % (simulation_state, )\n
  raise ValidationFailed, (msg,)\n
\n
return check\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>bank_account, reference, resource, check=None</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Base_checkCheck</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
