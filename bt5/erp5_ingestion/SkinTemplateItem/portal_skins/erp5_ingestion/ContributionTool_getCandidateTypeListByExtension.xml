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
  Find by give filename extension which portal_type is the right one.\n
  Use content_type_registry for that. \n
"""\n
from Products.CMFCore.utils import getToolByName\n
\n
registry = getToolByName(context, \'content_type_registry\', None)\n
if registry is None:\n
  return (None, )\n
else:\n
  pt = registry.findTypeName(\'a.%s\' %ext, None, None)\n
  return (pt,)\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>ext</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>ContributionTool_getCandidateTypeListByExtension</string> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string>Find portal be filename extension</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
