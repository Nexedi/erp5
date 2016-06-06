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
            <value> <string>"""This script fix dialog actions to add an empty dialog for object_print\n
actions that does not provide one.\n
"""\n
from Products.PythonScripts.standard import url_quote\n
\n
if dialog_category != \'object_print\':\n
  return actions.get(dialog_category, [])\n
\n
def addDialogIfNeeded(url):\n
  \'\'\'If the action url is not a dialog, we add a generic print dialog.\n
  \'\'\'\n
  parts = url.split(\'/\')\n
  absolute_url = \'/\'.join(parts[:-1])\n
  action = parts[-1]\n
  action_id = action.split(\'?\')[0]\n
  form = getattr(context, action_id, None)\n
  #if not (hasattr(form, \'pt\') and form.pt == \'form_dialog\'):\n
  if form is not None:\n
    url = \'%s/Base_viewIntermediatePrintDialog?dialog_action_url=%s\' % (\n
                 context.absolute_url(), url_quote(\'%s/%s\' % (absolute_url, action)))\n
  return url\n
\n
print_action_list = actions[\'object_print\']\n
new_print_action_list = []\n
for ai in print_action_list:\n
  ai_copy = ai.copy()\n
  # this is quite low level. It may require to be done from file system code in\n
  # the future.\n
  #ai_copy[\'original_url\'] = ai_copy[\'url\']\n
  #ai_copy[\'url\'] = addDialogIfNeeded(ai_copy[\'url\'])\n
  new_print_action_list.append( ai_copy )\n
\n
return new_print_action_list\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>actions, dialog_category</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Base_fixDialogActions</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
