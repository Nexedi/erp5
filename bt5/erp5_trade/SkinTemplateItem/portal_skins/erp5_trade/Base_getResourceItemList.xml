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
            <value> <string>try:\n
  return container.REQUEST.other[script.id]\n
except KeyError:\n
  pass\n
\n
if not use_list:\n
  return []\n
\n
portal = context.getPortalObject()\n
translateString = portal.Base_translateString\n
\n
if portal_type is None:\n
  portal_type = portal.getPortalResourceTypeList()\n
\n
use_uid = [context.portal_categories.resolveCategory(use).getUid()\n
              for use in use_list]\n
\n
result = [(\'\', \'\')]\n
\n
for resource in context.portal_catalog.searchResults(\n
               portal_type=portal_type,\n
               default_use_uid=use_uid,\n
               validation_state=validation_state,\n
               sort_on=((\'portal_type\', \'asc\'),\n
                        (\'title\', \'asc\'))) :\n
  if show_default_quantity_unit and resource.getQuantityUnit():\n
    result.append(\n
     (\'%s (%s)\' % (resource.getTitle(),\n
                   translateString(resource.getQuantityUnitTitle()),),\n
      resource.getRelativeUrl()))\n
  else:\n
    result.append(\n
     (resource.getTitle(),\n
      resource.getRelativeUrl()))\n
\n
container.REQUEST.other[script.id] = result\n
\n
return result\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>use_list, validation_state=\'validated\', portal_type=None, show_default_quantity_unit=True</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Base_getResourceItemList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
