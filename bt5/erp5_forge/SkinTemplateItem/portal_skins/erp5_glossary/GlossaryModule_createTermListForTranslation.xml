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
            <value> <string>catalog = context.portal_catalog\n
glossary_module = context\n
\n
for i in catalog(portal_type=\'Glossary Term\',\n
                 validation_state=\'validated\',\n
                 language_id=\'en\'):\n
\n
  english_term = i.getObject()\n
  \n
  reference = english_term.getReference()\n
  business_field = english_term.getBusinessField()\n
\n
  if catalog.getResultValue(portal_type=\'Glossary Term\',\n
                            causality_uid=english_term.getUid(),\n
                            reference=reference,\n
                            business_field_title=business_field,\n
                            language_id=language) is not None:\n
    continue\n
\n
  new_term = glossary_module.newContent(portal_type=\'Glossary Term\',\n
                                        reference=reference,\n
                                        business_field=business_field,\n
                                        language=language,\n
                                        title=english_term.getTitle(),\n
                                        description=english_term.getDescription(),\n
                                        comment=english_term.getComment(),\n
                                        causality=english_term.getRelativeUrl()\n
                                        )\n
\n
portal_status_message = context.Base_translateString(\'Terms created.\')\n
context.Base_redirect(keep_items={\'portal_status_message\':portal_status_message})\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>language</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>GlossaryModule_createTermListForTranslation</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
