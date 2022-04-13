##############################################################################
#
# Copyright (c) 2004 Nexedi SARL and Contributors. All Rights Reserved.
#                    Sebastien Robin <seb@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

import time
import threading

from AccessControl import ClassSecurityInfo
from AccessControl.SecurityManagement import getSecurityManager, \
        newSecurityManager, setSecurityManager
from Products.CMFActivity.ActivityTool import getCurrentNode
from Products.ERP5Type.Globals import InitializeClass, DTMLFile, PersistentMapping
from Products.ERP5Type.Core.Folder import Folder
from Products.ERP5Type.Tool.BaseTool import BaseTool
from Products.ERP5Type import Permissions
from Products.ERP5 import _dtmldir
from Products.ERP5.mixin.timer_service import TimerServiceMixin
from DateTime import DateTime
from six.moves import urllib

last_tic = time.time()
last_tic_lock = threading.Lock()
_check_upgrade = True

class AlarmTool(TimerServiceMixin, BaseTool):
  """
    This tool manages alarms.

    It is used as a central managment point for all alarms.

    Inside this tool we have a way to retrieve all reports coming
    from Alarms,...
  """
  id = 'portal_alarms'
  meta_type = 'ERP5 Alarm Tool'
  portal_type = 'Alarm Tool'
  title = 'Alarms'

  # Declarative Security
  security = ClassSecurityInfo()

  security.declareProtected( Permissions.ManagePortal, 'manage_overview' )
  manage_overview = DTMLFile( 'explainAlarmTool', _dtmldir )

  security.declareProtected( Permissions.ManagePortal , 'manageAlarmNode' )
  manageAlarmNode = DTMLFile( 'manageAlarmNode', _dtmldir )


  manage_options = ( ( { 'label'   : 'Overview'
                       , 'action'   : 'manage_overview'
                       }
                     , { 'label'   : 'Alarm Node'
                       , 'action'   : 'manageAlarmNode'
                       }
                     ,
                     )
                     + Folder.manage_options
                   )

  _properties = ( {'id': 'interval', 'type': 'int', 'mode': 'w', }, )
  interval = 60 # Default interval for alarms is 60 seconds
  # alarmNode possible values:
  #  ''      Bootstraping. The first node to call process_timer will cause this
  #          value to be set to its node id.
  #  (other) Node id matching this value will be the alarmNode.
  # Those values were chosen for backward compatibility with sites having an
  # alarmNode set to '' but expecting alarms to be executed. Use None to
  # disable alarm processing (see setAlarmNode).
  alarmNode = ''

  # API to manage alarms
  # Aim of this API:
  #-- see all alarms stored everywhere
  #-- defines global alarms
  #-- activate an alarm
  #-- see reports
  #-- see active alarms
  #-- retrieve all alarms

  security.declareProtected(Permissions.ModifyPortalContent, 'getAlarmList')
  def getAlarmList(self, to_active = 0):
    """
      We retrieve thanks to the catalog the full list of alarms
    """
    if to_active:
      now = DateTime()
      catalog_search = self.portal_catalog.unrestrictedSearchResults(
        portal_type = self.getPortalAlarmTypeList(),
        alarm_date={'query':now,'range':'ngt'}
      )
      # check again the alarm date in case the alarm was not yet reindexed
      alarm_list = []
      for x in catalog_search:
        alarm = x.getObject()
        alarm_date = alarm.getAlarmDate()
        if alarm_date is not None and alarm_date <= now:
          alarm_list.append(alarm)
    else:
      catalog_search = self.portal_catalog.unrestrictedSearchResults(
        portal_type = self.getPortalAlarmTypeList()
      )
      alarm_list = [x.getObject() for x in catalog_search]
    return alarm_list

  security.declareProtected(Permissions.ModifyPortalContent, 'tic')
  def tic(self):
    """
      We will look at all alarms and see if they should be activated,
      if so then we will activate them.
    """
    security_manager = getSecurityManager()
    try:
      for alarm in self.getAlarmList(to_active=1):
        if alarm is not None:
          user = alarm.getWrappedOwner()
          newSecurityManager(self.REQUEST, user)
          if alarm.isActive() or not alarm.isEnabled():
            # do nothing if already active, or not enabled
            continue
          if alarm.getProperty('automatic_solve'):
            alarm.solve()
          else:
            alarm.activeSense()
    finally:
      setSecurityManager(security_manager)

  security.declarePrivate('process_timer')
  def process_timer(self, interval, tick, prev="", next=""):
    """
      Call tic() every x seconds. x is defined in self.interval
      This method is called by TimerService in the interval given
      in zope.conf. The Default is every 5 seconds.
    """
    if not last_tic_lock.acquire(0):
      return
    try:
      # make sure our skin is set-up. On CMF 1.5 it's setup by acquisition,
      # but on 2.2 it's by traversal, and our site probably wasn't traversed
      # by the timerserver request, which goes into the Zope Control_Panel
      # calling it a second time is a harmless and cheap no-op.
      # both setupCurrentSkin and REQUEST are acquired from containers.
      self.setupCurrentSkin(self.REQUEST)
      # only start when we are the alarmNode
      alarmNode = self.getAlarmNode()
      current_node = getCurrentNode()
      global _check_upgrade
      if alarmNode == '':
        self.setAlarmNode(current_node)
        alarmNode = current_node
      if alarmNode == current_node:
        global last_tic
        now = tick.timeTime()
        if now - last_tic >= self.interval:
          self.tic()
          last_tic = now
      elif _check_upgrade and self.getServerAddress() == alarmNode:
        # BBB: check (once per run) if our node was alarm_node by address, and
        # migrate it.
        _check_upgrade = False
        self.setAlarmNode(current_node)
    finally:
      last_tic_lock.release()

  security.declarePublic('getAlarmNode')
  def getAlarmNode(self):
      """ Return the alarmNode """
      return self.alarmNode

  security.declareProtected(Permissions.ManageProperties, 'setAlarmNode')
  def setAlarmNode(self, alarm_node):
    """
      When alarm_node evaluates to false, set a None value:
      Its meaning is that alarm processing is disabled.
      This avoids an empty string to make the system re-enter boostrap mode.
    """
    if alarm_node:
      self.alarmNode = alarm_node
    else:
      self.alarmNode = None

  security.declarePublic('getNodeList')
  def getNodeList(self):
    return self.getPortalObject().portal_activities.getNodeList()

  security.declareProtected(Permissions.ManageProperties, 'manage_setAlarmNode')
  def manage_setAlarmNode(self, alarmNode, REQUEST=None):
      """ set the alarm node """
      if not alarmNode or self._isValidNodeName(alarmNode):
        self.setAlarmNode(alarmNode)
        if REQUEST is not None:
            REQUEST.RESPONSE.redirect(
                REQUEST.URL1 +
                '/manageAlarmNode?manage_tabs_message=' +
                urllib.parse.quote("Distributing Node successfully changed."))
      else :
        if REQUEST is not None:
            REQUEST.RESPONSE.redirect(
                REQUEST.URL1 +
                '/manageAlarmNode?manage_tabs_message=' +
                urllib.parse.quote("Malformed Distributing Node."))

