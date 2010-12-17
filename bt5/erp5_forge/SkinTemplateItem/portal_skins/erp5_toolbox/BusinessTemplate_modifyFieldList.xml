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
            <value> <string encoding="cdata"><![CDATA[

listbox_line_list = list(listbox)\n
listbox_line_list.sort(key=lambda x: (x[\'choice\'], x[\'listbox_key\']))\n
\n
for listbox_line in listbox_line_list:\n
  choice = listbox_line[\'choice\']\n
  key = listbox_line[\'listbox_key\']\n
\n
  if not choice:\n
    continue\n
  elif len(choice) > 1:\n
    raise ValueError, \'Unknown choice %s\' % choice\n
  else:\n
    choice = choice[0]\n
    if choice.startswith(\'0_\'):\n
      continue\n
    elif choice == \'1_create_form\':\n
      skin_folder_id, form_id = key.split(\'/\')\n
      skin_folder = context.portal_skins[skin_folder_id]\n
      skin_folder.manage_addProduct[\'ERP5Form\'].addERP5Form(id=form_id, title=\'\')\n
    elif choice == \'2_unproxify_field\':\n
      key_list = key.split(\'/\')\n
      form_path, field_id = \'/\'.join(key_list[:-1]), key_list[-1]\n
      form = context.portal_skins.restrictedTraverse(form_path)\n
      form.unProxifyField({field_id: None})\n
    elif choice == \'4_delete_form\':\n
      skin_folder_id, form_id = key.split(\'/\')\n
      skin_folder = context.portal_skins[skin_folder_id]\n
      skin_folder.manage_delObjects([form_id])\n
      # skin_folder.manage_addProduct[\'ERP5Form\'].addERP5Form(id=form_id, title=\'\')\n
      # raise NotImplementedError\n
    else:\n
      raise ValueError, \'Unknown choice %s\' % choice\n
\n
context.Base_redirect()\n


]]></string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>listbox, **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>BusinessTemplate_modifyFieldList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
