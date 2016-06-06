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
            <value> <string>resource = context.getResourceValue()\n
\n
result = []\n
if include_empty:\n
  result.append((\'\',\'\'))\n
\n
if resource is not None:\n
  portal = context.getPortalObject()\n
  kw = {\'validation_state\': \'!=invalidated\'} if skip_invalidated else {}\n
  result.extend((transformation.title, transformation.relative_url)\n
    for transformation in portal.portal_catalog(\n
      select_list=(\'title\', \'relative_url\'),\n
      portal_type=portal.getPortalTransformationTypeList(),\n
      strict_resource_uid=resource.getUid(),\n
      sort_on=(\'title\', \'relative_url\'),\n
      **kw))\n
\n
return result\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>include_empty=1, skip_invalidated=1</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>OrderLine_getResourceTransformationItemList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
