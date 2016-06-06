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
            <value> <string>knowledge_pads = context.ERP5Site_getKnowledgePadListForUser(\n
  mode=mode, default_pad_group=default_pad_group)\n
real_context = context.Base_getRealContext()\n
real_context_url = real_context.getRelativeUrl()\n
\n
visible_pads = [x for x in knowledge_pads\n
  if x.getValidationState() in (\'visible\', \'public\')]\n
\n
# first filter if we have a custom Pad for the context\n
for knowledge_pad in visible_pads:\n
  publication_section_list = knowledge_pad.getPublicationSectionList()\n
  if real_context_url in publication_section_list:\n
    if real_context.getPortalType() == \'Web Site\' and not default_pad_group:\n
      # ERP5 Web Site front gadget\n
      return knowledge_pad, knowledge_pads\n
    if knowledge_pad.getGroup() == default_pad_group:\n
      # some Web Section can have a customized EXPLICILY "sticked" Pad\n
      return knowledge_pad, knowledge_pads\n
  elif not publication_section_list and not default_pad_group:\n
    # ERP5 Site front gadget \n
    return knowledge_pad, knowledge_pads\n
\n
# no customized version found for this context so\n
# try finding pad by group\n
for knowledge_pad in visible_pads:\n
  if knowledge_pad.getGroup() == default_pad_group:\n
    break\n
else:\n
  if create_default_pad and context.Base_isUserAllowedToUseKnowledgePad():\n
    knowledge_pad = context.ERP5Site_createDefaultKnowledgePadListForUser(\n
      default_pad_group=default_pad_group, mode=mode)\n
    knowledge_pads.append(knowledge_pad)\n
  else:\n
    knowledge_pad = None\n
\n
return knowledge_pad, knowledge_pads\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>mode = None, default_pad_group=None, create_default_pad=False</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>ERP5Site_getActiveKnowledgePadForUser</string> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string>Get active knowledge pad for user</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
