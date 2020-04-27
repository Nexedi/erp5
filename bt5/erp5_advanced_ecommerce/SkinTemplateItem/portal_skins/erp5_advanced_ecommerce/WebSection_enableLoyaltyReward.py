context.REQUEST.RESPONSE.expireCookie("loyalty_reward")

context.REQUEST.set("loyalty_reward", "enable")


shopping_cart = context.SaleOrder_getShoppingCart()
if shopping_cart is not None:
  context.WebSection_updateShoppingCartTradeCondition(shopping_cart, None, preserve=True)

portal_status_message = context.Base_translateString("Your discount was enabled. Make an Order to see your discounts.")
form_id = context.REQUEST.get("form_id", "")
return context.Base_redirect(form_id, keep_items={"portal_status_message": portal_status_message})
