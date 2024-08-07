from six.moves.urllib.parse import urlparse
from six.moves.urllib.parse import parse_qsl

context.REQUEST.RESPONSE.setCookie("loyalty_reward", "disable", path='/')

context.REQUEST.set("loyalty_reward", "disable")

shopping_cart = context.SaleOrder_getShoppingCart()
if shopping_cart is not None:
  context.WebSection_updateShoppingCartTradeCondition(shopping_cart, None, preserve=True)

url = urlparse(context.REQUEST.HTTP_REFERER)
keep_items = dict(parse_qsl(url.query))
keep_items["portal_status_message"]=context.Base_translateString("Your discount was disabled, you can use it in future again.")
return context.Base_redirect(url.path, keep_items=keep_items)
