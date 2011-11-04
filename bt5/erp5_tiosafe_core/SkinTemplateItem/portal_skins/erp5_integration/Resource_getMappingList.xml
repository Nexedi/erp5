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
            <value> <string>""" Retrieve the category list of the resource. """\n
\n
result_list = []\n
\n
# add to the list the shared variations\n
mapping_dict = {}\n
for mapping in context.contentValues(portal_type="Mapped Property Type"):\n
  prop = mapping.mapped_property\n
  for cell in mapping.getCellValueList(base_id=prop):\n
    cat_list = cell.getCategoryList()\n
    lcat_list = []\n
    for cat in cat_list:\n
      base = cat.split(\'/\', 1)[0]\n
      try:\n
        cat = context.portal_categories.restrictedTraverse(cat).getTitle()\n
      except KeyError:\n
        base, path = cat.split(\'/\', 1)\n
        iv = context.restrictedTraverse(path)\n
        cat = iv.getTitle()\n
      lcat_list.append(base+"/"+cat)\n
    getter_id = "get%s" %(prop.capitalize())\n
    getter = getattr(cell, getter_id)\n
    value = getter()\n
    mapping_dict[str(lcat_list)] = {\'category\' : lcat_list,}\n
    mapping_dict[str(lcat_list)][prop] = value\n
    \n
ordered_key_list = mapping_dict.keys()\n
ordered_key_list.sort()\n
\n
return [mapping_dict[key] for key in ordered_key_list]\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Resource_getMappingList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
