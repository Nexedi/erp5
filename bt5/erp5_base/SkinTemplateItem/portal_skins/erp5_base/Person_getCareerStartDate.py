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
            <value> <string>all_career_step_list = context.contentValues(portal_type=\'Career\',\n
                                             checked_permission=\'View\')\n
\n
career_step_list = []\n
# only keep "active" career steps (and related to this organisation if given)\n
for career_step in all_career_step_list :\n
  if (subordination_relative_url is None or \\\n
      career_step.getSubordination() == subordination_relative_url) and \\\n
     career_step.getStartDate() and \\\n
     career_step.getValidationState() not in (\'cancelled\', \'deleted\'):\n
      career_step_list.append(career_step)\n
    \n
# sort them by start date\n
career_step_list.sort(key=lambda x: x.getStartDate())\n
for career_step in career_step_list :\n
  # TODO: take the first date of the last active career range.\n
  # for now, we only return the first one.\n
  return career_step.getStartDate()\n
\n
raise ValueError, \'No Career Step Defined.\'\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>subordination_relative_url=None</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Person_getCareerStartDate</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
