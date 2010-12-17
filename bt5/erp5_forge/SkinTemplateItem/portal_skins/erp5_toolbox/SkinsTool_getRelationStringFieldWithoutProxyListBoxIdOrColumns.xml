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
            <value> <string>multi_relation_field_meta_type_list = [\'RelationStringField\',\n
                                       \'MultiRelationStringField\']\n
for field_path, field in context.ZopeFind(\n
            context.portal_skins, obj_metatypes=multi_relation_field_meta_type_list + \n
                                                [\'ProxyField\'], search_sub=1):\n
  if field.meta_type == \'ProxyField\':\n
    template_field = field.getRecursiveTemplateField()\n
    if template_field is None or template_field.meta_type not in multi_relation_field_meta_type_list:\n
      continue\n
\n
  # acceptable if in a field library ?\n
  form = field.aq_parent\n
  if form.getId().endswith(\'FieldLibrary\'):\n
    continue\n
\n
  if not (field.get_value(\'proxy_listbox_ids\') or field.get_value(\'columns\')):\n
    print field_path\n
    continue\n
  \n
  for path, name in field.get_value(\'proxy_listbox_ids\'):\n
    if context.restrictedTraverse(path, None) is None:\n
      print \'   PROBLEM: field %s uses an invalid form for %s: %s\' % (field_path, name, path)\n
    else:\n
      proxy_listbox = context.restrictedTraverse(path)\n
      if proxy_listbox.meta_type not in (\'ProxyField\', \'ListBox\'):\n
        print \'   PROBLEM: field %s uses an invalid proxy with %s meta_type\' % (field_path, proxy_listbox.meta_type)\n
return printed\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>SkinsTool_getRelationStringFieldWithoutProxyListBoxIdOrColumns</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
