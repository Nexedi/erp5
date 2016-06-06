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
            <value> <string>"""Copy subscription information to the related organisation"""\n
\n
context.Credential_checkConsistency([\'Organisation\'])\n
organisation = context.getDestinationDecisionValue(portal_type="Organisation")\n
\n
#Mapping\n
organisation_mapping = (\n
    (\'organisation_title\', \'corporate_name\'),\n
    (\'organisation_description\', \'description\',),\n
    (\'organisation_default_telephone_text\', \'default_telephone_text\'),\n
    (\'organisation_default_address_street_address\', \'default_address_street_address\'),\n
    (\'organisation_default_address_zip_code\', \'default_address_zip_code\'),\n
    (\'organisation_default_address_city\', \'default_address_city\'),\n
    (\'organisation_default_address_region\', \'default_address_region\'),\n
    )\n
\n
context.Credential_copyRegistredInformation(organisation, organisation_mapping)\n
\n
#Try to validate\n
try:\n
  organisation.validate()\n
except:\n
  pass\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>CredentialRequest_setRegisteredInformationToOrganisation</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
