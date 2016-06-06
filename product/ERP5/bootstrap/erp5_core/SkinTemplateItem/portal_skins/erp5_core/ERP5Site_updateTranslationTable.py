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
            <value> <string>from Products.ERP5Type.Utils import getMessageIdWithContext\n
\n
supported_languages = context.Localizer.get_supported_languages()\n
translated_keys = {} # This dict prevents entering the same key twice\n
\n
sql_catalog = context.portal_catalog.getSQLCatalog(sql_catalog_id)\n
sql_catalog.z0_drop_translation()\n
sql_catalog.z_create_translation()\n
\n
z_catalog_translation_list = sql_catalog.z_catalog_translation_list\n
def catalog_translation_list(object_list):\n
  parameter_dict = {}\n
  for i in object_list:\n
    for property in (\'language\', \'message_context\', \'portal_type\',\n
                     \'original_message\', \'translated_message\'):\n
      parameter_dict.setdefault(property, []).append(i[property])\n
  z_catalog_translation_list(**parameter_dict)\n
\n
# Translate every workflow state in the context of the state variable\n
object_list = []\n
portal_workflow = context.portal_workflow\n
for wf_id, portal_type_list in portal_workflow.getChainDict().items():\n
  wf = getattr(portal_workflow, wf_id, None)\n
  if wf is None:\n
    continue\n
  state_var = wf.variables.getStateVar()\n
  if wf.states:\n
    for state_id, state in wf.states.items():\n
      for lang in supported_languages:\n
        for portal_type in portal_type_list:\n
          key = (lang, portal_type, state_var, state_id)\n
          if not translated_keys.has_key(key):\n
            translated_message = context.Localizer.erp5_ui.gettext(state_id, lang=lang).encode(\'utf-8\')\n
            translated_keys[key] = None # mark as translated\n
            object_list.append(dict(language=lang, message_context=state_var, portal_type=portal_type, original_message=state_id,\n
                               translated_message=translated_message))\n
\n
          # translate state title as well\n
          if state.title != \'\' :\n
            state_var_title = \'%s_title\' % state_var\n
            msg_id = getMessageIdWithContext(state.title, \'state\', wf.id)\n
            translated_message = context.Localizer.erp5_ui.gettext(msg_id, default=\'\', lang=lang).encode(\'utf-8\')\n
            if translated_message == \'\':\n
              msg_id = state.title\n
              translated_message = context.Localizer.erp5_ui.gettext(state.title.decode(\'utf-8\'), lang=lang).encode(\'utf-8\')\n
            key = (lang, portal_type, state_var_title, state_id, msg_id)\n
            if not translated_keys.has_key(key):\n
              translated_keys[key] = None # mark as translated\n
              object_list.append(dict(language=lang, message_context=state_var_title, portal_type=portal_type, original_message=state_id,\n
                                 translated_message=translated_message))\n
if object_list:\n
  catalog_translation_list(object_list)\n
\n
# Translate every portal type in the context of the portal type\n
object_list = []\n
for ptype in context.portal_types.objectValues():\n
  portal_type = ptype.title\n
  if not portal_type: portal_type = ptype.id\n
  for lang in supported_languages:\n
    key = (lang, \'portal_type\', portal_type)\n
    if not translated_keys.has_key(key):\n
      translated_keys[key] = None # mark as translated\n
      object_list.append(dict(language=lang, message_context=\'portal_type\', portal_type=portal_type, original_message=portal_type,\n
                         translated_message=context.Localizer.erp5_ui.gettext(portal_type, lang=lang).encode(\'utf-8\')))\n
if object_list:\n
  catalog_translation_list(object_list)\n
\n
print \'Done\'\n
return printed\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>sql_catalog_id=None</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>ERP5Site_updateTranslationTable</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
