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
This script notify the user that the form has been submitted\n
"""\n
from Products.DCWorkflow.DCWorkflow import ValidationFailed\n
from AccessControl import getSecurityManager\n
\n
form = state_change[\'object\']\n
portal = form.getPortalObject()\n
\n
translateString = portal.Base_translateString\n
portal_catalog = portal.portal_catalog\n
\n
\n
\n
u = getSecurityManager().getUser()\n
recipient = portal.portal_catalog.getResultValue(portal_type=\'Person\', reference=u)\n
 \n
\n
# Build the message and translate it\n
msg = []\n
\n
form_id = form.getId()\n
procedure=translateString(form.getPortalType())\n
\n
\n
wf_info=form.Egov_getProcedureWorkflowStateInfo(\'egov_universal_workflow\',\'pending\')\n
date_of_submission=wf_info[\'time\'].strftime(\'%d/%m/%y %H:%M\')\n
\n
subject = translateString("[E-government] Your ${procedure}  reference: ${form_id} has been submitted", \n
                           mapping = dict(procedure=procedure, form_id=form_id))\n
\n
msg_content=""" \n
\n
Your ${procedure} has been transmitted under the reference : ${form_id}, at ${date_of_submission}.\n
\n
The procedure is pending and will continue after your payment.\n
\n
E-government TEAM\n
\n
"""\n
\n
msg_content = translateString(msg_content,\n
                              mapping=dict(procedure=procedure, \n
                                           form_id=form_id,\n
                                           date_of_submission=date_of_submission\n
                                          )\n
                             )\n
\n
# We can now notify the accoutant through the notification tool\n
portal.portal_notifications.sendMessage(recipient=recipient, \n
    subject=subject, message=msg_content, portal_type_list=[\'%s\' % form.getPortalType(),],\n
    store_as_event=True)\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>state_change</string> </value>
        </item>
        <item>
            <key> <string>_proxy_roles</string> </key>
            <value>
              <tuple>
                <string>Assignor</string>
                <string>Manager</string>
                <string>Owner</string>
              </tuple>
            </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>sendPendingNotificationByMail</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
