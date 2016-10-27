"""Use script with Proxy Role Manager to update password of related person. 
Clear 'erp5_content_short' cache too."""

person = context.getDestinationDecisionValue(portal_type="Person")

if context.getPassword():
  login_list = [login for login in person.objectValues(portal_type='ERP5 Login') \
                if login.getValidationState() == 'validated']
  reference = context.getReference()
  if reference:
    for login in login_list:
      if login.getReference() == reference:
        break
    else:
      raise RuntimeError, 'Person %s does not have a validated Login with reference %r' % \
          (person.getRelativeUrl(), reference)
  else: # BBB when login reference is not set in Credential Update document.
    if login_list:
      login = sorted(login_list,
                     key=lambda x:x.getReference() == person.getReference(), reverse=True)[0]
    else:
      raise RuntimeError, 'Person %s does not have a validated Login with reference %r' % \
          (person.getRelativeUrl(), reference)
  login.setEncodedPassword(context.getPassword())
  context.portal_caches.clearCache(('erp5_content_short',))
  return login.getReference()
