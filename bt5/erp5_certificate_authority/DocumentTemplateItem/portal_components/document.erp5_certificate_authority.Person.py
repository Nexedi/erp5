from AccessControl import ClassSecurityInfo, Unauthorized, getSecurityManager
from erp5.component.document.erp5_version.Person import Person as ERP5Person
from Products.ERP5Type import Permissions

class Person(ERP5Person):
  security = ClassSecurityInfo()

  def _getCertificateLoginDocument(self):
    for _erp5_login in self.objectValues(
          portal_type=["ERP5 Login"]):
      if _erp5_login.getValidationState() == "validated" and \
        _erp5_login.getReference() == self.getUserId():
        # The user already created a Login document as UserId, so
        # So just use this one.
        return _erp5_login

    for _certificate_login in self.objectValues(
         portal_type=["Certificate Login"]):
      if _certificate_login.getValidationState() == "validated":
        return _certificate_login

    certificate_login = self.newContent(
      portal_type="Certificate Login",
      # For now use UserId as easy way.
      reference=self.getUserId()
    )
    certificate_login.validate()
    return certificate_login


  def _checkCertificateRequest(self):
    try:
      self.checkUserCanChangePassword()
    except Unauthorized:
      # in ERP5 user has no SetOwnPassword permission on Person document
      # referring himself, so implement "security" by checking that currently
      # logged in user is trying to get/revoke his own certificate
      user_id = self.getUserId()
      if not user_id:
        raise
      if getSecurityManager().getUser().getId() != user_id:
        raise

  def _getCertificate(self):
    return self.getPortalObject().portal_certificate_authority\
      .getNewCertificate(self._getCertificateLoginDocument().getReference())

  def _revokeCertificate(self):
    return self.getPortalObject().portal_certificate_authority\
      .revokeCertificateByCommonName(self._getCertificateLoginDocument().getReference())

  security.declarePublic('getCertificate')
  def getCertificate(self):
    """Returns new SSL certificate"""
    self._checkCertificateRequest()
    return self._getCertificate()

  security.declarePublic('revokeCertificate')
  def revokeCertificate(self):
    """Revokes existing certificate"""
    self._checkCertificateRequest()
    self._revokeCertificate()

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getTitle')
  def getTitle(self, **kw):
    """
      Returns the title if it exists or a combination of
      first name and last name
    """
    title = ERP5Person.getTitle(self, **kw)
    test_title = title.replace(' ', '')
    if test_title == '':
      return self.getDefaultEmailCoordinateText(test_title)
    else:
      return title
