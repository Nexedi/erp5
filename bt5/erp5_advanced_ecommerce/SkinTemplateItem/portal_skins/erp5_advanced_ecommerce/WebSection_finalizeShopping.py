from DateTime import DateTime
web_site = context.getWebSiteValue()
portal = context.getPortalObject()
isAnon = context.portal_membership.isAnonymousUser()
translateString = context.Base_translateString

if isAnon:
  # Create first an account for user
  msg = translateString("You need to login or create an account in order to continue.")
  return web_site.Base_redirect('login_form', \
                      keep_items={'portal_status_message': msg})

shopping_cart = context.SaleOrder_getShoppingCart()
sale_order = portal.portal_catalog.getResultValue(
                               portal_type="Sale Order",
                               reference=shopping_cart.getReference())

if sale_order.getSimulationState() == "draft":
  # Sometimes paypal replies too fast, and order is already ordered already
  # When users returns to the portal.
  sale_order.WebSite_executeMethodAsSuperUser('plan', **{'comment':"User concluded the Sale, waiting PayPal Confirmation."})


for amount in sale_order.getAggregatedAmountList():
  if 'base_amount/loyalty_program/using_point' in amount.getBaseApplicationList():
    user = context.ERP5Site_getAuthenticatedMemberPersonValue()
    loyalty_transaction = context.loyalty_transaction_module.newContent(
      portal_type='Loyalty Transaction',
      destination_section_value=user,
      causality_value=sale_order,
      destination_value=user)
    loyalty_transaction.newContent(
      portal_type='Loyalty Transaction Line',
      quantity=amount.getTotalPrice(),
      resource=amount.getResource())
    loyalty_transaction.deliver()
    break
# clean up shopping cart
context.WebSection_resetShoppingCart()
# Display nice message
if not batch_mode:
  context.Base_redirect('SaleOrder_viewThankYouMessage')
