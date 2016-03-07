# call remote instance to make the real check for us at server side
if login is not None and password is not None:
  try:
    return context.portal_wizard.callRemoteProxyMethod(
                       'Base_authenticateCredentialsFromExpressInstance', \
                       use_cache = 0, \
                       ignore_exceptions = 0, \
                       **{'login': login,
                          'password': password,
                          'erp5_uid': context.ERP5Site_getExpressInstanceUid()})
  except:
    # if an exception occurs at server side do NOT let user in.
    return 0
return 0
