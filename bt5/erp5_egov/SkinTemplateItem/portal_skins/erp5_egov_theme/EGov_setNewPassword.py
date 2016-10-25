from AccessControl import getSecurityManager
from Products.ERP5Type.Message import translateString

request = context.REQUEST
new_password = request.get("new_password")
former_password = request.get("current_password")
password_confirm = request.get("password_confirm")

user = getSecurityManager().getUser()
person, = context.acl_users.searchUsers(id=user.getUserId(), exact_match=True)
person = context.getPortalObject().restrictedTraverse(person['path'])

if not person.checkPassword(former_password):
  msg = translateString("Current password is wrong.")
elif new_password != password_confirm:
  msg = translateString("Confirmation failed, passwords are not equals.")
  return context.Base_redirect(form_id='EGov_viewChangePasswordForm', keep_items = {'portal_status_message' : msg})
else:
  msg = translateString("Password changed.")
  person.setPassword(new_password)

# clear erp5_content_short cache (see _authenticateCredentials in Products.ERP5Security.ERP5UserManager)
context.portal_caches.clearCache(('erp5_content_short',))
return context.WebSite_logout()
