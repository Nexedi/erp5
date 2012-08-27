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
  context.Zuite_tearDownSaleTradeConditionTest()\n
\n
portal = context.getPortalObject()\n
howto_dict = context.Zuite_getHowToInfo()\n
isTransitionPossible = portal.portal_workflow.isTransitionPossible\n
\n
# check if there is already the euro curency on the instance\n
currency = context.portal_catalog.getResultValue(portal_type=\'Currency\',\n
                                                 title=howto_dict[\'sale_howto_currency_title\'])\n
\n
if currency is None:\n
  currency = portal.currency_module.newContent(portal_type=\'Currency\',\n
                                               title=howto_dict[\'sale_howto_currency_title\'],\n
                                               reference=howto_dict[\'sale_howto_currency_tag\'],\n
                                               id=howto_dict[\'sale_howto_currency_tag\'],\n
                                               base_unit_quantity=0.01)\n
\n
if isTransitionPossible(currency, \'validate\'):\n
  currency.validate()\n
\n
my_organisation = portal.organisation_module.newContent(portal_type=\'Organisation\',\n
                                                        title=howto_dict[\'sale_howto_organisation_title\'],\n
                                                        corporate_name=howto_dict[\'sale_howto_organisation_title\'])\n
my_organisation.setRole(\'supplier\')\n
my_organisation.setGroup(\'my_group\')\n
my_organisation.validate()\n
\n
organisation = portal.organisation_module.newContent(portal_type=\'Organisation\',\n
                                                     title=howto_dict[\'sale_howto_organisation2_title\'],\n
                                                     corporate_name=howto_dict[\'sale_howto_organisation2_title\'])\n
organisation.validate()\n
\n
person = portal.person_module.newContent(portal_type=\'Person\',\n
                                         title=howto_dict[\'sale_howto_person_title\'],\n
                                         career_subordination_title=howto_dict[\'sale_howto_organisation_title\'])\n
person.validate()\n
\n
pref = getattr(context.portal_preferences, howto_dict[\'howto_preference_id\'], None)\n
if pref is None:\n
  pref = context.portal_preferences.newContent(portal_type="Preference",\n
                                               id=howto_dict[\'howto_preference_id\'])\n
  pref.setPreferredAccountingTransactionSectionCategory(\'group/my_group\')\n
if isTransitionPossible(pref, \'enable\'):\n
  pref.enable()\n
\n
pref.setPreferredAccountingTransactionSourceSection(my_organisation.getRelativeUrl())\n
\n
# Disabling save form warning\n
# this is bad but needed quickly to disable save form warning \n
pref.setPreferredHtmlStyleUnsavedFormWarning(False)\n
\n
# Clear cache\n
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
            <value> <string>Zuite_setUpSaleTradeConditionTest</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
