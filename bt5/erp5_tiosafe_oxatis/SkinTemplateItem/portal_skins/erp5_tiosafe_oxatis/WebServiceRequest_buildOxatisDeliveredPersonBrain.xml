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
            <value> <string>main_name = "%s %s" %(parameter_dict[\'firstname\'], parameter_dict[\'lastname\'])\n
shipping_name = "%s %s" %(parameter_dict.get(\'shipping_firstname\', \'\'), parameter_dict.get(\'shipping_lastname\', \'\'))\n
\n
person_dict = {}\n
\n
\n
if len(shipping_name.strip()) and main_name != shipping_name:\n
  site = context.getIntegrationSite()\n
  # This is another person\n
  person_dict[\'id\'] = "%s" %(parameter_dict[\'id\'])\n
  person_dict["is_customer"] = parameter_dict.get(\'is_customer\', \'false\')\n
  person_dict["firstname"] = "%s" %(parameter_dict[\'shipping_firstname\'],)\n
  person_dict["lastname"] = "%s" %(parameter_dict[\'shipping_lastname\'],)\n
  person_dict["email"] = "%s" %(parameter_dict[\'email\'],)\n
  if parameter_dict.get(\'shipping_company\', None):\n
    # Find the gid of the relation\n
    gid_prefix = context.getParentValue().delivered_organisation_module.getGidPrefix("")\n
    gid_property_list = context.getParentValue().delivered_organisation_module.getGidPropertyList()\n
    gid = [gid_prefix,]\n
    for prop in gid_property_list:\n
      if prop == "title":\n
        gid.append(parameter_dict[\'shipping_company\'])\n
      elif prop == "country":\n
        region = site.getCategoryFromMapping(category = \'Country/%s\' % parameter_dict[\'shipping_address_country\'],\n
                                             create_mapping=True,\n
                                             create_mapping_line=True,\n
                                             ).split(\'/\', 1)[-1]\n
        gid.append(region)\n
      elif prop == "email":\n
        gid.append(parameter_dict[\'email\'])\n
    gid = " ".join(gid)\n
    person_dict["relation"] = gid\n
  else:\n
    for key in [\'cellphone\',\n
                \'city\',\n
                \'country\',\n
                \'fax\',\n
                \'phone\',\n
                \'street\',\n
                \'zip\',\n
                ]:\n
      if parameter_dict.has_key("shipping_address_%s" %key):\n
        person_dict["shipping-%s" %key] = parameter_dict["shipping_address_%s" %key]\n
\n
  context.log("person_dict", person_dict)\n
  brain_list = [brain(context=context,\n
                    object_type=context.getDestinationObjectType(),\n
                    **person_dict),]\n
\n
  return brain_list\n
else:\n
  return []\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>parameter_dict, brain</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>WebServiceRequest_buildOxatisDeliveredPersonBrain</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
