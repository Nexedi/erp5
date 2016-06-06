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
            <value> <string>so_dict = parameter_dict.copy()\n
\n
billing_user = "%s %s" %(parameter_dict[\'billing_firstname\'], parameter_dict[\'billing_lastname\'])\n
site = context.getIntegrationSite()\n
\n
# Compute the gid the main user\n
gid_prefix = context.getParentValue().person_module.getGidPrefix("")\n
gid_property_list = context.getParentValue().person_module.getGidPropertyList()\n
person_gid = [gid_prefix,]\n
for prop in gid_property_list:\n
  if prop == "firstname":\n
    person_gid.append(parameter_dict[\'billing_firstname\'])\n
  elif prop == "lastname":\n
    person_gid.append(parameter_dict[\'billing_lastname\'])\n
  elif prop == "email":\n
    person_gid.append(parameter_dict[\'user_email\'])\n
person_gid = " ".join(person_gid)\n
\n
# First the invoice part\n
if parameter_dict.get("billing_company", None):\n
  # We have an organisation, compute its GID\n
  gid_prefix = context.getParentValue().organisation_module.getGidPrefix("")\n
  gid_property_list = context.getParentValue().organisation_module.getGidPropertyList()\n
  gid = [gid_prefix,]\n
  for prop in gid_property_list:\n
    if prop == "title":\n
      gid.append(parameter_dict[\'billing_company\'])\n
    elif prop == "country":\n
      region = site.getCategoryFromMapping(category = \'Country/%s\' % parameter_dict[\'billing_address_country\'],\n
                                           create_mapping=True,\n
                                           create_mapping_line=True,\n
                                           ).split(\'/\', 1)[-1]\n
      gid.append(region)\n
    elif prop == "email":\n
      gid.append(parameter_dict[\'user_email\'])\n
  gid = " ".join(gid)\n
  so_dict[\'destination_administration\'] = gid\n
  so_dict[\'destination_ownership\'] = gid\n
  so_dict[\'destination_decision\'] = person_gid\n
else:\n
  # We have the person\n
  so_dict[\'destination_administration\'] = person_gid\n
  so_dict[\'destination_ownership\'] = person_gid\n
  so_dict[\'destination_decision\'] = person_gid\n
\n
# Then the shipping part\n
if parameter_dict.get("shipping_company", None):\n
  # We have an organisation, compute its GID\n
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
      gid.append(parameter_dict[\'user_email\'])\n
  gid = " ".join(gid)\n
  so_dict[\'destination\'] = gid\n
else:\n
  # We have a person, compute his GID\n
  gid_prefix = context.getParentValue().delivered_person_module.getGidPrefix("")\n
  gid_property_list = context.getParentValue().delivered_person_module.getGidPropertyList()\n
  person_gid = [gid_prefix,]\n
  for prop in gid_property_list:\n
    if prop == "firstname":\n
      person_gid.append(parameter_dict[\'shipping_firstname\'])\n
    elif prop == "lastname":\n
      person_gid.append(parameter_dict[\'shipping_lastname\'])\n
    elif prop == "email":\n
      person_gid.append(parameter_dict[\'user_email\'])\n
  person_gid = " ".join(person_gid)\n
  so_dict[\'destination\'] = person_gid\n
\n
brain_list = [brain(context=context,\n
                    object_type=context.getDestinationObjectType(),\n
                    **so_dict),]\n
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
            <value> <string>WebServiceRequest_buildOxatisSaleOrderBrain</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
