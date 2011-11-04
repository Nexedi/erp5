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
            <value> <string>im = context\n
pub = im.getSourceSectionValue()\n
pub_sub_list = pub.objectValues()\n
if not len(pub_sub_list):\n
  raise ValueError, "%s sub in pub %s for im %s" %(len(pub_sub_list), pub.getPath(), im.getPath())\n
else:\n
  pub_sub = pub_sub_list[0]\n
#pub_sub = im.getSourceSectionValue().objectValues()[0]\n
\n
sub = im.getDestinationSectionValue()\n
\n
pub_xml = []\n
sub_xml = []\n
\n
for sign in sub.objectValues():\n
  pub_sign = pub_sub.get(sign.getId(), "No signature")\n
  pub_xml.append(pub_sign.getData(\'\'))\n
  sub_xml.append(sign.getData(\'\'))\n
\n
pub_xml = \'\\n\'.join(pub_xml)\n
sub_xml = \'\\n\'.join(sub_xml)\n
\n
return context.diffXML(sub_xml, pub_xml)\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>IntegrationModule_getSignatureDiff</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
