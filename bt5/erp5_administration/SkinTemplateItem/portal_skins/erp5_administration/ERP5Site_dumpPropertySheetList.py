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
            <value> <string>for ps in sorted(context.getPortalObject().portal_property_sheets.contentValues(), key=lambda x:x.getId()):\n
  for pd in sorted(ps.contentValues(), key=lambda x:x.getId()):\n
    print ps.getId()\n
    info_list = [\'id\', \'portal_type\', \'reference\']\n
    std_prop_list = [\'elementary_type\', \'property_default\', \'storage_id\', \'multivaluated\', \'range\', \'preference\', \'read_permission\', \'write_permission\', \'translatable\', \'translation_domain\']\n
    if pd.getPortalType() == \'Standard Property\':\n
      info_list += std_prop_list\n
    elif pd.getPortalType() == \'Acquired Property\':\n
      info_list += std_prop_list + [ \'acquisition_portal_type\', \'content_acquired_property_id_list\', \'acquisition_accessor_id\', \'acquisition_copy_value\', \'alt_accessor_id_list\', \'content_portal_type\', \'content_translation_acquired_property_id_list\', \'acquisition_object_id_list\', \'acquisition_mask_value\', \'acquisition_base_category_list\',]\n
    elif pd.getPortalType() == \'Category Property\':\n
      info_list += []\n
    elif pd.getPortalType() == \'TALES Constraint\':\n
      info_list += [\'expression\'] + [p for p in pd.propertyIds() if p.startswith(\'message\')]\n
    elif pd.getPortalType() in (\'Category Existence Constraint\', \'Category Existence Constraint\'):\n
      info_list += [\'constraint_base_category_list\'] + [p for p in pd.propertyIds() if p.startswith(\'message\')]\n
    elif pd.getPortalType() in (\'Category Membership State Constraint\', \'Acquired Category Membership State Constraint\'):\n
      info_list += [\'membership_portal_type_list\', \'constraint_base_category_list\', \'workflow_state_list\', \'workflow_variable\'] + [p for p in pd.propertyIds() if p.startswith(\'message\')]\n
\n
    elif pd.getPortalType() in (\'Property Existence Constraint\', ):\n
      info_list += [\'constraint_property_list\'] + [p for p in pd.propertyIds() if p.startswith(\'message\')]\n
    elif pd.getPortalType() in (\'Content Existence Constraint\', ):\n
      info_list += [\'constraint_portal_type\'] + [p for p in pd.propertyIds() if p.startswith(\'message\')]\n
    elif pd.getPortalType().endswith(\'Constraint\'):\n
      info_list += [] + [p for p in pd.propertyIds() if p.startswith(\'message\')]\n
    else:\n
      print "(not supported)",pd.getRelativeUrl(), pd.getPortalType()\n
\n
\n
    print " ", "\\n  ".join([\'%s: %s\' % (prop, pd.getProperty(prop)) for prop in sorted(info_list)])\n
    print\n
\n
return printed\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>ERP5Site_dumpPropertySheetList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
