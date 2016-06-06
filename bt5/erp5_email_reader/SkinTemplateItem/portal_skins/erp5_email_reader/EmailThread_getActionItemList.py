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
            <value> <string>result = []\n
url = context.getRelativeUrl()\n
Base_translateString = context.Base_translateString\n
action_list = context.portal_actions.listFilteredActionsFor(context.getObject()).get(\'workflow\', [])\n
\n
\n
# Javascript code\n
hide_and_process_js = """javascript:xmlHttp=new XMLHttpRequest(); \n
xmlHttp.open("GET", "%s/EmailThread_processAction?action=%s", false);\n
xmlHttp.send(null);\n
this.parentNode.parentNode.style.display = \'none\';\n
return false;"""\n
\n
hide_and_reply_js = """javascript:this.parentNode.parentNode.style.display = \'none\';\n
window.open(\'%s/EmailThread_processReply\');\n
return false;\n
"""\n
\n
\n
# This part must be cached and optimised - XXX\n
# Idea: get the state, retrieve standard action string for the state\n
# if not available, call getObject, portal_actions, etc. \n
# build the standard action string - last, fead the action string with\n
# params through %\n
for action in action_list:\n
  action_id = action[\'id\']\n
  if action_id == \'read_action\':\n
    # Not need to display\n
    pass\n
  elif action_id == \'reply_action\':\n
    result.append((Base_translateString(action[\'title\']), hide_and_reply_js % url))\n
  else:\n
    result.append((Base_translateString(action[\'title\']), hide_and_process_js % (url, action_id)))\n
\n
#result.append((\'Info\', \'info\'))\n
#result.append((\'Subject\', \'subject\'))\n
\n
return result\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>EmailThread_getActionItemList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
