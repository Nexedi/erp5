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
            <value> <string>toggable_pad = None\n
all_knowledge_pads = context.ERP5Site_getKnowledgePadListForUser(mode=mode)\n
if isinstance(knowledge_pad_url, basestring):\n
  toggable_pad = context.restrictedTraverse(knowledge_pad_url)\n
else:\n
  # we pass object\n
  toggable_pad = knowledge_pad_url\n
\n
if toggable_pad is not None:\n
  if toggable_pad.getValidationState() == \'invisible\':\n
    toggable_pad.visible()\n
  for pad in all_knowledge_pads:\n
    if pad.getObject()!=toggable_pad and pad.getValidationState()==\'visible\':\n
      pad.invisible()\n
if redirect:\n
  context.Base_redirect(form_id="view")\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>knowledge_pad_url=None, mode=None, redirect=True</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>ERP5Site_toggleActiveKnowledgePad</string> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string>Toggle active Knowledge Pad</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
