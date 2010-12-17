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
from Products.ERP5Type.Utils import cartesianProduct\n
portal = context.getPortalObject()\n
\n
tracking_parameters = {\n
    \'node_uid\': context.getSourceUid(),\n
    \'resource_uid\': context.getResourceUid(),\n
    \'at_date\': context.getStartDate(),\n
    \'output\': 1,\n
\n
    \'item_catalog_title\': kw.get(\'title\') or \'\',\n
    \'item_catalog_reference\': kw.get(\'reference\') or \'\',\n
    \'item_catalog_portal_type\': kw.get(\'portal_type\') or \'\',\n
    \'item_catalog_validation_state\': kw.get(\'validation_state\') or \'\',\n
}\n
\n
\n
check_variation = bool(context.getVariationCategoryList())\n
acceptable_variation_category_list = \\\n
      cartesianProduct(context.getCellRange(base_id=\'movement\'))\n
\n
result_list = []\n
for tracking_brain in portal.portal_simulation.getCurrentTrackingList(\n
                            **tracking_parameters):\n
  item = tracking_brain.getObject()\n
  \n
  # XXX can this be done in SQL ?\n
  # it could, by computing all variation texts, but I don\'t think this is\n
  # really necessary.\n
  if check_variation and \\\n
      item.Item_getVariationCategoryList(at_date=context.getStartDate())\\\n
      not in acceptable_variation_category_list:\n
    continue\n
  \n
  result_list.append(item)\n
\n
return result_list\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>*args, **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>DeliveryLine_getSelectableItemList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
