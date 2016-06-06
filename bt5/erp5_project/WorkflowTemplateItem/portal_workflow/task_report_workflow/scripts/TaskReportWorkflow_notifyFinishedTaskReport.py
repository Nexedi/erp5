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
            <value> <string>task_report = state_change[\'object\']\n
portal = task_report.getPortalObject()\n
\n
# Notify the requester.\n
source_person = task_report.getSourceValue(portal_type="Person")\n
destination_decision_person = task_report.getDestinationDecisionValue(portal_type="Person")\n
if destination_decision_person is None:\n
  destination_decision_person = task_report.getDestinationValue(portal_type="Person")\n
\n
# We send a message only if the requester have an email and \n
# the assignee is a user that can view the task report.\n
if source_person is not None \\\n
     and destination_decision_person is not None \\\n
     and destination_decision_person.getDefaultEmailText() \\\n
     and destination_decision_person.getReference():\n
  if len(portal.acl_users.erp5_users.getUserByLogin(source_person.getReference())):\n
    message = """\n
%s has finished the task report titled with %s.\n
Please look at this URL:\n
%s/%s\n
""" % (source_person.getTitle(), task_report.getTitle(),\n
       task_report.ERP5Site_getAbsoluteUrl(), task_report.getRelativeUrl())\n
    portal.portal_notifications.sendMessage(sender=source_person, recipient=destination_decision_person,\n
                                            subject="Task Report Finished", message=message)\n
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
                <string>Manager</string>
              </tuple>
            </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>TaskReportWorkflow_notifyFinishedTaskReport</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
