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
            <value> <string>#if context.getPortalType() == \'Container Line\' :\n
#   category_list = ((\'variation\',),)\n
#context.log(context.getPath(), base_category)\n
if base_category != None and base_category in context.getVariationBaseCategoryList():\n
  variation_list = []\n
  for category_item in context.getVariationCategoryItemList():\n
    category = category_item[1]\n
    title    = category_item[0]\n
    if same_type(title, \'\'):\n
      title = context.Localizer.erp5_ui.gettext(title)\n
    if category.startswith(base_category + \'/\'):\n
      variation_list.append((category, title))\n
  return variation_list\n
\n
base_category_list = ((\'emission_letter\',),(\'variation\',),(\'cash_status\',))\n
variation_category_list = context.getVariationCategoryList()  #(\'emission/letter/c\',\'cash_status/valid\',\'variation/2003\')\n
cash_line_list = []\n
for base_category in base_category_list :\n
  cash_line_list.append([x for x in context.OrderLine_getMatrixItemList(base_category) if x in variation_category_list])\n
#context.log("cash line list", str((cash_line_list, base_category_list, variation_category_list, context.OrderLine_getMatrixItemList(base_category))))\n
return cash_line_list\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>base_category=None, base_id=\'movement\', matrixbox=0,**kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>CashDetail_asCellRange</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
