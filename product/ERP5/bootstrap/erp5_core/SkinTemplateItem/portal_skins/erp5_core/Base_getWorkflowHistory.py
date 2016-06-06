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

from ZODB.POSException import ConflictError\n
\n
history_name_list = [\'building_history\', \' installation_history\', \'history\']\n
\n
history = {}\n
\n
portal_workflow = context.getPortalObject().portal_workflow\n
workflow_id_list = [workflow_id for workflow_id, workflow_state in context.getWorkflowStateItemList()]\n
\n
for history_name in history_name_list:\n
  \n
  for wf_id in workflow_id_list:\n
    \n
    list_history_item = None\n
    try:\n
      list_history_item = portal_workflow.getInfoFor(ob=context, name=history_name, wf_id=wf_id)\n
    except ConflictError:\n
      raise\n
    except:\n
      pass\n
\n
    if list_history_item not in ((), None):\n
      \n
      history_element_title_list = []\n
      for history_element_title in list_history_item[-1].keys():\n
        if history_element_title <> history_name:\n
          new_title = history_element_title.replace(\'_\', \' \').title()\n
          history_element_title_list.append(new_title)\n
\n
      history_item_list = []\n
      for history_item in list_history_item:\n
        history_item_info = ()\n
        for history_element_title in list_history_item[-1].keys():\n
          if history_element_title <> history_name:\n
            history_item_info += (history_item.get(history_element_title),)\n
        history_item_list.append(history_item_info)\n
      history_item_list.reverse()\n
\n
      wf_history = {}\n
      wf_history[\'title_list\'] = history_element_title_list\n
      wf_history[\'item_list\']  = history_item_list\n
      history[wf_id] = wf_history\n
\n
\n
return history\n


]]></string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Base_getWorkflowHistory</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
