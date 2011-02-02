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
# remove the currency if it was created by us before\n
currency = context.portal_catalog.getResultValue(portal_type=\'Currency\',\n
                                                 title=howto_dict[\'create_event_howto_currency_title\'],\n
                                                 local_roles=\'Owner\',)\n
if currency is not None:\n
  context.currency_module.deleteContent(currency.getId())\n
\n
# remove the person of the test if existing\n
person_list = context.Zuite_checkPortalCatalog(portal_type=\'Person\', max_count=1,\n
                                               title=howto_dict[\'create_event_howto_person_title\'])\n
if person_list is not None:\n
  portal.person_module.deleteContent(person_list[0].getId())\n
\n
# remove the person of the test if existing\n
person_list = context.Zuite_checkPortalCatalog(portal_type=\'Person\', max_count=1,\n
                                               title=howto_dict[\'create_event_howto_person2_title\'])\n
if person_list is not None:\n
  portal.person_module.deleteContent(person_list[0].getId())\n
\n
# remove the organisation of the test if existing\n
organisation_list = context.Zuite_checkPortalCatalog(portal_type=\'Organisation\', max_count=1,\n
                                                     title=howto_dict[\'create_event_howto_organisation_title\'])\n
if organisation_list is not None:\n
  portal.organisation_module.deleteContent(organisation_list[0].getId())\n
\n
# remove the campaign if exist\n
campaign_list = context.Zuite_checkPortalCatalog(portal_type=\'Campaign\', max_count=1,\n
                                                 title=howto_dict[\'create_event_howto_campaign_title\'])\n
if campaign_list is not None:\n
  portal.campaign_module.deleteContent(campaign_list[0].getId())\n
\n
# remove the event if exist\n
event_list = context.Zuite_checkPortalCatalog(portal_type=\'Mail Message\', max_count=999,\n
                                              title=howto_dict[\'create_event_howto_event_title\'])\n
if event_list is not None:\n
  portal.event_module.deleteContent([event.getId() for event in event_list])\n
\n
#remove the preference of the test if existing\n
pref = getattr(context.portal_preferences, howto_dict[\'howto_preference_id\'], None)\n
\n
if pref is not None:\n
  context.portal_preferences.deleteContent(howto_dict[\'howto_preference_id\'])\n
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
            <value> <string>Zuite_tearDownCreateEventTest</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
