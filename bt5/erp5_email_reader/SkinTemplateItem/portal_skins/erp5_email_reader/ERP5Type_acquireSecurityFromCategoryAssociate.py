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
WARNING: this script requires proxy manager\n
\n
This script tries to acquire category values from other objects\n
\n
base_category_list - list of category values we need to retrieve\n
object             - object which we want to assign roles to.\n
"""\n
category_dict = {}\n
\n
if object is None:\n
  return []\n
\n
for base_category in base_category_list:\n
  for o in object.getValueList(base_category):\n
    for user, role_list in o.get_local_roles():\n
      for role in role_list:\n
        if role == \'Associate\':\n
          category_dict.setdefault(\'Assignee\', []).append(user)\n
          category_dict.setdefault(\'Assignor\', []).append(user)\n
          category_dict.setdefault(\'Auditor\', []).append(user)\n
          category_dict.setdefault(\'Associate\', []).append(user)\n
\n
# By returning a dict, we force force ERP5Type\n
# to interprete the result as a mapping from\n
# roles to existing security groups \n
return category_dict\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>ERP5Type_acquireSecurityFromCategoryAssociate</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
