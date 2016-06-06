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
            <value> <string>knowledge_pad = context.restrictedTraverse(knowledge_pad_url)\n
knowledge_pad_module = knowledge_pad.getParentValue()\n
\n
# copy/paste\n
cp = knowledge_pad_module.manage_copyObjects(ids=[knowledge_pad.getId()])\n
new_id = context.knowledge_pad_module.manage_pasteObjects(\n
                                   cb_copy_data=cp)[0][\'new_id\']\n
new_knowledge_pad = knowledge_pad_module[new_id]\n
\n
# set publication section\n
new_knowledge_pad.setPublicationSectionValue(context)\n
new_knowledge_pad.visible()\n
\n
# because workflow state(i.e. visibility is set to default(invisible)\n
# set manually with respect to original\n
for original_box in knowledge_pad.objectValues(portal_type="Knowledge Box"):\n
  destination_box = new_knowledge_pad[original_box.getId()]\n
  if original_box.getValidationState() == \'visible\':\n
    destination_box.visible()\n
  elif original_box.getValidationState() == \'deleted\':\n
    destination_box.delete()\n
\n
return context.Base_redirect(cancel_url, keep_items={\n
  "portal_status_message": context.Base_translateString(\'Sticked.\')})\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>knowledge_pad_url, cancel_url=\'view\'</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>WebSection_stickKnowledgePad</string> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string>Create a local copy for this context of given Knowledge Pad</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
