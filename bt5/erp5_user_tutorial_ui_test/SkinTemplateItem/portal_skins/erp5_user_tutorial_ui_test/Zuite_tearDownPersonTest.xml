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
howto_dict = context.Zuite_getHowToInfo()\n
\n
# remove the person of the test if existing\n
person_list = context.portal_catalog(portal_type=\'Person\', \n
                                     title=(howto_dict[\'person_howto_title\'], howto_dict[\'person_howto_title2\'],))\n
if person_list is not None:\n
  portal.person_module.deleteContent([x.getId() for x in person_list])\n
\n
# remove the organisation of the test if existing\n
organisation_list = context.Zuite_checkPortalCatalog(portal_type=\'Organisation\', max_count=1,\n
                                                     title=howto_dict[\'person_howto_organisation_title\'])\n
if organisation_list is not None:\n
  portal.organisation_module.deleteContent(organisation_list[0].getId())\n
\n
return "Clean Ok"\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Zuite_tearDownPersonTest</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
