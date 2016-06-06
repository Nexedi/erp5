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
            <value> <string>"""Create the related person and the related organisation\n
Return related person and related organisation\n
Proxy:\n
Auditor -- to be able to get destination_decision\n
Author -- to be able to call newContent\n
Assignee -- to be able to call setDestinationDecisionValueList"""\n
\n
# check the script is not called from a url\n
if REQUEST is not None:\n
  return None\n
\n
destination_list = context.getDestinationDecisionValueList()\n
update_destination_list = False\n
for destination in destination_list:\n
  try:\n
    create_portal_type.remove(destination.getPortalType())\n
  except ValueError:\n
    #Portal type is not present\n
    pass\n
\n
if "Organisation" in create_portal_type:\n
  #Try to find existant organisation\n
  organisation_title = context.getOrganisationTitle()\n
  module = context.getDefaultModule("Organisation")\n
  organisation_list = module.searchFolder(title=organisation_title)\n
  #be sure we have the same title and no %title%\n
  organisation_list = [x.getObject() for x in organisation_list if x.getObject().getTitle() == organisation_title ]\n
  if organisation_list:\n
    destination_list.append(organisation_list[0]) \n
    create_portal_type.remove("Organisation")\n
    update_destination_list = True\n
\n
for portal_type in create_portal_type:\n
  update_destination_list = True\n
  module = context.getDefaultModule(portal_type)  \n
  obj = module.newContent(portal_type=portal_type)\n
  destination_list.append(obj)\n
\n
if update_destination_list:\n
  context.setDestinationDecisionValueList(destination_list)\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>create_portal_type=["Person"], REQUEST=None</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>CredentialRequest_setDefaultDestinationDecision</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
