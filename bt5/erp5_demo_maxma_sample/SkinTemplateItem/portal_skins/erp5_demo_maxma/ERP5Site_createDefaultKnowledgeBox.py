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
            <value> <string>knowledge_pad.setTitle("Home")\n
knowledge_box = knowledge_pad.newContent(\n
  portal_type=\'Knowledge Box\',\n
  specialise=\'specialise/portal_gadgets/erp5_gadget_best_seller_products\',\n
  mode=\'total_price\',\n
  section_category=\'group/my_group\',\n
  activate_kw = activate_kw)\n
knowledge_box.visible()\n
knowledge_box.setProperty(\'method\',\'getCurrentInventoryList\')\n
\n
knowledge_box = knowledge_pad.newContent(\n
  portal_type=\'Knowledge Box\',\n
  specialise=\'specialise/portal_gadgets/erp5_gadget_contact_person\',\n
  activate_kw = activate_kw)\n
knowledge_box.visible()\n
\n
# Documentation Gadget\n
knowledge_box = knowledge_pad.newContent(\n
  portal_type=\'Knowledge Box\',\n
  specialise=\'specialise/portal_gadgets/erp5_gadget_events\',\n
  activate_kw=activate_kw)\n
knowledge_box.visible()\n
\n
# Documentation Gadget\n
knowledge_box = knowledge_pad.newContent(\n
  portal_type=\'Knowledge Box\',\n
  specialise=\'specialise/portal_gadgets/erp5_gadget_new_sale_opportunity\',\n
  activate_kw=activate_kw)\n
knowledge_box.visible()\n
\n
knowledge_pad.edit(user_layout="1##3|2##4")\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>knowledge_pad, **activate_kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>ERP5Site_createDefaultKnowledgeBox</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
