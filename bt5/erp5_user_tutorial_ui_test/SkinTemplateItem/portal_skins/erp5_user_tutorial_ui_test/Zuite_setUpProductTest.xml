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
            <value> <string>if clean:\n
  context.Zuite_tearDownProductTest()\n
\n
howto_dict = context.Zuite_getHowToInfo()\n
portal = context.getPortalObject()\n
isTransitionPossible = portal.portal_workflow.isTransitionPossible\n
\n
system_preference = portal.portal_preferences.getActiveSystemPreference()\n
base_category_list = system_preference.getPreferredProductIndividualVariationBaseCategoryList()\n
if \'variation\' not in base_category_list:\n
  base_category_list.append(\'variation\')\n
  system_preference.setPreferredProductIndividualVariationBaseCategoryList(base_category_list)\n
\n
# check if there is already the euro curency on the instance\n
currency = context.portal_catalog.getResultValue(portal_type=\'Currency\',\n
                                                 title=howto_dict[\'product_howto_currency_title\'])\n
if currency is None:\n
  currency = portal.currency_module.newContent(portal_type=\'Currency\',\n
                                               title=howto_dict[\'product_howto_currency_title\'],\n
                                               reference=howto_dict[\'product_howto_currency_tag\'],\n
                                               id=howto_dict[\'product_howto_currency_tag\'],\n
                                               base_unit_quantity=0.01)\n
\n
if isTransitionPossible(currency, \'validate\'):\n
  currency.validate()\n
\n
\n
organisation = portal.organisation_module.newContent(\n
                 portal_type=\'Organisation\',\n
                 title=howto_dict[\'product_howto_organisation_title\'],\n
                 corporate_name=howto_dict[\'product_howto_organisation_title\'])\n
organisation.validate()\n
\n
portal.portal_caches.clearAllCache()\n
\n
return "Init Ok"\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>clean=True</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Zuite_setUpProductTest</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
