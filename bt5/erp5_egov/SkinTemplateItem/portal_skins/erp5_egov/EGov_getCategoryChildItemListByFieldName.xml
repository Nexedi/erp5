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
            <value> <string>if field_name is None or field_name=="":\n
  return [(\'\',\'\')]\n
\n
category = None\n
\n
if field_name == "my_contact_function":\n
  category = context.portal_categories.function\n
elif field_name =="my_organisation_direction_service":\n
  category = context.portal_categories.group\n
elif field_name.startswith(\'my_involved_service_group_\'):\n
  category = context.portal_categories.group\n
elif field_name.startswith(\'my_involved_service_function_\'):\n
  category = context.portal_categories.function\n
elif field_name == "my_procedure_target":\n
  category = context.portal_categories.target\n
elif field_name == "my_submission_site_list":\n
  category = context.portal_categories.site\n
elif field_name == "my_procedure_publication_section":\n
  category = context.portal_categories.publication_section\n
elif field_name == "my_submission_site":\n
  category = context.portal_categories.site\n
elif field_name.startswith("my_civility"):\n
  category = context.portal_categories.gender\n
\n
\n
if category is not None:\n
  return context.Base_getPreferredCategoryChildItemList(category, filter_node=0, translate=False)\n
elif field_name.startswith("my_attachment_model_"):\n
  portal_type_list = context.portal_catalog(portal_type=\'Contribution Predicate\')\n
  return [(\'\',\'\')] + [(a.getObject().getTitle(),a.getObject().getTitle()) for a in portal_type_list]\n
else:\n
  return [(\'\',\'\')]\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>field_name=\'\'</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>EGov_getCategoryChildItemListByFieldName</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
