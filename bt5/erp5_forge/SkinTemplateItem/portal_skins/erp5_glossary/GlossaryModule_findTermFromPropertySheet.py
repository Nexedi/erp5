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

result = context.GlossaryModule_getTermDictListFromPropertySheet(property_sheet_list)\n
\n
if export_tsv:\n
  for i in result:\n
    print \'\\t\'.join(map(lambda x:\'"%s"\'%x, (i[\'reference\'], i[\'language\'],\n
                                            i[\'business_field\'],\n
                                            i[\'title\'], i[\'description\'],\n
                                            i[\'field_path\'])))\n
  return printed\n
else:\n
  portal_catalog = context.portal_catalog\n
  num = 0\n
  for i in result:\n
    item_list = portal_catalog(portal_type=\'Glossary Term\',\n
                               reference=i[\'reference\'], language_id=i[\'language\'],\n
                               business_field_title=i[\'business_field\'],\n
                               validation_state="!=deleted")\n
    if len(item_list)>0:\n
      continue\n
\n
    new_id = context.generateNewId()\n
    context.newContent(id=new_id, portal_type=\'Glossary Term\',\n
                       container=context,\n
                       reference=i[\'reference\'], language=i[\'language\'],\n
                       business_field=i[\'business_field\'],\n
                       title=i[\'title\'], description=i[\'description\'],\n
                       comment=i[\'field_path\'])\n
    num += 1\n
\n
\n
portal_status_message = context.Base_translateString(\'%d terms created.\' % num)\n
context.Base_redirect(keep_items={\'portal_status_message\':portal_status_message})\n


]]></string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>property_sheet_list, export_tsv=False, REQUEST=None, **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>GlossaryModule_findTermFromPropertySheet</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
