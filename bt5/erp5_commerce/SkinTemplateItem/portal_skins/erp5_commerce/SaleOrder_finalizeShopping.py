"""
  Do whatever is necessary to finalize an order.
  This script is called after customer completes shopping.
"""
from DateTime import DateTime
request = context.REQUEST
web_site = context.getWebSiteValue()
isAnon = context.portal_membership.isAnonymousUser()
translateString = context.Base_translateString
shopping_cart = context.SaleOrder_getShoppingCart()
shopping_cart_item_list = shopping_cart.SaleOrder_getShoppingCartItemList(include_shipping=True)
customer = shopping_cart.SaleOrder_getShoppingCartCustomer()
buyer = shopping_cart.SaleOrder_getShoppingCartBuyer()

if isAnon:
  # create first an account for user
  msg = translateString("You need to create an account to continue. If you already have please login.")
  web_site.Base_redirect('login_form', \
                      keep_items={'portal_status_message': msg})
  return

#Check if payment is sucessfull
if buyer is None:
  raise ValueError("Impossible to finalize and order not payed")

portal_type = "Sale %s" % shopping_cart.getPortalType()
module = context.getDefaultModule(portal_type)
sale_order = module.newContent(portal_type=portal_type,
                                          destination_value = customer,
                                          destination_section_value = customer,
                                          destination_decision_value = customer,
                                          source_section_value = buyer,
                                          source_value = buyer,
                                          start_date = DateTime(),
                                          received_date = DateTime(),
                                          comment = shopping_cart.getComment(),
                                          # set order default currency,
                                          default_price_currency = web_site.WebSite_getShoppingCartDefaultCurrency().getRelativeUrl(),
                                          # set trade condition
                                          specialise_value = web_site.SaleOrder_getDefaultTradeCondition()
                                          )

for order_line in shopping_cart_item_list:
  resource = order_line.getResourceValue()
  sale_order.newContent(portal_type = order_line.getPortalType(),
                        resource = order_line.getResource(),
                        aggregate_list = order_line.getAggregateList(),
                        quantity = order_line.getQuantity(),
                        price = order_line.getPrice(),
                        title = resource.getTitle())

# order it
sale_order.order()

# clean up shopping cart
context.SaleOrder_getShoppingCart(action='reset')

context.Base_redirect('SaleOrder_viewThankYouMessage')
