## Script (Python) "addToCart"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=REQUEST=None,variant=None
##title=Add a product to the shopping cart
##
if REQUEST['quantity'] > 0:
   shopping_cart = context.getShoppingCart()
   prod_obj = context.restrictedTraverse(REQUEST['product_path'])
   del_days = prod_obj.delivery_days
   shopping_cart.addProductToCart(product=REQUEST['product_path']
    , quantity=REQUEST['quantity']
    , delivery_days=del_days
    , variant=variant)
   status_msg = 'Cart+updated'
else:
   status_msg = 'Please+enter+a+quantity'


context.REQUEST.RESPONSE.redirect('shoppingcart_view' + '?portal_status_message=' + status_msg)
