def checkPersonLoginExistenceConsistency(self, fixit=False):
  assert self.getPortalType() == 'Person'
  reference = self.getReference()
  if not reference:
    # no login is required
    return []
  if not self.hasPassword():
    # no login is required, but possibly another Login type object is required if implemented
    return []
  if len(self.objectValues(portal_type=self.getPortalObject().getPortalLoginTypeList())):
    # already migrated
    return []
  if fixit:
    login = self.newContent(
      portal_type='ERP5 Login',
      reference=reference,
    )
    login._setEncodedPassword(self.getPassword())
    login.validate()
  return ['%s has no Login type sub document.' % self.getRelativeUrl()]
