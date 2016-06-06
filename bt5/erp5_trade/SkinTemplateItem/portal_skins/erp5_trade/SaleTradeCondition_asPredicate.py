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
            <value> <string>if context.getValidationState() in (\'invalidated\', \'deleted\'):\n
  # return a predicate that will never apply\n
  return context.generatePredicate(criterion_property_list=(\'uid\',))\n
\n
category_list = [\n
  \'source\', \'source_section\',\n
  \'destination\', \'destination_section\',\n
]\n
criterion_list = []\n
\n
for category in category_list:\n
  if context.getPropertyList(category):\n
    criterion_list.append(category)\n
\n
date_context=context.asContext(\n
  start_date_range_min=context.getEffectiveDate(),\n
  start_date_range_max=context.getExpirationDate(),\n
)\n
\n
return date_context.generatePredicate(multimembership_criterion_base_category_list=criterion_list,\n
                                                      criterion_property_list=(\'start_date\',))\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>*args,**kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>SaleTradeCondition_asPredicate</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
