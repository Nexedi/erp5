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
            <value> <string>if selection_name is not None:\n
\n
  reference_variation_category_list = context.portal_selections.getSelectionParamsFor(selection_name)[\'reference_variation_category_list\']\n
  from Products.ERP5Type.Document import newTempAmount\n
  tmp_context = newTempAmount(context, "temp_context",\n
                              quantity=1.0,\n
                              variation_category_list=reference_variation_category_list,\n
                              resource=context.getRelativeUrl()) \n
  price_currency = context.REQUEST.get(\'price_currency\', None)\n
   \n
  aal = context.getAggregatedAmountList(tmp_context)\n
  for line in aal:\n
    resource = line.getResourceValue()\n
    sender_value = None\n
    if resource is not None:\n
      sender = line.getResourceValue().getPurchaseSupplyLineSource()\n
    line.setCategoryMembership(\'source\', sender)\n
    line.setCategoryMembership(\'price_currency\', price_currency)\n
  \n
  result = aal.getTotalPrice()\n
  return result\n
\n
\n
else:\n
  return None\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>selection=None, selection_name=None</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Transformation_getTotalPrice</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
