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
\n
# Update roles\n
portal_type = portal.searchFolder(title=\'portal_types\')[0]\n
portal_type.searchFolder(title=\'Person\')[0].updateRoleMapping()\n
portal_type.searchFolder(title=\'Product\')[0].updateRoleMapping()\n
portal_type.searchFolder(title=\'Organisation\')[0].updateRoleMapping()\n
portal_type.searchFolder(title=\'Sale Trade Condition\')[0].updateRoleMapping()\n
\n
# Clone users\n
module = context.person_module\n
my_user = module.scalability_user\n
for i in xrange(0,350):\n
  new_user = my_user.Base_createCloneDocument(batch_mode=1)\n
  name = \'scalability_user_%d\' %i\n
  new_user.setId(name)\n
  new_user.setTitle(name)\n
  new_user.setReference(name)\n
  # new_user.setSubordinationValue(some_organisation_document)\n
  new_user.validate()\n
  assignment = new_user.objectValues(portal_type=\'Assignment\')[0]\n
  assignment.open()\n
\n
# Update roles\n
portal_type = portal.searchFolder(title=\'portal_types\')[0]\n
portal_type.searchFolder(title=\'Person\')[0].updateRoleMapping()\n
portal_type.searchFolder(title=\'Product\')[0].updateRoleMapping()\n
portal_type.searchFolder(title=\'Organisation\')[0].updateRoleMapping()\n
portal_type.searchFolder(title=\'Sale Trade Condition\')[0].updateRoleMapping()\n
\n
# Validate rules in portal_rules\n
portal_rules = portal.portal_rules\n
for rule in portal_rules.searchFolder(validation_state = "draft"):\n
  rule.validate()\n
\n
\n
# Return 1, at the end of the script.\n
return 1\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>init_scalability</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
