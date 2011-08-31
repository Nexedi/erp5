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
            <value> <string>from Products.ERP5Type.Document import newTempBase\n
portal = context.getPortalObject()\n
getobject = portal.portal_catalog.getobject\n
request = context.REQUEST\n
integration_site = context\n
result = []\n
line_list = context.getCategoryMappingChildValueList()\n
len_line_list = len(line_list)\n
if len_line_list!=0:\n
  for line in line_list:\n
    container = integration_site\n
    parent = line.getParent()\n
    if line.getPortalType() == "Integration Category Mapping" and parent is not None:\n
      container = parent\n
    obj=container.newContent(portal_type=line.getPortalType(),\n
                          id= "%s" % "_".join(line.getRelativeUrl().split("/")[2:]),\n
                          uid="new_%s" % "_".join(line.getRelativeUrl().split("/")[2:]),\n
                          temp_object=1,\n
                          is_indexable=0,)\n
    obj.edit(source_reference=line.getSourceReference(),\n
          destination_reference=line.getDestinationReference())\n
    result.append(obj)\n
return result\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string> **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>IntegrationSite_getFastInputCategoryMappingLineList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
