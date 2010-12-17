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
            <value> <string>"""Returns the main organisation for that group.\n
"""\n
\n
if len(context.contentValues(filter=\n
    dict(portal_type=\'Accounting Period\'))) or context.getMapping():\n
  return context\n
\n
def getOrganisationForSectionCategory(section):\n
  mapping = section.getMappingRelatedValue(portal_type=\'Organisation\',\n
                           checked_permission=\'Access contents information\')\n
  if mapping is not None:\n
    return mapping\n
  \n
  organisation_list = section.getGroupRelatedValueList(portal_type=\'Organisation\',\n
                              strict_membership=1,\n
                              checked_permission=\'Access contents information\')\n
\n
  for organisation in organisation_list:\n
    if organisation.getProperty(\'validation_state\', \'unset\') not in (\'deleted\', \'invalidated\'):\n
      return organisation\n
\n
\n
group = context.getGroupValue()\n
if group is None:\n
  return context\n
\n
group_chain = []\n
while group.getPortalType() != \'Base Category\':\n
  group_chain.append(group)\n
  group = group.getParentValue()\n
\n
for group in group_chain:\n
  organisation = getOrganisationForSectionCategory(group)\n
  if organisation is not None and (\n
      len(organisation.contentValues(\n
              filter=dict(portal_type=\'Accounting Period\'))) or \n
      organisation.getMapping()):\n
    return organisation\n
\n
return context\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Organisation_getMappingRelatedOrganisation</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
