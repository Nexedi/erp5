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
first_person_dict = {}\n
site = context.getIntegrationSite()\n
\n
# First person dict\n
for key in [\'firstname\',\n
            \'lastname\',\n
            \'is_customer\',\n
            \'email\',\n
            \'id\',\n
            ]:\n
  first_person_dict[key] = "%s" %(parameter_dict.get(key,\'\'),)\n
# Copy the address if not from a company\n
if not parameter_dict.get(\'relation\', None):\n
  # this is the address of the person\n
  for key in [\'cellphone\',\n
              \'phone\',\n
              \'fax\',\n
              \'city\',\n
              \'country\',\n
              \'street\',\n
              \'zip\',\n
              ]:\n
    first_person_dict["billing-%s" %key] = parameter_dict.get("billing_address_%s" %key, \'\')\n
  first_person_dict[\'relation\'] = \'\'\n
else:\n
  # Find the gid of the relation\n
  gid_prefix = context.getParentValue().organisation_module.getGidPrefix("")\n
  gid_property_list = context.getParentValue().organisation_module.getGidPropertyList()\n
  gid = [gid_prefix,]\n
  for prop in gid_property_list:\n
    if prop == "title":\n
      gid.append(parameter_dict[\'relation\'])\n
    elif prop == "country":\n
      region = site.getCategoryFromMapping(category = \'Country/%s\' % parameter_dict[\'billing_address_country\'],\n
                                           create_mapping=True,\n
                                           create_mapping_line=True,\n
                                           ).split(\'/\', 1)[-1]\n
      gid.append(region)\n
    elif prop == "email":\n
      gid.append(parameter_dict[\'email\'])\n
  gid = " ".join(gid)\n
  first_person_dict[\'relation\'] = gid\n
\n
brain_list = [brain(context=context,\n
                    object_type=context.getDestinationObjectType(),\n
                    **first_person_dict),]\n
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
            <value> <string>WebServiceRequest_buildOxatisPersonBrain</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
