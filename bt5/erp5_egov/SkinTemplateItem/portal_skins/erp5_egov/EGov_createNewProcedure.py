translateString = context.Base_translateString

request=context.REQUEST

if context.portal_membership.isAnonymousUser() and not captcha_ok:
  absolute_url = context.absolute_url()
  new_url = 'captcha/CheckCaptcha/view?portal_type=%s' % new_application_procedure
  redirect_url = "%s/%s" % (absolute_url, new_url)
else:
  portal_type = new_application_procedure
  if portal_type is not None and portal_type != '':
    module = context.getDefaultModule(portal_type=portal_type)
    # Create a new procedure
    new_procedure = module.newContent(portal_type=portal_type)
    absolute_url = context.absolute_url()
    module_id = module.getId()
    new_object_id = new_procedure.getId()
    redirect_url = "%s/%s/%s/%s" % (absolute_url, module_id, new_object_id, 'view')
  else:
    message = translateString("You must choose a procedure")

    redirect_url = "%s?portal_status_message=%s" % (context.absolute_url(), message)
    
result = request['RESPONSE'].redirect(redirect_url) 
return result
