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
def get_term_list(reference):\n
  reference = reference.rsplit(\' Module\', 1)[0]\n
  term_list = portal_catalog(portal_type=\'Glossary Term\',\n
                             validation_state=\'validated\',\n
                             language_id=\'en\',\n
                             reference=reference)\n
  return [i.getObject() for i in term_list]\n
\n
line_list = []\n
c = 0\n
portal_type_list = context.GlossaryModule_getAvailablePortalTypeList()\n
for reference in portal_type_list:\n
  portal_type = context.getPortalObject().portal_types[reference]\n
  term_list = get_term_list(reference)\n
  #if not term_list:\n
  #  continue\n
\n
  c += 1\n
  field_description = portal_type.description\n
  if len(term_list) == 1 and \\\n
     term_list[0].getDescription() == field_description:\n
   continue\n
\n
  line = newTempBase(context, \'tmp_glossary_field_%s\' %  c)\n
  line.edit(field_path=reference,\n
            field_edit_url = \'%s/manage_main\' % portal_type.absolute_url(),\n
            field_description=field_description,\n
            reference=reference,\n
            term_list=term_list,\n
            )\n
  line.setUid(reference)\n
  line_list.append(line)\n
\n
line_list.sort(key=lambda x:x.field_path)\n
return line_list\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>**kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>GlossaryModule_getBusinessFieldPortalTypeList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
