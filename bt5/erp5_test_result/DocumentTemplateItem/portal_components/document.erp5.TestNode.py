from Products.ERP5Type.XMLObject import XMLObject
from DateTime import DateTime
from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions

class TestNode(XMLObject):

  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  @security.protected(Permissions.ModifyPortalContent)
  def setPingDate(self):
    """
    Set a new date to now when the node was last alive
    """
    portal = self.getPortalObject()
    portal.portal_task_distribution.getMemcachedDict().set(
       "%s_ping_date" % (self.getRelativeUrl()), DateTime())
    if self.getValidationState() == "invalidated":
      self.validate()

  @security.protected(Permissions.AccessContentsInformation)
  def getPingDate(self):
    """
    Set a new date to now when the node was last alive
    """
    portal = self.getPortalObject()
    return portal.portal_task_distribution.getMemcachedDict().get(
       "%s_ping_date" % (self.getRelativeUrl()))


