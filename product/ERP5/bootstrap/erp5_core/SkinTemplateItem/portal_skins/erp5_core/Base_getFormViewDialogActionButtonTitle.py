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
            <value> <string>request = context.REQUEST\n
\n
button_title = request.get(\'button_title\', None)\n
if button_title is not None:\n
  return button_title\n
\n
wf_actions =  context.portal_actions.portal_actions.listFilteredActionsFor(context)[\'workflow\']\n
workflow_action = request.get(\'workflow_action\', None) or request.get(\'field_my_workflow_action\', None)\n
if workflow_action:\n
  for action in wf_actions: \n
    if action[\'id\'] == workflow_action:\n
      return action[\'name\']\n
\n
if workflow_action:\n
  # It means that workflow_action is not available now. Redirect to default view with a nice message.\n
  from Products.ERP5Type.Message import translateString\n
  message = translateString("Workflow state may have been updated by other user. Please try again.")\n
  context.Base_redirect(\'view\', keep_items={\'portal_status_message\': message})\n
\n
return form.title\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>form</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Base_getFormViewDialogActionButtonTitle</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
