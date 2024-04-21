from Products.ERP5Type.XMLObject import XMLObject
from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions
from Acquisition import aq_base

class TestSuiteRepository(XMLObject):

  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Compatibility Code to be removed after 06/2018, since all instances using
  # test suites should be migrated at that time. Purpose here was to fix the
  # setting of some properties that were defined with type "lines" instead of "string".
  # This was making the property existence constraint not working properly.
  def _fixPropertyConsistency(self):
    aq_base_self = aq_base(self)
    for property_name in ('branch', 'buildout_section_id', 'git_url', 'profile_path'):
      property_value = getattr(aq_base_self, property_name, None)
      if property_value is not None and isinstance(property_value, tuple):
        if len(property_value) > 0:
          property_value = property_value[0]
          setattr(aq_base_self, property_name, property_value)
        else:
          delattr(aq_base_self, property_name)

  def getBranch(self, *args, **kw):
    self._fixPropertyConsistency()
    return self._baseGetBranch(*args, **kw)

  def getBuildoutSectionId(self, *args, **kw):
    self._fixPropertyConsistency()
    return self._baseGetBuildoutSectionId(*args, **kw)

  def getGitUrl(self, *args, **kw):
    self._fixPropertyConsistency()
    return self._baseGetGitUrl(*args, **kw)

  def getProfilePath(self, *args, **kw):
    self._fixPropertyConsistency()
    return self._baseGetProfilePath(*args, **kw)

  # End of compatibility code