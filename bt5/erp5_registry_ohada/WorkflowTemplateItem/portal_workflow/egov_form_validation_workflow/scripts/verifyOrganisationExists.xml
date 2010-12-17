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
            <value> <string>from Products.DCWorkflow.DCWorkflow import ValidationFailed\n
# Make a constraint, it is easier\n
request_eform = state_change[\'object\']\n
portal = request_eform.getPortalObject()\n
organisation_module = portal.organisation_module\n
person_module = portal.person_module\n
date = request_eform.getDate()\n
if request_eform.getPortalType() == \'P2\':\n
  organisation_list = portal.portal_catalog(parent_uid = portal.organisation_module.getUid(),\n
                                            corporate_registration_code = \\\n
                                    request_eform.getEstablishmentModification() \\\n
                                    and request_eform.getEstablishmentCorporateRegistrationCode()\\\n
                                    or request_eform.getCompanyCorporateRegistrationCode(),\n
                                            ignore_empty_string = 0)\n
  if not len(organisation_list):\n
    raise ValidationFailed, \'Organisation was not found for this person\'\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>state_change</string> </value>
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
            <value> <string>verifyOrganisationExists</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
