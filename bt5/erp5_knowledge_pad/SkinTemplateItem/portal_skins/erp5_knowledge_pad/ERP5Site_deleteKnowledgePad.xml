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
            <value> <string>pad = context.restrictedTraverse(knowledge_pad_relative_url)\n
try:\n
  # If the current active pad is deleted, activate last one.\n
  for other_pad in context.ERP5Site_getKnowledgePadListForUser(mode=mode):\n
    if other_pad != pad:\n
      if other_pad.getValidationState() != \'invisible\':\n
        break\n
      invisible = other_pad\n
  else:\n
    invisible.visible()\n
  pad.delete()\n
  msg = \'Pad removed.\'\n
except UnboundLocalError:\n
  msg = \'Can not remove the only one pad.\'\n
\n
return context.Base_redirect(form_id="view", keep_items={\n
  "portal_status_message": context.Base_translateString(msg)})\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>knowledge_pad_relative_url, mode=None</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>ERP5Site_deleteKnowledgePad</string> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string>Delete knowledge pad from server</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
