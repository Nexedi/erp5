def migrateToERP5Login(self):
  assert self.getPortalType() == 'Person'
  login_portal_type = 'ERP5 Login'
  reference = self.getReference()
  if not reference:
    # no user id and no login is required
    return
  if not (self.hasUserId() or self.getUserId() == reference):
    self.setUserId(reference)

  if reference.startswith("go_"):
    login_portal_type = "Google Login"
    reference = self.getDefaultEmailText()
  elif reference.startswith("fb_"):
    login_portal_type = "Facebook Login"
    reference = reference[len("fb_"):]
  else:
    if not self.hasPassword():
      # no login is required, but possibly another Login type object is required if implemented
      return
  if len(self.objectValues(portal_type=login_portal_type)):
    # already migrated
    return
  login = self.newContent(
    portal_type=login_portal_type,
    reference=reference,
  )
  if login_portal_type == "ERP5 Login":
    login._setEncodedPassword(self.getPassword())
    self._setEncodedPassword(None)

  login.validate()
