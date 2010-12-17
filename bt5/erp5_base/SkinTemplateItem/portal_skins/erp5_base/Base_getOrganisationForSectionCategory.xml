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
            <value> <string>"""Returns the main organisation for a section_category.\n
\n
"""\n
portal = context.getPortalObject()\n
\n
def getOrganisationForSectionCategory(section_category):\n
  section = portal.portal_categories.restrictedTraverse(section_category)\n
\n
  mapping = section.getMappingRelatedValue(portal_type=\'Organisation\',\n
                           checked_permission=\'Access contents information\')\n
  if mapping is not None:\n
    return mapping.getRelativeUrl()\n
  \n
  organisation_list = section.getGroupRelatedValueList(portal_type=\'Organisation\',\n
                              strict_membership=1,\n
                              checked_permission=\'Access contents information\') + \\\n
                      section.getGroupRelatedValueList(portal_type=\'Organisation\',\n
                              checked_permission=\'Access contents information\') \n
\n
  for organisation in organisation_list:\n
    if organisation.getProperty(\'validation_state\', \'unset\') not in (\'deleted\', \'cancelled\'):\n
      return organisation.getRelativeUrl()\n
\n
\n
from Products.ERP5Type.Cache import CachingMethod\n
getOrganisationForSectionCategory = CachingMethod(getOrganisationForSectionCategory,\n
                                                  id=script.getId())\n
organisation_url = getOrganisationForSectionCategory(section_category)\n
if organisation_url:\n
  return portal.restrictedTraverse(organisation_url, None)\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>section_category</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Base_getOrganisationForSectionCategory</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
