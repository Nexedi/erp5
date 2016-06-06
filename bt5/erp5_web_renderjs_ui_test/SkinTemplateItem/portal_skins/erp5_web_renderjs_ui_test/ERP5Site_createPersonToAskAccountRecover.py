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
            <value> <string>alpha = \'0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ\'\n
new_password = \'\'.join([random.choice(alpha) for i in range(10)])\n
\n
person_module = context.getPortalObject().person_module\n
user_id = "user_a_test"\n
person = getattr(person_module, user_id, None)\n
if person:\n
  if person.getReference() != user_id:\n
    person.setReference(user_id)\n
else:\n
  person = person_module.newContent(portal_type="Person",\n
                                    reference=user_id,\n
                                    id=user_id,\n
                                    password=new_password,\n
                                    default_email_text="userA@example.invalid")\n
  assignment = person.newContent(portal_type=\'Assignment\')\n
  assignment.open()\n
\n
# Make sure always a new password\n
person.setPassword(new_password)\n
return "OK"\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>ERP5Site_createPersonToAskAccountRecover</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
