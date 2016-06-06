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

REQUEST=context.REQUEST\n
selection_name = REQUEST[\'selection_name\']\n
object_list = context.portal_selections.getSelectionValueList(selection_name, context=context, REQUEST=REQUEST)\n
delivery_list = []\n
for o in object_list:\n
  delivery_list.append(o)\n
\n
if len(delivery_list) < 2:\n
  ret_url = context.absolute_url() + \'/\' + form_id\n
  qs = \'?portal_status_message=Please+select+more+than+one+items.\'\n
else:\n
  ret_url = context.absolute_url() + \'/\' + form_id\n
  qs = \'?portal_status_message=Merged.\'\n
  context.portal_simulation.mergeDeliveryList(delivery_list)\n
\n
return REQUEST.RESPONSE.redirect( ret_url + qs )\n


]]></string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>form_id=\'\'</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Delivery_mergeDeliveryList</string> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string>Merge deliveries into one</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
