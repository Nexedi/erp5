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
            <value> <string>"""\n
  This script will create all knowledge pads user may need in using\n
  ERP5 and respective web sites. This script should be integrated through\n
  an interaction workflow on Assignment so when the first assignment for user is\n
  opened this script will be called and everything will be created.\n
"""\n
portal = context.getPortalObject()\n
\n
# ERP5 front\n
context.ERP5Site_createDefaultKnowledgePadListForUser(default_pad_group=None, \n
                                                      mode=\'erp5_front\', \n
                                                      owner=owner)\n
web_site = None\n
# Customize this to respective needs\n
default_website_id = None\n
if default_website_id is not None:\n
  web_site = getattr(portal.web_site_module, default_website_id, None)\n
\n
if web_site is not None:\n
  # Web front\n
  web_site.ERP5Site_createDefaultKnowledgePadListForUser(default_pad_group=None, \n
                                                         mode=\'web_front\', \n
                                                         owner=owner)\n
  # web section\n
  web_site.ERP5Site_createDefaultKnowledgePadListForUser(default_pad_group=\'default_section_pad\',\n
                                                         mode=\'web_section\', \n
                                                         owner=owner)\n
  # web section content\n
  web_site.ERP5Site_createDefaultKnowledgePadListForUser(default_pad_group=\'default_content_pad\',\n
                                                         mode=\'web_section\', \n
                                                         owner=owner)\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>owner=None</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Base_createKnowledgePadListForUser</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
