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
\n
result = []\n
\n
portal_catalog = context.portal_catalog\n
portal_skins = context.portal_skins\n
\n
def get_term_list(business_field, reference):\n
  reference = reference.rsplit(\'_title\', 1)[0]\n
  term_list = portal_catalog(portal_type=\'Glossary Term\',\n
                             validation_state=\'validated\',\n
                             language_id=\'en\',\n
                             business_field_title=(\'core\', business_field),\n
                             reference=reference)\n
  return [i.getObject() for i in term_list]\n
\n
def get_field_and_reference_list(business_field):\n
  business_field = business_field.split(\'/\')[0]\n
  result = []\n
  skin_folder = getattr(portal_skins, \'erp5_%s\' % business_field, None)\n
  if skin_folder is None:\n
    skin_folder = getattr(portal_skins, business_field)\n
\n
  for i in skin_folder.objectValues():\n
    if i.meta_type==\'ERP5 Form\':\n
      for f in i.objectValues():\n
        if f.id.startswith(\'my_\'):\n
          r = f.id[3:]\n
          result.append((f, r))\n
        elif f.id.startswith(\'your_\'):\n
          r = f.id[5:]\n
          result.append((f, r))\n
  return result\n
\n
business_field_list = [i for i in business_field_list if i]\n
\n
line_list = []\n
c = 0\n
item_dict = {}\n
for business_field in business_field_list:\n
  for field, reference in get_field_and_reference_list(business_field):\n
    term_list = get_term_list(business_field, reference)\n
    #if not term_list:\n
    #  continue\n
    if item_dict.has_key(field):\n
      continue\n
    item_dict[field] = True\n
\n
    field_path = \'%s/%s/%s\' % (field.aq_parent.aq_parent.getId(),\n
                               field.aq_parent.getId(),\n
                               field.getId())\n
\n
    c += 1\n
    field_title = field.get_value(\'title\')\n
    field_description = field.get_value(\'description\')\n
    field_note_list = []\n
    if field.meta_type==\'ProxyField\':\n
      if field.is_delegated(\'title\') is True:\n
        field_note_list.append(\'Delegated.\')\n
      elif field.get_tales_expression(\'title\') is not None:\n
        field_note_list.append(\'Tales is used.\')\n
\n
    if len(term_list) == 1 and \\\n
        term_list[0].getTitle() == field_title and \\\n
        term_list[0].getDescription() == field_description:\n
      continue\n
\n
    line = newTempBase(context, \'tmp_glossary_field_%s\' %  c)\n
    line.edit(field_title=field_title,\n
              field_path=field_path,\n
              field_edit_url = \'%s/manage_main\' % field.absolute_url(),\n
              field_note=\' \'.join(field_note_list),\n
              field_description=field_description,\n
              reference=reference,\n
              term_list=term_list,\n
              field_meta_type=field.meta_type\n
              )\n
    line.setUid(field_path)\n
    line_list.append(line)\n
\n
line_list.sort(key=lambda x:x.field_path)\n
return line_list\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>business_field_list, **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>GlossaryModule_getBusinessFieldFieldList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
