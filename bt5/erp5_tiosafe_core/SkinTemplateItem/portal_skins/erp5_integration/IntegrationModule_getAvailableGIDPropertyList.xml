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
if "person_module" in context.getId():\n
  property_list = ((\'First Name\',\'firstname\'),\n
                  (\'Last Name\',\'lastname\'),\n
                  (\'Birthday\',\'birthday\'),\n
                  (\'Email\',\'email\'))\n
\n
\n
elif context.getId() == "product_module":\n
  property_list = ((\'Title\',\'title\'),\n
                  (\'Reference\',\'reference\'),\n
                  (\'Ean13\',\'ean13\'),(\'ID\',\'id\'))\n
\n
\n
elif context.getId() == "sale_order_module":\n
  property_list = ((\'Reference\',\'reference\'),)\n
\n
\n
elif "organisation_module" in context.getId():\n
  property_list = ((\'Title\',\'title\'),\n
                  (\'Country\',\'country\'),\n
                  (\'Email\',\'email\'))\n
\n
elif "payment_transaction_module" in context.getId():\n
  property_list = ((\'Title\',\'title\'),\n
                  (\'Reference\',\'reference\'),(\'ID\',\'id\'))\n
\n
return property_list\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>IntegrationModule_getAvailableGIDPropertyList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
