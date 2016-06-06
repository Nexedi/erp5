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
            <value> <string>portal = context.getPortalObject()\n
portal_type = \'Person\'\n
module = portal.getDefaultModule(portal_type)\n
\n
sender_list = [entity.getRelativeUrl() for entity\\\n
               in context.Base_getEntityListFromFromHeader(default_email_text or \'\')]\n
\n
if sender_list:\n
  context.setSourceList(sender_list)\n
  message = portal.Base_translateString(\'Sender found from ${person_module_translated_title}.\',\n
                                        mapping={\'person_module_translated_title\': module.getTranslatedTitle()})\n
  return context.Base_redirect(form_id=kw.get(\'form_id\', \'view\'),\n
                               keep_items={\'portal_status_message\': message})\n
\n
\n
person = module.newContent(portal_type=portal_type,\n
                           default_email_text=default_email_text,\n
                           default_telephone_text=default_telephone_text,\n
                           first_name=first_name,\n
                           last_name=last_name)\n
\n
context.setSourceValue(person)\n
\n
message = portal.Base_translateString(\'Sender Person Created.\')\n
return context.Base_redirect(form_id=kw.get(\'form_id\', \'view\'),\n
                             keep_items={\'portal_status_message\': message})\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>default_email_text=None, default_telephone_text=None, first_name=None, last_name=None, **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Event_createSenderPerson</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
