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
            <value> <string>portal = context.getPortalObject()\n
N_ = portal.Base_translateString\n
request = container.REQUEST\n
\n
style = request.get(\'your_portal_skin\',\n
        request.get(\'field_your_portal_skin\',\n
                              context.getPreferredReportStyle()))\n
\n
item_list = [(\'\', \'\')]\n
\n
from Products.ERP5.Document.Document import ConversionError\n
\n
try:\n
  if style == \'ODS\':\n
    return context.Base_getConversionFormatItemList(\n
         base_content_type=\'application/vnd.oasis.opendocument.spreadsheet\')\n
  elif style == \'ODT\':\n
    return context.Base_getConversionFormatItemList(\n
         base_content_type=\'application/vnd.oasis.opendocument.text\')\n
except ConversionError:\n
  # OOo server not here, just return empty list\n
  pass\n
\n
return item_list\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Preference_getReportFormatItemList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
