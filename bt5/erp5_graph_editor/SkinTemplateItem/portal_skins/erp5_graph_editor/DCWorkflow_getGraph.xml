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
            <value> <string>from Products.ERP5Type.Message import translateString\n
import json\n
portal = context.getPortalObject()\n
\n
# if a graph has been saved, we use this info for node coordinates.\n
position_graph = context.getProperty(\'jsplumb_graph\')\n
if position_graph:\n
  position_graph = json.loads(position_graph)[\'graph\']\n
\n
# TODO:\n
#  select after script in edge properties\n
#  checked box for validation ? or at least select before script\n
\n
def getDCWorkflowGraph(dc_workflow):\n
  graph = dict(node=dict(), edge=dict())\n
  for state in dc_workflow.states.objectValues():\n
    is_initial_state = state.getId() == dc_workflow.states.initial_state\n
    graph[\'node\'][state.getId()] = dict(\n
      _class=\'dc_workflow.state\',\n
      name=state.title_or_id(),\n
      is_initial_state="Yes" if is_initial_state else "No")\n
    if is_initial_state:\n
      graph[\'node\'][state.getId()][\'css\'] = { "color": "red" } # TODO: use different CSS for initial state\n
\n
    for transition in state.transitions:\n
      if transition in dc_workflow.transitions:\n
        transition = dc_workflow.transitions[transition]\n
        if transition.new_state_id:\n
          graph[\'edge\']["%s_%s" % (state.getId(), transition.id)] = (\n
              dict(_class=\'dc_workflow.transition\',\n
                   source=state.getId(),\n
                   destination=transition.new_state_id,\n
                   name=transition.actbox_name or transition.title_or_id(),\n
                   description=transition.description,\n
                   actbox_url=transition.actbox_url,\n
                   transition_id=transition.getId() # used for edition.\n
                  ))\n
\n
  if position_graph:\n
    for state_id in graph[\'node\'].keys():\n
      if state_id in position_graph[\'node\']:\n
        graph[\'node\'][state_id][\'coordinate\'] = position_graph[\'node\'][state_id][\'coordinate\']\n
  return graph\n
\n
\n
class_definition = {\n
  \'dc_workflow.transition\': {\n
    \'_class\': \'edge\',\n
    \'type\': \'object\',\n
    \'description\': \'A DCWorkflow Transition\',\n
    \'properties\': {\n
      \'name\': {\n
        \'type\': \'string\',\n
        \'name\': \'Name\',\n
        \'description\': \'Name of this transition, will be displayed in the document actions\',\n
      },\n
      \'description\': {\n
        \'type\': \'string\',\n
        \'name\': \'Description\',\n
      },\n
      \'actbox_url\': {\n
        \'type\': \'string\',\n
        \'name\': \'Action URL\',\n
        \'description\': \'URL of the action, variables will be substitued. XXX TODO: higher level ! just configure "script name" \'\n
      },\n
    }\n
  },\n
  \'dc_workflow.state\': {\n
    \'_class\': \'node\',\n
    \'type\': \'object\',\n
    \'description\': \'A DCWorkflow State\',\n
    \'properties\': {\n
      \'name\': {\n
        \'type\': \'string\',\n
        \'name\': \'Name\',\n
        \'description\': \'The name of the state, will be displayed in document view\',\n
      },\n
      \'id\': {\n
        \'type\': \'string\',\n
        \'name\': \'Id\',\n
        \'description\': \'Id of the state, will be used for catalog searches\',\n
      },\n
      \'is_initial_state\': {\n
        \'type\': \'string\',\n
        \'enum\': [\'Yes\', \'No\'],\n
        \'name\': \'Is initial State\',\n
        \'description\': \'Set to Yes if this state is the initial state for newly created documents\',\n
      },\n
    }\n
  }\n
}\n
\n
return json.dumps(dict(graph=getDCWorkflowGraph(context), class_definition=class_definition), indent=2)\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>DCWorkflow_getGraph</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
