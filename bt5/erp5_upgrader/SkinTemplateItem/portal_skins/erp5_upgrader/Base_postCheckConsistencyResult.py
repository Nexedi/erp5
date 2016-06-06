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
            <value> <string>active_process = context.getPortalObject().restrictedTraverse(active_process)\n
\n
# We don\'t need check more if something is already inconsistent\n
if active_process.ActiveProcess_sense() and not fixit:\n
  return\n
\n
constraint_message_list = context.checkConsistency(\n
  fixit=fixit, filter=filter,)\n
\n
if constraint_message_list and not active_process.getResultList():\n
  active_process.postActiveResult(\n
    severity=0 if fixit else 1,\n
    summary="%s Consistency - At least one inconsistent object found" % (\'Fix\' if fixit else \'Check\', ),\n
    detail=[m.message for m in constraint_message_list])\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>fixit, filter, active_process</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Base_postCheckConsistencyResult</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
