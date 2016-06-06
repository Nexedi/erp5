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
            <value> <string>prefix = \'field_listbox_term_\'\n
prefix_length = len(prefix)\n
portal_skins = context.portal_skins\n
portal_catalog = context.portal_catalog\n
\n
for i in kw.keys():\n
  if not(i.startswith(prefix) and kw[i]):\n
    continue\n
\n
  term_uid = int(kw[i])\n
  term = portal_catalog(uid=term_uid)[0].getObject()\n
\n
  field_path = i[prefix_length:]\n
  field = portal_skins.restrictedTraverse(field_path)\n
\n
  field.manage_edit_xmlrpc(dict(title=term.getTitle(),\n
                                description=term.getDescription()))\n
\n
\n
portal_status_message = context.Base_translateString(\'Fields updated.\')\n
context.Base_redirect(keep_items={\'portal_status_message\':portal_status_message})\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>**kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>GlossaryModule_updateFieldByTerm</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
