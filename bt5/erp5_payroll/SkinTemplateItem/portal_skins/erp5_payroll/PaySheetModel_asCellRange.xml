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
            <value> <string>\'\'\'\n
  this script return a list of catorgory Items\n
  It\'s used in the Pay Sheet Model to return all category slices \n
  corresponding to childs of the selection of the base category in the view\n
\'\'\'\n
\n
category_list = []\n
\n
for category in context.getVariationSettingsCategoryList():\n
  category_name = category.replace(\'salary_range/\',\'\',1)\n
  if context.portal_categories.getCategoryValue(category) is None:\n
    raise ValueError, \'no category %s\' % category\n
  else:\n
    if matrixbox:\n
      category_list.extend(context.portal_categories.getCategoryValue(category).getCategoryChildLogicalPathItemList(checked_permission=\'View\', is_right_display=1, base=1)[1:])\n
    else:\n
      cat_list = [cat[0] for cat in\n
          context.portal_categories.salary_range[category_name].getCategoryChildItemList(checked_permission=\'View\', base=1)[1:]]\n
      category_list.append(cat_list)\n
\n
return category_list\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>matrixbox=0, base_id=\'movement\',**kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>PaySheetModel_asCellRange</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
