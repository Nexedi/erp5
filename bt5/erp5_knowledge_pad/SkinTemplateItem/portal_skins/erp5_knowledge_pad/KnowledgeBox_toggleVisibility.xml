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
            <value> <string encoding="cdata"><![CDATA[

""" \n
  This script is called by drag and drop javascript framework\n
  when user click on \'Minimize\' button.\n
"""\n
# format to Zope relative URL (\'knowledge_pad_module_3_4\' -> \'knowledge_pad_module/3/4\')\n
splitted_box_relative_url = box_relative_url.split(\'_\')\n
box = context.restrictedTraverse(\'knowledge_pad_module/%s/%s\' %(splitted_box_relative_url[-2], \n
                                                               splitted_box_relative_url[-1]))\n
state = box.getValidationState()\n
if state == \'visible\':\n
  box.invisible()\n
elif state == \'invisible\':\n
  box.visible()\n


]]></string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>box_relative_url</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>KnowledgeBox_toggleVisibility</string> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string>Toggle box\'s visibility on server</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
