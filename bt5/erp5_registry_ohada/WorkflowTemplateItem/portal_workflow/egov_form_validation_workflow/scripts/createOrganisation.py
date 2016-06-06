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
            <value> <string>request_eform = state_change[\'object\']\n
portal = request_eform.getPortalObject()\n
organisation_module = portal.organisation_module\n
denomination = request_eform.getTitle()\n
name = request_eform.getName()\n
rccm =request_eform.getReference()\n
address = request_eform.getAddress()\n
place = request_eform.getDefaultAddressCity()\n
\n
ORGANISATION_DATA = ( ( denomination, name, rccm ,address, place),)\n
\n
for login, corporate_name, reference,default_address_street_address, default_address_city in ORGANISATION_DATA:\n
  if login in organisation_module.objectIds():\n
    organisation = organisation_module[login]\n
  else:\n
    organisation = organisation_module.newContent(id=login,\n
                                                  portal_type=\'Organisation\')\n
\n
  organisation.edit(title = login,\n
                    corporate_name = corporate_name,\n
                    reference = reference,\n
                    default_address_street_address = default_address_street_address,\n
                    default_address_city = default_address_city,)\n
\n
organisation.Base_DoWorkflowAction(action_name = \'deposer_dossier_action\',\n
                                   wf_id = \'business_life_cycle_workflow\')\n
\n
return \'Organisations Created.\'\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>state_change</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>createOrganisation</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
