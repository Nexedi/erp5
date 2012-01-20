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
            <value> <string># This is the standard version of text content substitution mapping method.\n
# This script returns commonly used keywords, and can be specified in Web Pages\n
# to substitute URLs embedded into the texts.\n
#\n
# Note: Please do not add rarely used ones into this script, because it becomes\n
# just an overhead for most pages. If you need more, it is better to create\n
# your own script instead.\n
\n
website = context.getWebSiteValue()\n
if website is None:\n
  # handle the case when substitution happens on web page module context (i.e. reindex, or mass pre conversion)\n
  # then fall back to ERP5 site as a Web Site\n
  website = context.getPortalObject()\n
  return dict(website_url=website.absolute_url(),\n
              websection_url=website.absolute_url(),\n
              webpage_url=context.absolute_url())\n
else:\n
  websection = context.getWebSectionValue()\n
  return dict(website_url=website.absolute_url(),\n
              websection_url=websection.absolute_url(),\n
              webpage_url=websection.getPermanentURL(context))\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>WebPage_getStandardSubstitutionMappingDict</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
