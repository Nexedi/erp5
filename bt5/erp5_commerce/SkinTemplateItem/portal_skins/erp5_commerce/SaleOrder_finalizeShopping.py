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
            <key> <string>_Change_Python_Scripts_Permission</string> </key>
            <value>
              <list>
                <string>Manager</string>
              </list>
            </value>
        </item>
        <item>
            <key> <string>_Change_bindings_Permission</string> </key>
            <value>
              <list>
                <string>Manager</string>
              </list>
            </value>
        </item>
        <item>
            <key> <string>_Change_cache_settings_Permission</string> </key>
            <value>
              <list>
                <string>Manager</string>
              </list>
            </value>
        </item>
        <item>
            <key> <string>_Change_permissions_Permission</string> </key>
            <value>
              <list>
                <string>Manager</string>
              </list>
            </value>
        </item>
        <item>
            <key> <string>_Change_proxy_roles_Permission</string> </key>
            <value>
              <list>
                <string>Manager</string>
              </list>
            </value>
        </item>
        <item>
            <key> <string>_Copy_or_Move_Permission</string> </key>
            <value>
              <list>
                <string>Manager</string>
              </list>
            </value>
        </item>
        <item>
            <key> <string>_Delete_objects_Permission</string> </key>
            <value>
              <list>
                <string>Manager</string>
              </list>
            </value>
        </item>
        <item>
            <key> <string>_Manage_WebDAV_Locks_Permission</string> </key>
            <value>
              <list>
                <string>Manager</string>
              </list>
            </value>
        </item>
        <item>
            <key> <string>_Manage_properties_Permission</string> </key>
            <value>
              <list>
                <string>Manager</string>
              </list>
            </value>
        </item>
        <item>
            <key> <string>_Take_ownership_Permission</string> </key>
            <value>
              <list>
                <string>Manager</string>
              </list>
            </value>
        </item>
        <item>
            <key> <string>_Undo_changes_Permission</string> </key>
            <value>
              <list>
                <string>Manager</string>
              </list>
            </value>
        </item>
        <item>
            <key> <string>_View_History_Permission</string> </key>
            <value>
              <list>
                <string>Manager</string>
              </list>
            </value>
        </item>
        <item>
            <key> <string>_View_Permission</string> </key>
            <value>
              <list>
                <string>Manager</string>
              </list>
            </value>
        </item>
        <item>
            <key> <string>_View_management_screens_Permission</string> </key>
            <value>
              <list>
                <string>Manager</string>
              </list>
            </value>
        </item>
        <item>
            <key> <string>_WebDAV_Lock_items_Permission</string> </key>
            <value>
              <list>
                <string>Manager</string>
              </list>
            </value>
        </item>
        <item>
            <key> <string>_WebDAV_Unlock_items_Permission</string> </key>
            <value>
              <list>
                <string>Manager</string>
              </list>
            </value>
        </item>
        <item>
            <key> <string>_WebDAV_access_Permission</string> </key>
            <value>
              <list>
                <string>Manager</string>
              </list>
            </value>
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
            <value> <string>"""\n
  Do whatever is necessary to finalize an order.\n
  This script is called after customer completes shopping.\n
"""\n
from DateTime import DateTime\n
request = context.REQUEST\n
web_site = context.getWebSiteValue()\n
isAnon = context.portal_membership.isAnonymousUser()\n
translateString = context.Base_translateString\n
shopping_cart = context.SaleOrder_getShoppingCart()\n
shopping_cart_item_list = shopping_cart.SaleOrder_getShoppingCartItemList(include_shipping=True)\n
customer = shopping_cart.SaleOrder_getShoppingCartCustomer()\n
buyer = shopping_cart.SaleOrder_getShoppingCartBuyer()\n
\n
if isAnon:\n
  # create first an account for user\n
  msg = translateString("You need to create an account to continue. If you already have please login.")\n
  web_site.Base_redirect(\'login_form\', \\\n
                      keep_items={\'portal_status_message\': msg})\n
  return\n
\n
#Check if payment is sucessfull\n
if buyer is None:\n
  raise ValueError, "Impossible to finalize and order not payed"\n
\n
portal_type = "Sale %s" % shopping_cart.getPortalType()\n
module = context.getDefaultModule(portal_type)\n
sale_order = module.newContent(portal_type=portal_type,\n
                                          destination_value = customer,\n
                                          destination_section_value = customer,\n
                                          destination_decision_value = customer,\n
                                          source_section_value = buyer,\n
                                          source_value = buyer,\n
                                          start_date = DateTime(),\n
                                          received_date = DateTime(),\n
                                          comment = shopping_cart.getComment(),\n
                                          # set order default currency,\n
                                          default_price_currency = web_site.WebSite_getShoppingCartDefaultCurrency().getRelativeUrl(),\n
                                          # set trade condition\n
                                          specialise_value = web_site.SaleOrder_getDefaultTradeCondition()\n
                                          )\n
\n
for order_line in shopping_cart_item_list:\n
  resource = order_line.getResourceValue()\n
  sale_order.newContent(portal_type = order_line.getPortalType(),\n
                        resource = order_line.getResource(),\n
                        aggregate_list = order_line.getAggregateList(),\n
                        quantity = order_line.getQuantity(),\n
                        price = order_line.getPrice(),\n
                        title = resource.getTitle())\n
\n
# order it\n
sale_order.order()\n
\n
# clean up shopping cart\n
context.SaleOrder_getShoppingCart(action=\'reset\')\n
\n
context.Base_redirect(\'SaleOrder_viewThankYouMessage\')\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>SaleOrder_finalizeShopping</string> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string>Finalize order</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
