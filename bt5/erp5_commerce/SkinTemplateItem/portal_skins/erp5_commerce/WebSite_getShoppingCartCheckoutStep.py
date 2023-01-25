"""
  Return the current step for checkout procedure that will be displayed on Shopping Cart page.
"""
web_site = context.getWebSiteValue()
shopping_cart = web_site.SaleOrder_getShoppingCart()
empty_cart = shopping_cart.SaleOrder_isShoppingCartEmpty()
is_consistent = shopping_cart.SaleOrder_isConsistent()
is_anonymous = context.portal_membership.isAnonymousUser()

if empty_cart:
  return context.Base_translateString('Add a product to your Shopping Cart.')

if not is_consistent:
  return context.Base_translateString('Select a Shipping Service.')

if is_consistent and is_anonymous:
  return context.Base_translateString('Please, you must login to proceed.')

if is_consistent and not is_anonymous:
  return context.Base_translateString('Select your billing address.')

return
