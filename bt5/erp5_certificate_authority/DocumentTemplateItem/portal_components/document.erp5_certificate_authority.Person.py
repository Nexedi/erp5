from AccessControl import ClassSecurityInfo, Unauthorized, getSecurityManager
from erp5.component.document.erp5_version.Person import Person as ERP5Person
from Products.ERP5Type import Permissions

class Person(ERP5Person):
  security = ClassSecurityInfo()

  def checkCertificateRequest(self):
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

  def _generateCertificate(self):
    certificate_login = self.newContent(
      portal_type="Certificate Login",
    )
    certificate_dict = certificate_login.getCertificate()
    certificate_login.validate()
    return certificate_dict

  security.declarePublic('generateCertificate')
  def generateCertificate(self):
    """Returns new SSL certificate
       This API was kept for backward compatibility"""
    self.checkCertificateRequest()
    return self._generateCertificate()

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
