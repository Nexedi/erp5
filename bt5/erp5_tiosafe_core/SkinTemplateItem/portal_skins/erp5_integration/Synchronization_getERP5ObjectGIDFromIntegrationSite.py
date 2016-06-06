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
            <value> <string>configurator = context.getPortalObject().portal_integrations[site_id][module_id]\n
prefix = configurator.getGidPrefix("")\n
property_list = configurator.getGidPropertyList()\n
mapped_property_list = []\n
\n
gid = prefix\n
\n
property_mapping = {"firstname" : "first_name",\n
                    "lastname" : "last_name",\n
                    "birthday" :"start_date",\n
                    "email" : "default_email_text"}\n
\n
for prop in property_list:\n
  if prop == "country":\n
    prop_value = object.contentValues(portal_type="Address")[0].getRegion("")\n
  else:\n
    mapped_prop = property_mapping.get(prop, prop)\n
    if reverse:\n
      mapped_property_list.append(mapped_prop)\n
      continue\n
    prop_value = object.getProperty(mapped_prop)\n
  if isinstance(prop_value, unicode):\n
    prop_value = prop_value.encode(\'utf-8\')\n
  gid += " %s" %(prop_value,)\n
\n
if reverse:\n
  return mapped_property_list\n
\n
return gid\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>object=None, site_id="", module_id="", reverse=False</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Synchronization_getERP5ObjectGIDFromIntegrationSite</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
