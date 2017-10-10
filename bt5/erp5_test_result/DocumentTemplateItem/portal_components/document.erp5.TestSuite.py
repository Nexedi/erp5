from Products.ERP5Type.XMLObject import XMLObject
from DateTime import DateTime
from zLOG import LOG,INFO,ERROR
from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions
from Products.ERP5.mixin.periodicity import PeriodicityMixin

class TestSuite(XMLObject, PeriodicityMixin):

  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  security.declareProtected(Permissions.AccessContentsInformation, 'isRestartAllowed')
  def isRestartAllowed(self, current_date=None):
    """
    Calculates allowance for restarting periodic test
    """
    allow_restart = False
    if current_date is None:
      current_date = DateTime()
    if not self.isEnabled():
      return allow_restart
    alarm_date = self.getAlarmDate()
    if alarm_date is None or alarm_date <= current_date:
      allow_restart = True
      self.setAlarmDate(self.getNextPeriodicalDate(current_date, alarm_date))
    return allow_restart

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

       
