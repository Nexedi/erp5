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
            <value> <string>from Products.ERP5Form.Report import ReportSection\n
path = context.getPhysicalPath()\n
portal_workflow = context.getPortalObject().portal_workflow\n
return [\n
  ReportSection(\n
    form_id="Base_viewWorkflowHistory",\n
    level=1,\n
    listbox_display_mode="FlatListMode",\n
    path=path,\n
    selection_params={\n
      "workflow_id": workflow_id,\n
      "workflow_title": portal_workflow[workflow_id].title or workflow_id},\n
    temporary_selection=False)\n
  for workflow_id in context.Base_getWorkflowHistory()\n
]\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>_proxy_roles</string> </key>
            <value>
              <tuple>
                <string>Anonymous</string>
                <string>Assignee</string>
                <string>Assignor</string>
                <string>Associate</string>
                <string>Auditor</string>
                <string>Authenticated</string>
                <string>Author</string>
                <string>Manager</string>
                <string>Member</string>
                <string>Owner</string>
                <string>Reviewer</string>
              </tuple>
            </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Base_getWorkflowHistorySectionList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
