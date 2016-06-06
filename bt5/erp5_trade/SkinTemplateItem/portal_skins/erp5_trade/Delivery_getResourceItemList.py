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
            <value> <string>from Products.ERP5Type.Cache import CachingMethod\n
portal = context.getPortalObject()\n
\n
if context.getPortalType() in portal.getPortalSaleTypeList():\n
  use_list = context.portal_preferences.getPreferredSaleUseList()\n
elif context.getPortalType() in portal.getPortalPurchaseTypeList():\n
  use_list = portal.portal_preferences.getPreferredPurchaseUseList()\n
elif context.getPortalType() in portal.getPortalInternalTypeList():\n
  use_list = portal.portal_preferences.getPreferredInternalUseList()\n
else:\n
  use_list = portal.portal_preferences.getPreferredPurchaseUseList()\\\n
             + portal.portal_preferences.getPreferredSaleUseList()\\\n
             + portal.portal_preferences.getPreferredInternalUseList()\n
\n
if not use_list:\n
  return []\n
\n
sql_kw = {}\n
try:\n
  resource_title = cell.resource_title\n
except AttributeError:\n
  resource_title = None\n
try:\n
  reference = cell.default_reference\n
except AttributeError:\n
  reference = None\n
\n
if resource_title not in (None, ""):\n
  sql_kw[\'title\'] = resource_title\n
if reference not in (None, ""):\n
  sql_kw[\'reference\'] = reference\n
\n
\n
if len(sql_kw) == 0:\n
  try:\n
    if cell.getResourceValue() is not None:\n
      sql_kw[\'reference\'] = cell.getResourceReference()\n
      sql_kw[\'title\'] = cell.getResourceTitle()\n
    else:\n
      return [(\'\', \'\')]\n
  except AttributeError:\n
    pass\n
\n
def getResourceItemList(sql_kw):\n
  portal = context.getPortalObject()\n
\n
  result = []\n
  for resource in portal.portal_catalog.searchResults(sort_on=((\'portal_type\', \'asc\'),\n
                                                               (\'title\', \'asc\')),\n
                                                      **sql_kw):\n
    result.append(\n
      (resource.getTitle(),\n
       resource.getRelativeUrl()))\n
\n
  result.append((\'\', \'\'))\n
  return result\n
\n
\n
\n
sql_kw[\'portal_type\'] = portal_type\n
sql_kw[\'validation_state\'] = validation_state\n
sql_kw[\'default_use_uid\'] = [context.portal_categories.resolveCategory(use).getUid()\n
                             for use in use_list]\n
\n
\n
getResourceItemList = CachingMethod(getResourceItemList, ("getResourceItemList", context.aq_parent.getId()),\n
                                          cache_factory="erp5_ui_long")\n
\n
\n
return getResourceItemList(sql_kw)\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>validation_state=\'validated\', portal_type=None, cell=None</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Delivery_getResourceItemList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
