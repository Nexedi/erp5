## Script(Python) "update_cart"
##parameters=REQUEST=None
##title=Update the shopping cart

if context.meta_type == 'MMM Shop Shopping Cart':
   if REQUEST.has_key('emptyCart'):
      context.clearCart()
      status_msg = 'The+cart+is+empty !'
      return_page =  'cart'
   elif REQUEST.has_key('checkOut'):
      status_msg = 'BLA'
      return_page = 'checkout'
   else:
      status_msg = 'No+action+selected'
      return_page =  'cart'
else:
   status_msg = 'Update+script+called+in+the+wrong+context'
   return_page =  'cart'

if return_page == 'cart':
   context.REQUEST.RESPONSE.redirect(context.local_absolute_url() + '/shoppingcart_view?portal_status_message=' + status_msg)
else:
   context.REQUEST.RESPONSE.redirect(context.local_absolute_url() + '/checkoutPage')
