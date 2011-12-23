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
This script returns the list of property that can be used\n
to configure the GID for a given portal type\n
"""\n
property_list = ()\n
if portal_type == "Person":\n
  property_list = ((\'First Name\',\'firstname\'),\n
                  (\'Last Name\',\'lastname\'),\n
                  (\'Birthday\',\'birthday\'),\n
                  (\'Email\',\'email\'))\n
\n
\n
if portal_type == "Product":\n
  property_list = ((\'Title\',\'title\'),\n
                  (\'Reference\',\'reference\'),\n
                  (\'Ean13\',\'ean13\'),)\n
\n
\n
if portal_type == "Sale Order":\n
  property_list = ((\'Reference\',\'reference\'),)\n
\n
\n
return property_list\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>portal_type</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>SynchronizationConfiguratorItem_getAvailablePropertyList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
