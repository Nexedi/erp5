def migrateToERP5Login(self):
  assert self.getPortalType() == 'Person'
  reference = self.getReference()
  if not reference:
    # no user id and no login is required
    return
  if not self.hasUserId() or self.getUserId() == reference:
    self._baseSetUserId(reference)
    self.reindexObject()
  if not self.hasPassword():
    # no login is required, but possibly another Login type object is required if implemented
    return
  if len(self.objectValues(portal_type=self.getPortalObject().getPortalLoginTypeList())):
    # already migrated
    return
  login = self.newContent(
    portal_type='ERP5 Login',
    reference=reference,
  )
  login._setEncodedPassword(self.getPassword())
  login.validate()
  self._setEncodedPassword(None)
