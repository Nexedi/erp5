portal = context.getPortalObject()
translateString = context.Base_translateString
website = context.getWebSiteValue()

# Call Base_edit
result, result_type = context.Base_edit(form_id, silent_mode=1, field_prefix='your_')

# Return if not appropriate
if result_type != 'edit':
  return result
kw, _ = result
# Set default values
person_group = None
person_function = None
person_site = None
person_role = 'client'

reference = kw.pop('reference')
password = kw.pop('password')
kw.pop('password_confirm', None)

# Check that user doesn't already exists
person_list = [x for x in portal.acl_users.searchUsers(login=reference, exact_match=True) if 'path' in x]
if person_list:
  msg = translateString("This account already exists. Please provide another email address.")
  kw['portal_status_message'] = msg
  context.REQUEST.form.update(kw)
  return getattr(website, form_id)()

# create Person account
person_module = portal.getDefaultModule(portal_type='Person')
person = person_module.newContent(portal_type='Person')
user_id = person.Person_getUserId()
# Create default career
person.newContent(portal_type='Career',
                  id='default_career',
                  group=person_group,
                  function=person_function,
                  role=person_role)
# Create assignment
assignment = person.newContent(portal_type='Assignment',
                               group=person_group,
                               function=person_function,
                               role=person_role, # Required for security based on role
                               site=person_site)
login = person.newContent(portal_type='ERP5 Login',
                          reference=reference,
                          password=password)
login.validate()
assignment.open()

person.validate()
person.manage_setLocalRoles(user_id, ['Auditor'])

person.WebSite_immediateReindex()
login.WebSite_immediateReindex()
person.WebSite_executeMethodAsSuperUser('edit', **kw)



is_shopping_cart = context.REQUEST.get('is_shopping_cart')
if is_shopping_cart is None:
  is_shopping_cart = context.REQUEST.get('field_your_is_shopping_cart')

if is_shopping_cart:
  msg = translateString("Your account was successfully created, now you can proceed to payment.")
else:
  msg = translateString("Your account was successfully created.")

# Set owner local role for cart if needed
shopping_cart = context.SaleOrder_getShoppingCart()
if shopping_cart is not None:
  shopping_cart.manage_setLocalRoles(user_id, ['Owner'])
  portal.portal_sessions[container.REQUEST['session_id']].update(shopping_cart=shopping_cart)

"""
response = context.REQUEST.RESPONSE
response.setHeader("__ac_name", reference)
response.setHeader("__ac_password", password)
"""
came_from = kw.pop('came_from', None)
if came_from:
  from ZTUtils import make_query
  parameter_string = make_query(__ac_name=reference, __ac_password=password,
                                portal_status_message=msg, editable_mode=0)
  return context.REQUEST.RESPONSE.redirect('%s?%s' % (came_from, parameter_string))
return website.Base_redirect('/', keep_items=dict(portal_status_message=msg,
                             __ac_name=reference,  # XXX - Make it generic
                             __ac_password=password, # XXX - Make it generic
                             editable_mode=0))
