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
portal_type = \'Data Protection Request\'\n
module = portal.getDefaultModule(portal_type)\n
current_user = portal.ERP5Site_getAuthenticatedMemberPersonValue()\n
\n
reference_index = portal.portal_ids.generateNewId(id_group=(\'data_protection_request\'), default=1)\n
reference = \'DPR-%s\' % (reference_index,)\n
data_protection = module.newContent(portal_type=portal_type,\n
                                    contributor_value=current_user,\n
                                    agent_value=context,\n
                                    description=description,\n
                                    reference=reference)\n
data_protection.submit()\n
msg = portal.Base_translateString(\'New data protection request added.\')\n
return context.Base_redirect(form_id, keep_items={\'portal_status_message\': msg}, **kw)\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>description, form_id=\'view\', **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Base_addDataProtectionRequest</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
