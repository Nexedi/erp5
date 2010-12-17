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
            <value> <string>history = context.Base_getWorkflowHistory()\n
bug_history = history.get(\'bug_workflow\', None)\n
\n
follow_up_list = []\n
\n
if bug_history is not None:\n
  title_list = bug_history[\'title_list\']\n
  item_list = bug_history[\'item_list\']\n
  index_dict = {}\n
\n
  for i in range(len(title_list)):\n
    index_dict[title_list[i]] = i\n
\n
  for item in item_list:\n
    action = item[index_dict[\'Action\']]\n
    comment = item[index_dict[\'Comment\']]\n
    time = item[index_dict[\'Time\']]\n
    actor = item[index_dict[\'Actor\']]\n
\n
    if action is not None and action.endswith(\'_action\'):\n
      if action.startswith(\'open\'):\n
        # I guess nobody wants to enter a comment to open a bug.\n
        continue\n
      if not comment:\n
        comment = \'\'\n
      else:\n
        comment = comment.strip()\n
      if not actor:\n
        actor = \'unknown\'\n
      if not time:\n
        time = \'unknown\'\n
      else:\n
        time = time.ISO()\n
      follow_up_list.append(\'%s by %s at %s:\\n%s\' % (action[:-7], actor, time, comment))\n
\n
comment_id = len(follow_up_list)\n
for i in range(len(follow_up_list)):\n
  follow_up_list[i] = (\'Comment #%d: \' % comment_id) + follow_up_list[i]\n
  comment_id -= 1\n
\n
return \'\\n\\n\'.join(follow_up_list)\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Bug_getFollowUpListAsText</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
