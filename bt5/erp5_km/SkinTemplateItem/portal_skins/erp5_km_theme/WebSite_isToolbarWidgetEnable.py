if context.portal_membership.isAnonymousUser():
  return False

choice = context.getLayoutProperty('layout_display_toolbar_widget','display')

if choice == 'display':
  return True

from AccessControl import getSecurityManager
u=getSecurityManager().getUser()

if choice == 'webmaster':
  website = context.getWebSiteValue()
  return 'Assignor' in u.getRolesInContext(website)

if choice == 'context':
  return 'Assignor' in u.getRolesInContext(context)

return False
