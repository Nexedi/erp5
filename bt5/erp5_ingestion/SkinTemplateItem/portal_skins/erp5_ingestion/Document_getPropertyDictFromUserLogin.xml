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
            <value> <string>"""\n
Gets document properties discovered from the user who contributes / owns the document.\n
User would be usually the current user, but sometimes the name has to be given explicitly\n
if e.g. the doc is contributed by email, and the script is run by zope user.\n
"""\n
assignment_dict = context.ERP5Site_getPersonAssignmentDict(user_name=user_name)\n
group_list = assignment_dict[\'group_list\']\n
\n
if group_list:\n
  group_level_dict = {}\n
  for group in group_list:\n
    group_level = len(group.split("/"))\n
    group_level_dict[group] = group_level\n
  \n
  #Get the highest levels groups of the assignments\n
  ##if group_list = [\'g1\', \'g1/g1.1\', \'g1/g1.2\'] returns [\'g1\']\n
  ##if group_list = [\'g1/g1.1\', \'g1/g1.2\'] returns [\'g1/g1.1\', \'g1/g1.2\']\n
  highest_level_group_value = min(group_level_dict.itervalues())\n
  highest_level_group_list = [k for k in group_level_dict if group_level_dict[k] == highest_level_group_value]\n
  return {\'group_list\': highest_level_group_list}\n
\n
return {}\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>user_name=None</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Document_getPropertyDictFromUserLogin</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
