"""
  Add resource to shopping cart.

  TODO:
  - support generic variations beyond size and variation
    (through introspection of resource) also in
    SaleOrder_viewShoppingCartRenderer and
    SaleOrder_viewShoppingCartWidgetRenderer
  - implement form validation and parameter retrieval using Base_edit
  - Resource_viewAsShop should be select through portal types
"""
from DateTime import DateTime
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
    form.validate_all_to_request(request)
  except FormValidationError as validation_errors:
    # Pack errors into the request
    field_errors = form.ErrorFields(validation_errors)
    request.set('field_errors', field_errors)
    # Make sure editors are pushed back as values into the REQUEST object
    for f in form.get_fields():
      field_id = f.id
      if field_id in request:
        value = request.get(field_id)
        if callable(value):
          value(request)
    return form(request)

session_id = request.get('session_id', None)

if session_id in [None, '']:
  # Rely on cookies information
  session_id = request.cookies.get('session_id', None)

if session_id in [None, '']:
  # first call so generate session_id and send back via cookie
  now = DateTime()
  session_id = context.Base_generateSessionID(max_long=20)
  expire_timeout_days = 90
  request.RESPONSE.setCookie('session_id', session_id,
                             expires=(now + expire_timeout_days).rfc822(), path='/')
  request.set('session_id', session_id)

shopping_cart = context.SaleOrder_getShoppingCart()
shopping_cart_items = context.SaleOrder_getShoppingCartItemList()

# get category like size and variation
category = request.form.get('field_variation_box_your_category', '')
base_category = ''
if category:
  [base_category, category] = category.split('/', 1)
variation = request.form.get('field_variation_box_your_variation', None)
## check if we don't have already such a resource in cart
line_found=False
for order_line in shopping_cart_items:
  if order_line.getResource() == resource.getRelativeUrl():
    if (not variation or order_line.getVariation() == variation) and (not category or getattr(order_line, 'get%s' % base_category.title())() == category):
      line_found = True
      if checkout:
        # We don't update quantities if it is a direct checkout.
        break
      new_quantity = int(order_line.getQuantity()) + quantity
      if new_quantity <= 0:
        ## remove items with zero quantity
        shopping_cart.manage_delObjects(order_line)
      else:
        order_line.setQuantity(new_quantity)
      break

if not line_found:
  ## new Resource so add it to shopping cart
  order_line = shopping_cart.newContent(portal_type='Sale Order Line')
  order_line.setResource(resource.getRelativeUrl())
  order_line.setQuantity(quantity)
  order_line.setBaseContributionList(resource.getBaseContributionList())
  if variation:
    order_line.setVariation(variation)
  if category:
    method_id = getattr(order_line,'set%s' % base_category.title())
    method_id(category)
  order_line.setPrice(context.getPrice(supply_path_type=["Sale Supply Line", "Sale Supply Cell"], context=order_line))
context.WebSection_updateShoppingCartTradeCondition(shopping_cart, None)

context.getPortalObject().portal_sessions[session_id].update(shopping_cart=shopping_cart)

if checkout:
  website = context.getWebSiteValue()
  if website is not None:
    return website.cart.Base_redirect("",
       keep_items={'portal_status_message':context.Base_translateString("Added to cart.")})

keep_items = {
  'portal_status_message':context.Base_translateString("Added to cart.")}
if variation:
  keep_items['variation'] = variation
if( context.getPortalType() == 'Product'):
  context.Base_redirect('Resource_viewAsShop',
                      keep_items=keep_items)
else:
  context.Base_redirect('view',
                      keep_items=keep_items)
