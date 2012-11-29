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
            <value> <string>"""Returns the list of section_uid for a group section_category.\n
\n
This will only return organisations member of this section category.\n
If \'strict_membership\' is true, then only organisations strictly member\n
of the category will be returned.\n
If no organisations are member of this section category, then [-1] is returned.\n
"""\n
portal = context.getPortalObject()\n
\n
section = portal.portal_categories.restrictedTraverse(section_category)\n
return [x.uid for x in\n
            section.getGroupRelatedValueList(portal_type=\'Organisation\',\n
                                             strict_membership=strict_membership,\n
                                             checked_permission=\'View\')] or [-1]\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>section_category, strict_membership=False</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Base_getSectionUidListForSectionCategory</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
