"""
  Add resource to shopping cart.
"""
request = container.REQUEST
if resource is None:
  resource = context

if form_id is not None:
  from Products.Formulator.Errors import FormValidationError
  form = getattr(context, form_id, None)
  quantity = int(request.get('field_your_buy_quantity'))
  # FIXME:
  # this handling of validation errors should be automatically handled by the 
  # button itself
  try:
    params = form.validate_all_to_request(request)
  except FormValidationError, validation_errors:
    # Pack errors into the request
    field_errors = form.ErrorFields(validation_errors)
    request.set('field_errors', field_errors)
    # Make sure editors are pushed back as values into the REQUEST object
    for f in form.get_fields():
      field_id = f.id
      if request.has_key(field_id):
        value = request.get(field_id)
        if callable(value):
          value(request)
    return form(request)

shopping_cart = context.SaleOrder_getShoppingCart()
shopping_cart_items = context.SaleOrder_getShoppingCartItemList()

## check if we don't have already such a resource in cart
line_found=False
for order_line in shopping_cart_items:
  if order_line.getResource() == resource.getRelativeUrl():
    new_quantity = int(order_line.getQuantity()) + quantity
    if new_quantity <= 0:
      ## remove items with zero quantity
      shopping_cart.manage_delObjects(order_line)
    else:
      order_line.setQuantity(new_quantity)
    line_found=True
    break

if line_found == False:
  ## new Resource so add it to shopping cart
  order_line = shopping_cart.newContent(portal_type='Sale Order Line')
  order_line.setResource(resource.getRelativeUrl())
  order_line.setQuantity(quantity)

if( context.getPortalType() == 'Product'):
  context.Base_redirect('Resource_viewAsShop',
                      keep_items={'portal_status_message':context.Base_translateString("Added to cart.")})
else:
  context.Base_redirect('view',
                      keep_items={'portal_status_message':context.Base_translateString("Added to cart.")})
