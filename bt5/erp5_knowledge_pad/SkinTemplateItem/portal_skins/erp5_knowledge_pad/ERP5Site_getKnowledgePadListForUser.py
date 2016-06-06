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
# in Web Mode we can have a temporary object created based on current language, document by reference\n
real_context_url = context.Base_getRealContext().getRelativeUrl()\n
if mode == \'web_front\':\n
  # Web Site must at least one Pad referenced by context\n
  filter_pad = lambda x: real_context_url in x.getPublicationSectionList() and x.getGroup() is None\n
elif mode == \'web_section\':\n
  # Web Sections, Web Pages can "reuse" tabs\n
  filter_pad = lambda x: real_context_url in x.getPublicationSectionList() or x.getGroup() == default_pad_group\n
elif mode == \'erp5_front\':\n
  # leave only those not having a publication_section as \n
  # this means belonging to root\n
  filter_pad = lambda x: x.getPublicationSection() is None and x.getGroup() is None\n
else:\n
  filter_pad = lambda x: 1\n
\n
results = []\n
def search(container, *states, **kw):\n
  # call getObject() explicitly so that further getter methods do not\n
  # invoke getObject().\n
  for pad in container.searchFolder(validation_state=states,\n
                                    portal_type="Knowledge Pad",\n
                                    sort_on=(("creation_date", "ascending"),),\n
                                    limit=50, **kw):\n
    try:\n
      pad = pad.getObject()\n
      if filter_pad(pad) and pad.getValidationState() in states:\n
        results.append(pad)\n
    except Exception:\n
      pass\n
\n
# first for context\n
search(portal.knowledge_pad_module, \'visible\', \'invisible\', local_roles=\'Owner\')\n
if not results:\n
  request = portal.REQUEST\n
  if request.get(\'is_anonymous_knowledge_pad_used\', 1):\n
    # try to get default pads for anonymous users if allowed on site\n
    search(portal.knowledge_pad_module, \'public\')\n
  if not portal.portal_membership.isAnonymousUser():\n
    # try getting default knowledge pads for user from global site preference\n
    user_pref = context.Base_getActiveGlobalKnowledgePadPreference()\n
    if user_pref is not None:\n
      # use template from user\'s preferences \n
      search(user_pref, \'public\')\n
    if results:\n
      # set a REQUEST variable (this can be used in HTML views)\n
      request.set(\'is_knowledge_pad_template_used\', 1)\n
\n
return results\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>mode=None, default_pad_group=None</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>ERP5Site_getKnowledgePadListForUser</string> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string>Get knowledge pads for user</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
