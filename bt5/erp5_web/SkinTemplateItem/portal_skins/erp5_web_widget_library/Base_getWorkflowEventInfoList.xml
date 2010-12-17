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
  Return a merge list of all workflow history sorted by time.\n
  Result is returned as a sorted list of tempobject (returned by\n
  Base_getWorkflowHistoryItemList).\n
  This script can easily be used as list method by a listbox\n
"""\n
\n
from Products.CMFCore.WorkflowCore import WorkflowException\n
history = {}\n
workflow_id_list = [workflow_id for workflow_id, workflow_state in context.getWorkflowStateItemList()]\n
for wf_id in workflow_id_list:\n
  try:\n
    history[wf_id]=context.Base_getWorkflowHistoryItemList(workflow_id=wf_id)\n
  except WorkflowException:\n
     # some workflow don\'t have history\n
     pass\n
\n
event_list = []\n
for worrkflow_id in history.keys():\n
  event_list += history[worrkflow_id]\n
if sort: event_list.sort(key=lambda x:x.time, reverse=True)\n
return event_list\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>sort=1</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Base_getWorkflowEventInfoList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
