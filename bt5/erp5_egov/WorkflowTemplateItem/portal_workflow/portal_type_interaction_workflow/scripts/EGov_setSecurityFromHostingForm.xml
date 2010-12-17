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
            <value> <string>procedure_request = state_change[\'object\']\n
\n
nb_line = 32\n
\n
# map_role_dict = {\'access_type\':\'erp5_mapped_role_name\'}\n
map_role_dict = {\'View\':\'Auditor\',\n
                 \'Process\':\'Assignee\',\n
                 \'Validate\':\'Assignor\',\n
                 \'Associate\':\'Associate\'\n
                }\n
\n
# map_group_function_dict = {\'index\':[\'group_relative_url\',\'function_relative_url\', list(erp5_mapped_role_name)]}\n
map_group_function_dict = {}\n
\n
\n
# Get the procedure\'s target\n
\n
j=0\n
for i in range (nb_line)[1:]:\n
  param_list = []\n
  role_list=[]\n
  if hasattr(procedure_request, \'getInvolvedServiceFunction%s\' % i) and hasattr(procedure_request, \'getInvolvedServiceGroup%s\' % i):\n
    getFunction = getattr(procedure_request, \'getInvolvedServiceFunction%s\' % i, None)\n
    getGroup = getattr(procedure_request, \'getInvolvedServiceGroup%s\' % i, None)\n
    if getFunction():\n
      param_list.append(\'function/%s\' % getFunction())\n
    if getGroup():\n
      param_list.append(\'group/%s*\' % getGroup())      \n
\n
  if hasattr(procedure_request, \'getInvolvedServiceView%s\' % i): \n
    getView = getattr(procedure_request, \'getInvolvedServiceView%s\' % i, None)\n
    if getView(): \n
      role_list.append(map_role_dict[\'View\'])\n
\n
  if hasattr(procedure_request, \'getInvolvedServiceValidate%s\' % i): \n
    getValidate = getattr(procedure_request, \'getInvolvedServiceValidate%s\' % i, None)\n
    if getValidate(): \n
      role_list.append(map_role_dict[\'Validate\'])\n
\n
  if hasattr(procedure_request, \'getInvolvedServiceProcess%s\' % i): \n
    getProcess = getattr(procedure_request, \'getInvolvedServiceProcess%s\' % i, None)\n
    if getProcess(): \n
      role_list.append(map_role_dict[\'Process\'])\n
\n
  if hasattr(procedure_request, \'getInvolvedServiceAssociate%s\' % i): \n
    getAssociate = getattr(procedure_request, \'getInvolvedServiceAssociate%s\' % i, None)\n
    if getAssociate(): \n
      role_list.append(map_role_dict[\'Associate\']) \n
      \n
  if param_list and role_list: \n
    role_definition = \',\'.join(role_list)\n
    param_list.append(role_definition)\n
    map_group_function_dict[j] = param_list\n
    j=j+1\n
\n
\n
#Create the default role for Assignee\n
procedure_request.newContent(portal_type=\'Role Information\',\n
                     title=\'Default Assignee Role Information\',\n
                     role_name=\'Assignee\',\n
                     description=\'Last assigned person\',\n
                     role_base_category_script_list=\'group function site\',\n
                     role_base_category_script_id=\'ERP5Site_getSecurityFromWorkflowAssignment\',\n
                     )\n
\n
"""\n
#Create Associate user or service role\n
procedure_request.newContent(portal_type=\'Role Information\',\n
                     title=\'Default Associate User or Service Role Information\',\n
                     role_name_list=[Associate, Assignee],\n
                     description=\'Any associate user or service\',\n
                     role_base_category_script_id=\'ERP5Site_getSecurityFromWorkflowHistory\',\n
                     )\n
"""\n
\n
#XXX Sometimes securities are generated using information in form\n
#In this case a specific function sould be used as role_base_category_script_id\n
for (seq,role_definition) in map_group_function_dict.items():\n
  role_name = role_definition[-1]\n
  role_name_list = role_name.split(\',\')\n
  procedure_request.newContent(portal_type=\'Role Information\',\n
                     title=\'Role Information %s\' % (seq+1),\n
                     role_name_list=role_name_list,\n
                     description=\'Generated Role Information - %s \' % role_name,\n
                     role_base_category_list=\'group function\',\n
                     role_base_category_script_id=\'\',\n
                     role_category_list=role_definition[:-1])\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>state_change</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>EGov_setSecurityFromHostingForm</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
