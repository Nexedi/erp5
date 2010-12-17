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
            <value> <string>\'\'\'\n
get the list of active process from the selection \n
\'\'\'\n
\n
user_name = context.portal_membership.getAuthenticatedMember().getId()\n
module_title=context.getTitle()\n
\n
active_process_dict = {}\n
\n
selection_param_list = context.portal_selections.getSelectionParamsFor(\'file_import_parameters_selection\').items()\n
\n
for (x,y) in selection_param_list:\n
  if x.startswith(\'portal_activities\'):\n
    if y[\'import_module\']==module_title and y[\'import_user_name\']==user_name:\n
      active_process_dict[x] = "Module %s, imported at %s by %s" % (y[\'import_module\'], y[\'import_date_time\'], y[\'import_user_name\'])\n
\n
active_process_list = [(y,x) for (x,y) in active_process_dict.items()]\n
\n
active_process_list.sort(lambda x, y: cmp(x[1],y[1]), reverse=True )\n
\n
return active_process_list\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>**kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Base_getActiveProcessFromSelectionList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
