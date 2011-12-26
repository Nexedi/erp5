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
  Render an entire Pad and needed JavaScript code.\n
  Used to make instant Pad switching.\n
"""\n
from json import dumps\n
\n
pad = context.restrictedTraverse(pad_relative_url)\n
\n
# render Pad\'s html\n
body = pad.KnowledgePad_viewDashboardWidget(real_context=context,\n
                                            columns=1)\n
\n
\n
# \'keep_items\' to be used as \'params\' to \'updater\' javascript method call\n
portal_type_list = ["Web Page", "Web Illustration", "Web Table"]\n
keep_items = dict(SearchableText=\'\',\n
                  portal_type=portal_type_list)\n
\n
# generate needed JavaScript code (even for \'public\' boxes)\n
javascript_list = []\n
for box in pad.objectValues():\n
  gadget = box.getSpecialiseValue()\n
  gadget_type = gadget.getRenderType()\n
  if box.getValidationState() in [\'visible\', \'invisible\', \'public\'] \\\n
        and gadget_type==\'asynchronous\' and gadget.getValidationState()!=\'invisible\':\n
    edit_form_id=gadget.getEditFormId()\n
    view_form_id=gadget.getViewFormId()\n
    base_url = \'%s/%s\' %(context.absolute_url(), view_form_id) \n
    box_dom_id = box.getRelativeUrl().replace(\'/\', \'_\')\n
    view_form_dom_id = \'%s_content\' %box_dom_id;\n
    javascript_code = pad.KnowledgePad_generateAjaxCall(base_url, box, \\\n
                            view_form_dom_id, params=keep_items, \\\n
                            ignore_security_check=1)\n
    javascript_list.append(javascript_code)\n
javascript = \'\'.join(javascript_list)\n
\n
result = {\'body\': body,\n
          \'javascript\':  javascript}\n
\n
return dumps(result)\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>pad_relative_url, mode</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>WebSection_getUNGDocumentListPadAsJSON</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
