## Script(Python) "addToCart"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=REQUEST=None,variant=None
##title=Add a product to the shopping cart

shopmanager = context.portal_shop_manager
product = context

cart = shopmanager.getMemberCart()
if not cart:
    home = context.portal_membership.getHomeFolder()
    home.invokeFactory(id='ShoppingCart', type_name='Shopping Cart')
    cart = shopmanager.getMemberCart()
del_days = product.getDeliveryDays()

reqvar = 'quantity'
if REQUEST.has_key(reqvar):
    quantity = REQUEST.get(reqvar)
    title = "%s: %s" % (product.title, product.shortVariation(variant))
    try:
        quantity = int(quantity)
    except:
        quantity = 0
    if quantity > 0:
        cart.addProductToCart(prod_path=product.absolute_url(relative=1)
                                          , prod_title=title
                                          , quantity=quantity
                                          , delivery_days=del_days
                                          , mail_receive=1
                                          , variation_value=product.newVariationValue(variant=variant)
                                   )

status_msg = 'Cart+updated'

context.REQUEST.RESPONSE.redirect(context.local_absolute_url(target=cart) +
                                     '/view?portal_status_message=' + status_msg)
