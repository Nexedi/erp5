from AccessControl import ClassSecurityInfo, Unauthorized, getSecurityManager
from Products.ERP5.Document.Person import Person as ERP5Person

class Person(ERP5Person):
  security = ClassSecurityInfo()
  security.declarePublic('getCertificate')

  def _checkCertificateRequest(self):
    try:
      self.checkUserCanChangePassword()
    except Unauthorized:
      # in ERP5 user has no SetOwnPassword permission on Person document
      # referring himself, so implement "security" by checking that currently
      # logged in user is trying to get/revoke his own certificate
      user_id = self.Person_getUserId()
      if not user_id:
        raise
      if getSecurityManager().getUser().getId() != user_id:
        raise

  def _getCertificate(self):
    return self.getPortalObject().portal_certificate_authority\
      .getNewCertificate(self.Person_getUserId())

  def _revokeCertificate(self):
    return self.getPortalObject().portal_certificate_authority\
      .revokeCertificateByCommonName(self.Person_getUserId())

  def getCertificate(self):
    """Returns new SSL certificate"""
    self._checkCertificateRequest()
    return self._getCertificate()

  security.declarePublic('revokeCertificate')
  def revokeCertificate(self):
    """Revokes existing certificate"""
    self._checkCertificateRequest()
    self._revokeCertificate()
