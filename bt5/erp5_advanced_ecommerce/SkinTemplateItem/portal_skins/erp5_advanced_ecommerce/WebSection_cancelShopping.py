""" """
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
  sale_order.WebSite_executeMethodAsSuperUser('cancel', **{'comment':"Sale Order cancelled because: %s" % reason})
msg = translateString("Your command is cancelled.")
# Display nice message
web_site.Base_redirect('', keep_items={'portal_status_message': msg})
