REQUEST = context.REQUEST
result, message =  context.getPortalTypesProperties()
ret_url = context.absolute_url() + '/' + REQUEST.get('form_id', 'view')

if REQUEST is not None:
  ret_url = context.absolute_url() + '/' + REQUEST.get('form_id', 'view')
  if not result:
    message = context.Base_translateString("Portal type properties have been updated.")
  REQUEST.RESPONSE.redirect("%s?portal_status_message=%s"% (ret_url, message))
