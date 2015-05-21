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
            <value> <string>portal =  context.getPortalObject()\n
\n
"""Delete objects we are about to create """\n
for i in range(start, start + num):\n
  if getattr(portal.position_announcement_module, \'announcement_\' + str(i), None) is not None:\n
    portal.position_announcement_module.deleteContent(\'announcement_\' + str(i))\n
  if getattr(portal.position_opportunity_module, \'opportunity_\' + str(i), None) is not None:\n
    portal.position_opportunity_module.deleteContent(\'opportunity_\' + str(i))\n
  if getattr(portal.position_module, \'position_\' + str(i), None) is not None:\n
    portal.position_module.deleteContent(\'position_\' + str(i))\n
\n
"""Create objects with given parameters"""\n
for i in range(start, start + num):\n
  portal.position_announcement_module.newContent(id = \'announcement_\' + str(i), title = \'Super Announcement Title %d\' % i, portal_type=\'Position Announcement\')\n
  portal.position_opportunity_module.newContent(id = \'opportunity_\' + str(i), title = \'Super Opportunity %d\' % i, portal_type=\'Position Opportunity\')\n
  portal.position_module.newContent(id = \'position_\' + str(i), title = \'Super Position %d\' % i, portal_type=\'Position\')\n
\n
return \'Created Successfully.\'\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>start = 0, num = 1</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>testE5gEhr_CreateDataSample</string> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string>Create Objects</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
