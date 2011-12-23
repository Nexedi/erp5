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
            <value> <string>brain_list = []\n
org_dict = {}\n
\n
if len(parameter_dict.get(\'shipping_company\', \'\')) and  \\\n
       parameter_dict[\'shipping_company\'] != parameter_dict.get(\'relation\', \'\'):\n
  org_dict["title"] = parameter_dict[\'shipping_company\']\n
  org_dict[\'id\'] = "%s" %(parameter_dict[\'id\'])\n
#  org_dict["email"] = "%s" %(parameter_dict[\'email\'],)\n
  for key in [\'cellphone\',\n
              \'city\',\n
              \'country\',\n
              \'fax\',\n
              \'phone\',\n
              \'street\',\n
              \'zip\',\n
              ]:\n
    org_dict["shipping-%s" %key] = parameter_dict.get("shipping_address_%s" %key, None)\n
\n
  org_dict["country"] = org_dict["shipping-country"]\n
  brain_list = [brain(context=context,\n
                      object_type=context.getDestinationObjectType(),\n
                      **org_dict),]\n
\n
return brain_list\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>parameter_dict, brain</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>WebServiceRequest_buildOxatisDeliveredOrganisationBrain</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
