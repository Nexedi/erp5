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
            <value> <string>\'\'\'This script is deprecated, it is much recommended to use\n
ERP5Site_getWorkflowStateItemList by passing the portal type and state_var instead.\n
\'\'\'\n
\n
from Products.CMFCore.utils import getToolByName\n
\n
if not (same_type(workflow_id_list, []) or same_type(workflow_id_list, ())):\n
  workflow_id_list = (workflow_id_list,)\n
\n
state_dict = {}\n
item_list = []\n
for workflow_id in workflow_id_list:\n
  workflow = getToolByName(context, \'portal_workflow\')[workflow_id]\n
  for state in workflow.states.objectValues():\n
    if state.title and state.id!=\'deleted\':\n
      if not state_dict.has_key(state.id):\n
        # we hide states without titles\n
        item_list.append((state.title, state.id))\n
        state_dict[state.id] = None\n
return item_list\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>workflow_id_list</string> </value>
        </item>
        <item>
            <key> <string>_proxy_roles</string> </key>
            <value>
              <tuple>
                <string>Auditor</string>
                <string>Manager</string>
                <string>Member</string>
              </tuple>
            </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Base_getWorkflowStateItemList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
