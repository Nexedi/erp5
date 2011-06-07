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
            <value> <string>"""Close all person assignment \n
Parameters:\n
role -- Role category item (List of String, default: [])\n
comment -- Workflow transition comment (String, default: "")\n
Proxy:\n
Assignor -- only assignor manage assignment. Needed this proxy for auto accept\n
Return opened assignment list\n
"""\n
\n
person = context.getDestinationDecisionValue(portal_type="Person")\n
\n
# Check current assignment\n
\n
current_assignment_list = person.searchFolder(portal_type="Assignment",\n
                                              validation_state="open")\n
open_assignment = []\n
for assignment in current_assignment_list:\n
  assignment = assignment.getObject()\n
  if assignment.getRole() in role:\n
    assignment.close(comment)\n
  else:\n
    open_assignment.append(assignment)\n
return open_assignment\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>role=[],comment=""</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>CredentialRequest_closePersonAssignment</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
