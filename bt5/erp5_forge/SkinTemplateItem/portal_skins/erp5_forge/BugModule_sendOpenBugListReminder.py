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
            <value> <string>portal = context.getPortalObject()\n
bug_module = portal.bug_module\n
server_url = portal.ERP5Site_getAbsoluteUrl()\n
\n
body_text_line_list = []\n
addBodyLine = body_text_line_list.append\n
bug_count = 0\n
\n
assigned_to_dict={}\n
not_assigned_bug_list=[]\n
\n
for bug in bug_module.searchFolder(portal_type=\'Bug\',\n
                                   simulation_state=(\'confirmed\', \'set_ready\',),\n
                                   sort_on=((\'id\', \'asc\', \'int\'),)):\n
  bug = bug.getObject()\n
  if bug.getSource():\n
    assigned_to_dict.setdefault(bug.getSource(), []).append(bug)\n
  else:\n
    not_assigned_bug_list.append(bug)\n
  bug_count += 1\n
\n
for assignee, bug_list in assigned_to_dict.items():\n
  addBodyLine(" Assigned to %s:" % bug_list[0].getSourceTitle())\n
  for bug in bug_list:\n
    addBodyLine("  [%s] %s" % (bug.getReference(), bug.getTitle()))\n
    addBodyLine("    %s/%s/view" % (server_url, bug.getRelativeUrl()))\n
    addBodyLine(\'\')\n
  addBodyLine(\'\')\n
\n
if not_assigned_bug_list:\n
  addBodyLine(\'\')\n
  addBodyLine(" Not assigned:")\n
  for bug in not_assigned_bug_list:\n
    addBodyLine("  [%s] %s" % (bug.getReference(), bug.getTitle()))\n
    addBodyLine("    %s/%s/view" % (server_url, bug.getRelativeUrl()))\n
    addBodyLine(\'\')\n
\n
if bug_count:\n
  portal.portal_notifications.sendMessage(sender=None,\n
                          recipient=[],\n
                          subject="%s: %s Open Bugs" % (portal.title_or_id(), bug_count,),\n
                          message=\'\\n\'.join(body_text_line_list))\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>BugModule_sendOpenBugListReminder</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
