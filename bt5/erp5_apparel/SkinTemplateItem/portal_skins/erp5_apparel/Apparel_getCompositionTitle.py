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
            <value> <string># this script is used to display a small text in the main form corresponding to the composition\n
# it return something like "3.0 % Polyamide, 5.0 % Elasthanne"\n
translateString = context.Base_translateString\n
\n
title_list = []\n
cell_list = []\n
poly_list = context.ApparelFabric_asCellRange(matrixbox=1)[0]\n
for cat, title in poly_list:\n
  cell = context.getCell(cat, base_id=\'composition\')\n
  if cell is not None:\n
    cell_list.append({\'quantity\':cell.getQuantity(), \'title\':translateString(catalog=\'content\', msg=title)})\n
\n
# sort by quantity\n
cell_list.sort(key=lambda x: x[\'quantity\'], reverse=True)\n
\n
for cell in cell_list:\n
    quantity = cell[\'quantity\']\n
    text = \'%s %% %s\' % (quantity*100, cell[\'title\'])\n
    title_list.append(text)\n
final_text = \', \'.join(title_list)\n
return final_text\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Apparel_getCompositionTitle</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
