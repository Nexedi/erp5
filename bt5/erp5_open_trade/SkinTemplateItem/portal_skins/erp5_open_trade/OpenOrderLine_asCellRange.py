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
            <value> <string encoding="cdata"><![CDATA[

resource = context.getResourceValue()\n
cell_range = []\n
if resource is not None:\n
  base_category_list = resource.getVariationBaseCategoryList(omit_optional_variation=1)\n
\n
  for base_category in base_category_list:\n
    if matrixbox:\n
      # XXX matrixbox is right_display (not as listfield) => invert display and value in item\n
      cell_range.append( map(lambda x: (x[1],x[0]), context.getVariationCategoryItemList(base_category_list=(base_category,), display_id=\'translated_title\' ) ) )\n
    else:\n
      cell_range.append( context.getVariationCategoryList(base_category_list = (base_category,) ) )\n
\n
  cell_range = filter(lambda x: x != [], cell_range )\n
\n
return cell_range\n


]]></string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>matrixbox=False, base_id=\'path\', **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>OpenOrderLine_asCellRange</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
