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
            <value> <string>from Products.ERP5Form.Report import ReportSection\n
\n
REQUEST = context.REQUEST\n
variation_category_list = REQUEST.get(\'variation_category_list\', [])\n
if len(variation_category_list):\n
  reference_variation_category_list = variation_category_list\n
elif reference_variation_category_list == []:\n
  reference_variation_category_list = context.getVariationCategoryList()\n
\n
result = []\n
\n
#  from Products.ERP5Type.Utils import cartesianProduct\n
# XXX unable to import cartesianProduct, so, I copied the code (Romain)\n
def cartesianProduct(list_of_list):\n
  if len(list_of_list) == 0:\n
    return [[]]\n
  result = []\n
  head = list_of_list[0]\n
  tail = list_of_list[1:]\n
  product = cartesianProduct(tail)\n
  for v in head:\n
    for p in product:\n
      result += [[v] + p]\n
  return result\n
\n
# Separate reference_variation_category_list by base category\n
variation_category_dict = {}\n
for variation_category in reference_variation_category_list:\n
  base_category = variation_category.split(\'/\',1)[0]\n
  if variation_category_dict.has_key( base_category ):\n
    variation_category_dict[base_category].append( variation_category )\n
  else:\n
    variation_category_dict[base_category] = [variation_category]\n
\n
variation_key_list = cartesianProduct( variation_category_dict.values() )\n
        \n
        \n
portal = context.portal_url.getPortalObject()\n
\n
for variation_key in variation_key_list:\n
  params =  { \n
    \'reference_variation_category_list\' : variation_key,\n
  }\n
\n
  result.append(\n
    # Context is report form\n
    ReportSection(path=context.getPhysicalPath(), \n
                  title=\'Resource variation\',   \n
                  level=1,\n
                  form_id=\'Transformation_viewExpanded\',\n
                  selection_name=\'transformation_expanded_selection\',\n
                  selection_params=params,\n
#                  selection_columns="Id",\n
                  listbox_display_mode=\'FlatListMode\'\n
    )             \n
  )\n
\n
return result\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>reference_variation_category_list=[]</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Transformation_getReportSectionList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
