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
            <value> <string encoding="cdata"><![CDATA[

\'\'\'Returns a list of items (state_title, state_id) of the workflows that are chained\n
to the given portal_type(s). This can also be filtered to workflows that are using\n
a given state_var (simulation_state, validation_state etc).\n
\n
display_none_category argument controls wether the list will contain an empty item \n
as first element or not (just like category tool API)\n
\n
The state titles will be translated unless you pass translate=False\n
\'\'\'\n
if translate:\n
  from Products.ERP5Type.Message import translateString\n
else:\n
  translateString = lambda msg: msg\n
\n
workflow_tool = context.getPortalObject().portal_workflow\n
workflow_set = set() # existing workflows.\n
state_set = set([\'deleted\']) # existing state ids (we do not want to return a same state id twice \n
                             # if more than one workflow define the same state). Also note that we\n
                             # always ignore deleted state.\n
\n
result_list = display_none_category and [(\'\', \'\')] or []\n
\n
if isinstance(portal_type, basestring):\n
  portal_type = portal_type,\n
  \n
chain_dict = workflow_tool.getWorkflowChainDict()\n
for portal_type in portal_type:\n
  for workflow_id in chain_dict[\'chain_%s\' % portal_type].split(\',\'):\n
    workflow_id = workflow_id.strip()\n
    if workflow_id in workflow_set:\n
      continue\n
    workflow_set.add(workflow_id)\n
    \n
    workflow = workflow_tool[workflow_id]\n
    \n
    # skip interaction workflows or workflows with only one state (such as edit_workflow)\n
    if workflow.states is None or len(workflow.states.objectIds()) <= 1:\n
      continue\n
    \n
    # skip workflows using another state variable\n
    if state_var not in (None, workflow.variables.getStateVar()):\n
      continue\n
    \n
    for state in workflow.states.objectValues():\n
      if state.id in state_set:\n
        continue\n
      state_set.add(state.id)\n
      \n
      result_list.append((str(translateString(state.title)), state.id))\n
\n
return result_list\n


]]></string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>portal_type=(), state_var=None, display_none_category=True, translate=True</string> </value>
        </item>
        <item>
            <key> <string>_proxy_roles</string> </key>
            <value>
              <tuple>
                <string>Manager</string>
              </tuple>
            </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>ERP5Site_getWorkflowStateItemList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
