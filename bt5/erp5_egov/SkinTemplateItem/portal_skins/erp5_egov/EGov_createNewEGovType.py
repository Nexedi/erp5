request=context.REQUEST

if context.portal_membership.isAnonymousUser() and not captcha_ok:
  absolute_url = context.absolute_url()
  new_url = 'captcha/CheckCaptcha/view'
  redirect_url = "%s/%s" % (absolute_url, new_url)
else:
  
  portal_types = context.getPortalObject().portal_types
  # Create a new procedure
  new_procedure = portal_types.newContent(portal_type='EGov Type')
  absolute_url = portal_types.absolute_url()
  new_object_id = new_procedure.getId()

  redirect_url = "%s/%s/%s" % (absolute_url, new_object_id, 'view')

result = request['RESPONSE'].redirect(redirect_url) 
return result
