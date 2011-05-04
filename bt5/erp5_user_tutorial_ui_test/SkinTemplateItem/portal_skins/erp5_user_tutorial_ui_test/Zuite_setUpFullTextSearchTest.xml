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
            <value> <string>if clean:\n
  context.Zuite_tearDownFullTextSearchTest()\n
\n
portal = context.getPortalObject()\n
howto_dict = context.Zuite_getHowToInfo()\n
\n
\n
person = portal.person_module.newContent(portal_type=\'Person\',\n
                                         title=howto_dict[\'full_text_person_title\'],\n
                                         reference=howto_dict[\'full_text_person_reference\'],\n
                                         default_email_text=howto_dict[\'full_text_person_email\'])\n
# create Organisation\n
organisation = portal.organisation_module.newContent(portal_type=\'Organisation\',\n
                                                     title=howto_dict[\'full_text_organisation_title\'],\n
                                                     default_email_text=howto_dict[\'full_text_organisation_email\'])\n
# set organisation\n
person.setCareerSubordinationValue(organisation)\n
\n
# Create Currency\n
portal.currency_module.newContent(portal_type=\'Currency\',\n
                                  title=howto_dict[\'dig_currency_title\'])\n
\n
return "Init Ok"\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>clean=True</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Zuite_setUpFullTextSearchTest</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
