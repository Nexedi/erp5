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
            <value> <string>request = context.REQUEST\n
apparel_colour_range = context.getSpecialiseValue(portal_type=(\'Apparel Colour Range\',))\n
msg = context.Base_translateString(\'No Apparel Model Colour Variation found.\')\n
\n
if apparel_colour_range is None:\n
  msg = context.Base_translateString(\'Apparel Colour Range must be defined.\')\n
else:\n
  apparel_colour_range_variation_list = map( lambda x: x.getObject(), apparel_colour_range.searchFolder(portal_type=(\'Apparel Colour Range Variation\',)))\n
\n
  apparel_model_colour_variation_list  = context.searchFolder(portal_type=(\'Apparel Model Colour Variation\',))\n
  apparel_model_colour_variation_title_list = map( lambda x: x.getObject().getTitle(), apparel_model_colour_variation_list)\n
\n
  count = 0\n
  for apparel_colour_range_variation in apparel_colour_range_variation_list:\n
    if apparel_colour_range_variation.getTitle() not in apparel_model_colour_variation_title_list:\n
      count += 1\n
      # Use portal activity for creating lot of variation\n
      context.activate(activity=\'SQLQueue\').newContent(\n
        portal_type = \'Apparel Model Colour Variation\',\n
        title = apparel_colour_range_variation.getTitle(),\n
        description = apparel_colour_range_variation.getDescription(),\n
        destination_reference = apparel_colour_range_variation.getDestinationReference()\n
      )\n
\n
  if count != 0:\n
    msg = context.Base_translateString(\'${count} Apparel Colour Range Variations created.\',\n
        mapping={\'count\': count})\n
\n
context.Base_redirect(form_id=form_id,\n
                      keep_items=dict(portal_status_message=msg))\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>form_id=\'view\'</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>ApparelModel_copyApparelColourRangeVariation</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
