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
domain_list = []\n
supply_chain_module = context.getPortalObject().supply_chain_module\n
if depth == 0:\n
  category_list = []\n
  for q in context.ProductionOrderModule_getSelectionProductionOrderList():\n
    specialise = q.getSpecialiseValue()\n
    if specialise is not None and specialise not in category_list:\n
      category_list.append(specialise) \n
else:\n
  return domain_list\n
\n
for category in category_list:\n
  domain = parent.generateTempDomain(id = \'sub\' + category.getId() )\n
  domain.edit(title = category.getTitle(),\n
              membership_criterion_base_category = (\'specialise\', ), \n
              membership_criterion_category = (category.getRelativeUrl(),),\n
              domain_generator_method_id = script.id,\n
              uid = category.getUid())\n
                \n
  domain_list.append(domain)\n
\n
return domain_list\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>depth, parent, **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>ProductionOrderModule_generateSpecialiseDomain</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
