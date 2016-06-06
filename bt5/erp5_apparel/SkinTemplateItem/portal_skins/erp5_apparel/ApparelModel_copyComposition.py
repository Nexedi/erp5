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
This script is used to copy composition from a related Apparel Fabric Colour\n
Variation to the current object.\n
\'\'\'\n
\n
cell_id_list = []\n
msg = context.Base_translateString(\'No Composition found.\')\n
colour_range = context.getSpecialiseValue(portal_type=\'Apparel Colour Range\')\n
if colour_range is None:\n
  msg = context.Base_translateString(\'Apparel Colour Range must be defined.\')\n
\n
elif len(colour_range.contentValues(portal_type=\'Apparel Colour Range Variation\')) != 0:\n
  colour_variation = colour_range.contentValues(portal_type=\'Apparel Colour Range Variation\')[0]\n
  variation_line_list = colour_variation.contentValues(portal_type="Apparel Colour Range Variation Line",\n
    sort_on=\'int_index\')\n
  if len(variation_line_list):\n
    # the first one is the most important one\n
    # take composition only from the first one\n
    variation_line = variation_line_list[0]\n
    apparel_fabric_colour_variation = variation_line.getSpecialiseValue(portal_type=\'Apparel Fabric Colour Variation\')\n
    if apparel_fabric_colour_variation is not None:\n
      fabric = apparel_fabric_colour_variation.getParentValue()\n
      composition_list = fabric.getCompositionList()\n
      # get cells\n
      poly_list = fabric.ApparelFabric_asCellRange(matrixbox=1)[0]\n
      context.setCompositionList(composition_list)\n
      #context.setVariationBaseCategoryList([\'composition\',])\n
      context.setCellRange(base_id=\'composition\', *context.ApparelFabric_asCellRange(matrixbox=False))\n
\n
      for cat, title in poly_list:\n
        cell = fabric.getCell(cat, base_id=\'composition\')\n
        if cell is not None:\n
          new_cell = context.newCell(cat, base_id=\'composition\',\n
                                     portal_type=\'Mapped Value\', # XXX\n
                                     quantity=cell.getProperty(\'quantity\'))\n
      if len(poly_list):\n
        msg = context.Base_translateString(\'${count} Compositions created.\',\n
            mapping={\'count\': len(poly_list)})\n
\n
return context.Base_redirect(form_id=form_id,\n
                      keep_items = dict(portal_status_message=msg))\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>form_id=\'view\'</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>ApparelModel_copyComposition</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
