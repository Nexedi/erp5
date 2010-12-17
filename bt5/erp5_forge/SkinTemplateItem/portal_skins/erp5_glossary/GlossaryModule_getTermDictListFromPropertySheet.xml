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
            <value> <string>ignore = (\'custom\',)\n
all_field_list = []\n
def iterate(obj):\n
  for i in obj.objectValues():\n
    if i.getId() in ignore:\n
      continue\n
    if i.meta_type==\'ERP5 Form\':\n
      all_field_list.extend(i.objectValues())\n
    elif i.isPrincipiaFolderish:\n
      iterate(i)\n
\n
iterate(context.portal_skins)\n
\n
properties = []\n
for i in property_sheet_list:\n
  properties.extend([x[0] for x in context.GlossaryModule_getPropertySheetAttributeList(i)])\n
\n
dic = {}\n
for i in all_field_list:\n
  id = i.getId()\n
  title = i.get_value(\'title\') or \'\'\n
  skin_id = i.aq_parent.aq_parent.getId()\n
  prefix = \'erp5_\'\n
  if skin_id.startswith(prefix):\n
    skin_id = skin_id[len(prefix):]\n
  if id.startswith(\'my_\'):\n
    for p in properties:\n
      if id==\'my_%s\' % p:\n
        key = (p, skin_id, title)\n
        dic[key] = i\n
  if id.startswith(\'your_\'):\n
    for p in properties:\n
      if id==\'your_%s\' % p:\n
        key = (p, skin_id, title)\n
        dic[key] = i\n
\n
result = []\n
for (reference, business_field, title) in dic.keys():\n
  language = \'en\'\n
  field = dic[(reference, business_field, title)]\n
  description = field.get_value(\'description\')\n
  field_path = \'%s/%s/%s\' % (field.aq_parent.aq_parent.getId(),\n
                            field.aq_parent.getId(),\n
                            field.getId())\n
  result.append({\'reference\':reference,\n
                 \'language\':language,\n
                 \'business_field\':business_field,\n
                 \'title\':title,\n
                 \'description\':description,\n
                 \'field_path\':field_path\n
                 })\n
\n
return result\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>property_sheet_list</string> </value>
        </item>
        <item>
            <key> <string>_proxy_roles</string> </key>
            <value>
              <tuple>
                <string>Authenticated</string>
                <string>Manager</string>
                <string>Member</string>
              </tuple>
            </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>GlossaryModule_getTermDictListFromPropertySheet</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
