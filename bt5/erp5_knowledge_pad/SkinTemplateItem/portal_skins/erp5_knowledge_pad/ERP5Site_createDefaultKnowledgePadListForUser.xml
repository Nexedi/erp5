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
            <value> <string>knowledge_pad = None\n
portal = context.getPortalObject()\n
system_pref = context.portal_preferences.getActiveSystemPreference()\n
user_pref = context.Base_getActiveGlobalKnowledgePadPreference()\n
\n
is_web_mode = mode in (\'web_front\', \'web_section\',)\n
if not is_web_mode:\n
  # leave only those not having a publication_section\n
  filter_pad = lambda x: x.getPublicationSection() is None and x.getGroup() is None\n
elif default_pad_group:\n
  filter_pad = lambda x: x.getGroup() == default_pad_group\n
else:\n
  # find from preferences for the same context(site, section, page)\n
  filter_pad = lambda x: context in x.getPublicationSectionValueList()\n
\n
# try to find template KnowledgePad from System Preference (and user Preference\n
# for backward compatibility only).\n
for pref in (system_pref, user_pref):\n
  if pref is not None:\n
    # use template from preferences\n
    for pref_pad in pref.objectValues(portal_type=\'Knowledge Pad\'):\n
      if filter_pad(pref_pad):\n
        break\n
    else:\n
      continue\n
    cp = pref.manage_copyObjects(ids=[pref_pad.getId()])\n
    new_id = context.knowledge_pad_module.manage_pasteObjects(\n
                                   cb_copy_data=cp)[0][\'new_id\']\n
    knowledge_pad = context.knowledge_pad_module[new_id]\n
    knowledge_pad.makeTemplateInstance()\n
    # set each contaned box\'s state manually to visible\n
    # by default their state as well pads would be invisible (default state)\n
    # pad\'s visibility is fixed in ERP5Site_toggleActiveKnowledgePad()\n
    for box in knowledge_pad.contentValues(portal_type=\'Knowledge Box\'):\n
      box.visible()\n
    break\n
else:\n
  # created empty one because no template found\n
  knowledge_pad = context.knowledge_pad_module.newContent(\n
                            portal_type = \'Knowledge Pad\',\n
                            title = context.Base_translateString(\'Tab 1\'))\n
if is_web_mode:\n
  # in Web Mode we can have a temporary Web Site objects created based on current language\n
  real_context = context.Base_getRealContext()\n
  if real_context.getPortalType() == \'Web Site\' and not default_pad_group:\n
    # script is called within Front Page Gadgets view\n
    knowledge_pad.setPublicationSectionValue(real_context)\n
\n
  # create a default pad for user belonging to respective pad group\n
  # this pad will be available globally for other contexes using the same\n
  # layout definition\n
  knowledge_pad.setGroup(default_pad_group)\n
\n
knowledge_pad.visible()\n
# set owner\n
if owner is not None:\n
  current_user = context.portal_membership.getAuthenticatedMember()\n
  knowledge_pad.manage_setLocalRoles(userid=owner, roles=[\'Owner\'])\n
  knowledge_pad.manage_delLocalRoles([str(current_user)])\n
  knowledge_pad.reindexObject()\n
\n
# set default gadgets\n
context.ERP5Site_createDefaultKnowledgeBox(knowledge_pad)\n
\n
# Calling immediateReindexObject explicitly is a coding crime.\n
# But it\'s safe for newly created objects and this script should\n
# be called rarely enough to not cause any performance issue.\n
# Any other solution would be more complicated.\n
# See also ERP5Site_addNewKnowledgePad\n
knowledge_pad.immediateReindexObject()\n
\n
if REQUEST is None:\n
  return knowledge_pad\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>default_pad_group=None, mode=None, owner=None, REQUEST=None</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>ERP5Site_createDefaultKnowledgePadListForUser</string> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string>Create default tabs for user</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
