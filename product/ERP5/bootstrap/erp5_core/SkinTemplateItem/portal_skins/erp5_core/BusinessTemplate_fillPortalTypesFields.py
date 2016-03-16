context.guessPortalTypes()

REQUEST = context.REQUEST

if REQUEST is not None:
  ret_url = context.absolute_url() + '/' + REQUEST.get('form_id', 'view')
  REQUEST.RESPONSE.redirect("%s?portal_status_message=Portal+Type+Data+Updated"% ret_url)
