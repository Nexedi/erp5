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
            <value> <string>bug_line = context\n
bug = bug_line.getParentValue()\n
project = bug.getSourceProjectValue()\n
portal = bug.getPortalObject()\n
if project is not None:\n
  recipient_list = [ i.getParentValue() for i in project.getDestinationProjectRelatedValueList(portal_type="Assignment")]\n
else:\n
  recipient_list = bug_line.getDestinationValueList() or bug.getDestinationValueList()\n
  recipient_list.extend(bug_line.getSourceValueList() or bug.getSourceValueList())\n
\n
#If highest level of severity is reach, send Notifications also to source_decision\n
if bug.getBugSeverityUid() is not None:\n
  bug_severity_list = portal.portal_categories.bug_severity.getCategoryChildValueList(sort_on=\'int_index\')\n
  if bug_severity_list and\\\n
     bug_severity_list[-1].getUid() ==\\\n
     bug.getBugSeverityUid():\n
    recipient_list.extend(bug.getSourceDecisionValueList())\n
\n
unique_recipient_list = []\n
for recipient in recipient_list:\n
  if recipient.getRelativeUrl() not in [ur.getRelativeUrl() for ur in unique_recipient_list]:\n
    unique_recipient_list.append(recipient)\n
return unique_recipient_list\n
</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>BugLine_getRecipientValueList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
