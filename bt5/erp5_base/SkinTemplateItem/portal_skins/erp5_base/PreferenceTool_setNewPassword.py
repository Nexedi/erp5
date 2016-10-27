from AccessControl import getSecurityManager
from Products.ERP5Type.Message import translateString

login = getSecurityManager().getUser().getLoginValue()
if login is None:
  msg = translateString(
    'You cannot change the password for $reference.',
    mapping={'reference': reference},
  )
elif not login.checkPassword(current_password):
  msg = translateString("Current password is wrong.")
else:
  login.setPassword(new_password)
  # clear erp5_content_short cache (see _authenticateCredentials in Products.ERP5Security.ERP5UserManager)
  context.portal_caches.clearCache(('erp5_content_short',))
  return context.getPortalObject().Base_redirect('logout')
return context.Base_redirect(dialog_id, keep_items={'portal_status_message': msg})
