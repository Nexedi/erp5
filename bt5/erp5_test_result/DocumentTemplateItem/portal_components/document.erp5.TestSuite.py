from six.moves import urllib
import requests

from Products.ERP5Type.XMLObject import XMLObject
from DateTime import DateTime
from AccessControl import ClassSecurityInfo
from Acquisition import aq_base
from Products.ERP5Type import Permissions
from Products.ERP5.mixin.periodicity import PeriodicityMixin

class TestSuite(XMLObject, PeriodicityMixin):

  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  security.declareProtected(Permissions.ModifyPortalContent, 'setPingDate')
  def setPingDate(self):
    """
    Set a new date to now when the node was last alive
    """
    portal = self.getPortalObject()
    portal.portal_task_distribution.getMemcachedDict().set(
       "%s_ping_date" % (self.getRelativeUrl()), DateTime())
    if self.getValidationState() == "invalidated":
      self.validate()

  security.declareProtected(Permissions.AccessContentsInformation, 'getPingDate')
  def getPingDate(self):
    """
    Set a new date to now when the node was last alive
    """
    portal = self.getPortalObject()
    return portal.portal_task_distribution.getMemcachedDict().get(
       "%s_ping_date" % (self.getRelativeUrl()))

  security.declareProtected(
    Permissions.AccessContentsInformation,
    'getSlapOSInstanceParameterSchemaURL')
  def getSlapOSInstanceParameterSchemaURL(self):
    """Return the URL of the schema to use for SlapOS parameters.
    """
    for test_suite_repository in self.contentValues(
        portal_type='Test Suite Repository'):
      git_url = test_suite_repository.getGitUrl()
      if git_url:
        if git_url.endswith('/'):
          git_url = git_url[:-1]
        if git_url.endswith('.git'):
          git_url = git_url[:-4]
        software_json_url = "{git_url}/raw/{branch}/{profile_path}.json".format(
          git_url=git_url,
          branch=test_suite_repository.getBranch(),
          profile_path=test_suite_repository.getProfilePath(),
        )
        try:
          software_json = requests.get(software_json_url, timeout=5).json()
        except ValueError:
          return None
        for software_type in ('RootSoftwareInstance', 'default'):
          if software_type in software_json['software-type']:
            return urllib.parse.urljoin(
              software_json_url,
              software_json['software-type'][software_type]['request'])


  # Compatibility Code to be removed after 06/2018, since all instances using
  # test suites should be migrated at that time. Purpose here was to fix the
  # setting of some properties that were defined with type "lines" instead of "string".
  # This was making the property existence constraint not working properly.
  def _fixPropertyConsistency(self):
    aq_base_self = aq_base(self)
    for property_name in ('additional_bt5_repository_id', 'test_suite'):
      property_value = getattr(aq_base_self, property_name, None)
      if property_value is not None and isinstance(property_value, tuple):
        if len(property_value) > 0:
          property_value = property_value[0]
          setattr(aq_base_self, property_name, property_value)
        else:
          delattr(aq_base_self, property_name)

  def getAdditionalBt5RepositoryId(self, *args, **kw):
    self._fixPropertyConsistency()
    return self._baseGetAdditionalBt5RepositoryId(*args, **kw)

  def getTestSuite(self, *args, **kw):
    self._fixPropertyConsistency()
    return self._baseGetTestSuite(*args, **kw)

  # End of compatibility code