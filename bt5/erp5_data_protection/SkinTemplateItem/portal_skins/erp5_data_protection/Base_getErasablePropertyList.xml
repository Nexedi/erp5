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
            <value> <string>from Products.ERP5Type.Document import newTempBase\n
portal = context.getPortalObject()\n
document_to_inspect = context.getAgentValue()\n
property_map_list = document_to_inspect.getPropertyMap()\n
\n
def filterPropertyMapList(property_map):\n
  # Keep only some kind of properties\n
  # We assume that categories, dates, and numerical values\n
  # doesn\'t carry compromising data\n
  restricted_property_list = (\'id\', \'rid\', \'id_group\',\n
                              \'id_generator\', \'last_id\',\n
                              \'reference\',)\n
  return property_map[\'type\'] in (\'string\', \'data\', \'text\',) and \\\n
    property_map[\'id\'] not in restricted_property_list and \\\n
    document_to_inspect.getProperty(property_map[\'id\']) and \\\n
    document_to_inspect.hasProperty(property_map[\'id\'])\n
\n
property_map_list = filter(filterPropertyMapList, property_map_list)\n
property_map_list = document_to_inspect.Base_updatePropertyMapListWithFieldLabel(property_map_list)\n
\n
MAX_LENGHT = 25\n
listbox_object_list = []\n
for index, property_map in enumerate(property_map_list):\n
  temp_object = newTempBase(portal, \'temp%s\' % (index,))\n
  try:\n
    property_value = unicode(document_to_inspect.getProperty(property_map[\'id\']), \'utf-8\')[:MAX_LENGHT]\n
  except UnicodeDecodeError:\n
    property_value = \'Not viewable: binary content\'\n
\n
  temp_object.edit(uid=property_map[\'id\'],\n
                   property_id=property_map[\'id\'],\n
                   property_label=portal.Base_translateString(property_map.get(\'label\', \'\')),\n
                   property_description=portal.Base_translateString(property_map.get(\'description\', \'\')),\n
                   property_value=property_value)\n
  listbox_object_list.append(temp_object)\n
\n
return listbox_object_list\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>**kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Base_getErasablePropertyList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
