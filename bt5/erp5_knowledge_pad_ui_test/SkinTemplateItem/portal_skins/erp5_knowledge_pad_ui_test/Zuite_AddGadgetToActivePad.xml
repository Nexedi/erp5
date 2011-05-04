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
  Add (if not present) gadgets to current knowledge pad.\n
"""\n
active_pad, all_pads = context.ERP5Site_getActiveKnowledgePadForUser(mode, default_pad_group)\n
\n
active_pad = active_pad.getObject()\n
gadget_list = active_pad.contentValues(filter={\'portal_type\': \'Knowledge Box\'})\n
contained_gadgets = [x.getSpecialiseValue().getRelativeUrl() \\\n
                       for x in gadget_list if x.getValidationState() in (\'visible\', \'invisible\',)]\n
if gadget_relative_url not in contained_gadgets:\n
  # add only if not there\n
  knowledge_box = active_pad.newContent(portal_type=\'Knowledge Box\')\n
  knowledge_box.setSpecialiseValue(gadget_relative_url)\n
  knowledge_box.visible()\n
else:\n
  # reuse gadget\n
  knowledge_box = [x for x in gadget_list if x.getSpecialiseValue().getRelativeUrl()==gadget_relative_url][0]\n
\n
context.REQUEST.set(\'portal_status_message\', knowledge_box.getRelativeUrl())\n
return context.view()\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>gadget_relative_url, mode=\'erp5_front\', default_pad_group=None</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Zuite_AddGadgetToActivePad</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
