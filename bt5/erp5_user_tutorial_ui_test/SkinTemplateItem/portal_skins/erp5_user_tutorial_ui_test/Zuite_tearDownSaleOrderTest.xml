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
            <value> <string>portal = context.getPortalObject()\n
howto_dict = context.Zuite_getHowToInfo()\n
\n
# remove the currency if it was created by us before\n
currency = context.portal_catalog.getResultValue(portal_type=\'Currency\',\n
                                                 title=howto_dict[\'sale_howto_currency_title\'],\n
                                                 local_roles = \'Owner\')\n
if currency is not None:\n
  context.currency_module.deleteContent(currency.getId())\n
\n
# remove the product of the test if existing\n
product_list = context.Zuite_checkPortalCatalog(portal_type=\'Product\', max_count=1,\n
                                                       title=howto_dict[\'sale_howto_product_title\'])\n
if product_list is not None:\n
  portal.product_module.deleteContent(product_list[0].getId())\n
\n
# remove the organisation of the test if existing\n
organisation_list = context.Zuite_checkPortalCatalog(portal_type=\'Organisation\', max_count=1,\n
                                                            title=howto_dict[\'sale_howto_organisation_title\'])\n
if organisation_list is not None:\n
  portal.organisation_module.deleteContent(organisation_list[0].getId())\n
\n
# remove the second organisation of the test if existing\n
organisation_list2 = context.Zuite_checkPortalCatalog(portal_type=\'Organisation\', max_count=1,\n
                                                            title=howto_dict[\'sale_howto_organisation2_title\'])\n
if organisation_list2 is not None:\n
  portal.organisation_module.deleteContent(organisation_list2[0].getId())\n
\n
# remove the third organisation of the test if existing\n
organisation_list3 = context.Zuite_checkPortalCatalog(portal_type=\'Organisation\', max_count=1,\n
                                                             title=howto_dict[\'sale_howto_organisation3_title\'])\n
if organisation_list3 is not None:\n
  portal.organisation_module.deleteContent(organisation_list3[0].getId())\n
\n
# remove the organisation of the test if existing\n
person_list = context.Zuite_checkPortalCatalog(portal_type=\'Person\', max_count=1,\n
                                                      title=howto_dict[\'sale_howto_person_title\'])\n
if person_list is not None:\n
  portal.person_module.deleteContent(person_list[0].getId())\n
\n
# remove related sale packing list and sale order\n
sale_packing_list_list = context.Zuite_checkPortalCatalog(portal_type=\'Sale Packing List\',\n
                                                                 title=howto_dict[\'sale_howto_product_title\'])\n
if sale_packing_list_list is not None:\n
  for sale_packing_list in sale_packing_list_list:\n
    portal.sale_packing_list_module.deleteContent(sale_packing_list.getId())\n
\n
sale_order_list = context.Zuite_checkPortalCatalog(portal_type=\'Sale Order\', max_count=1,\n
                                                          title=howto_dict[\'sale_howto_product_title\'])\n
if sale_order_list is not None:\n
  for applied_rule in sale_order_list[0].getCausalityRelatedValueList(portal_type=\'Applied Rule\'):\n
    applied_rule.getParentValue().deleteContent(applied_rule.getId())\n
  portal.sale_order_module.deleteContent(sale_order_list[0].getId())\n
\n
sale_invoice_transaction_list = context.Zuite_checkPortalCatalog(portal_type=\'Sale Invoice Transaction\',\n
                                                                       title=howto_dict[\'sale_howto_product_title\'])\n
if sale_invoice_transaction_list is not None:\n
  for sale_invoice_transaction in sale_invoice_transaction_list:\n
    portal.accounting_module.deleteContent(sale_invoice_transaction.getId())\n
\n
payment_transaction_list = context.Zuite_checkPortalCatalog(portal_type=\'Payment Transaction\', max_count=1,\n
                                                                  title=howto_dict[\'sale_howto_payment_title\'])\n
if payment_transaction_list is not None:\n
  for applied_rule in payment_transaction_list[0].getCausalityRelatedValueList(portal_type=\'Applied Rule\'):\n
    applied_rule.getParentValue().deleteContent(applied_rule.getId())\n
  portal.accounting_module.deleteContent(payment_transaction_list[0].getId())\n
\n
# remove created accounting periods\n
accounting_period_list = context.Zuite_checkPortalCatalog(portal_type=\'Accounting Period\', max_count=1,\n
                                                            title=howto_dict[\'optional_new_accounting_period_title\'])\n
if accounting_period_list is not None:\n
  accounting_period_list[0].getParentValue().deleteContent(accounting_period_list[0].getId())\n
\n
\n
pref = getattr(context.portal_preferences, howto_dict[\'howto_preference_id\'], None)\n
if pref is not None:\n
  context.portal_preferences.deleteContent(howto_dict[\'howto_preference_id\'])\n
\n
portal.portal_caches.clearAllCache()\n
\n
return "Clean Ok"\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Zuite_tearDownSaleOrderTest</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
