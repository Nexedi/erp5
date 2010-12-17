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
            <value> <string>from Products.ERP5Type.Message import translateString\n
document = state_change_info[\'object\']\n
portal = state_change_info.getPortal()\n
\n
error_message_list = []\n
language_item_list = portal.Base_getContentTranslationLanguageValueAndLabelList()\n
\n
for property_name in document.getTypeInfo().getContentTranslationDomainPropertyNameList():\n
  original_message = document.getProperty(property_name)\n
  for language, language_label in language_item_list:\n
    try:\n
      translation_original_text = document.getPropertyTranslationOriginalText(property_name, language)\n
    except KeyError:\n
      translation_original_text = None\n
    if translation_original_text is not None and translation_original_text!=original_message:\n
      error_message = translateString(\n
        \'property ${property_name} of ${language} is outdated\', mapping={\'property_name\':property_name, \'language\':language_label})\n
      error_message_list.append(error_message)\n
\n
\n
content_translation_state = portal.portal_workflow.getInfoFor(document, \'content_translation_state\')\n
\n
\n
if error_message_list:\n
  if content_translation_state!=\'outdated\':\n
    document.invalidateContentTranslation(error_message=error_message_list)\n
else:\n
  if content_translation_state!=\'latest\':\n
    document.validateContentTranslation()\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>state_change_info</string> </value>
        </item>
        <item>
            <key> <string>_proxy_roles</string> </key>
            <value>
              <tuple>
                <string>Manager</string>
              </tuple>
            </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>checkAndUpdateTranslationStatus</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
