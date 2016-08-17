from AccessControl import getSecurityManager
from Products.ERP5Type.Message import translateString

portal = context.getPortalObject()
user = getSecurityManager().getUser()
person = context.acl_users.erp5_users.getPersonByReference(user.getId())
for login in person.objectValues(portal_type='ERP5 Login'):
  if login.getReference() == reference and login.getValidationState() == 'validated':
    break
else:
  msg = translateString('You cannot change the password for %r.' % reference)
  return context.Base_redirect(dialog_id, keep_items=dict(portal_status_message=msg))
if not login.checkPassword(current_password):
  msg = translateString("Current password is wrong.")
  return context.Base_redirect(dialog_id, keep_items=dict(portal_status_message=msg))

login.setPassword(new_password)
# clear erp5_content_short cache (see _authenticateCredentials in Products.ERP5Security.ERP5UserManager)
context.portal_caches.clearCache(('erp5_content_short',))
return portal.Base_redirect('logout')
