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
from AccessControl.SecurityManagement import newSecurityManager
from Globals import InitializeClass, DTMLFile, PersistentMapping
from Products.ERP5Type.Core.Folder import Folder
from Products.ERP5Type.Tool.BaseTool import BaseTool
from Products.ERP5Type import Permissions
from Products.ERP5 import _dtmldir
from DateTime import DateTime
import urllib
import socket

from zLOG import LOG, INFO

import re
# minimal IP:Port regexp
NODE_RE = re.compile('^\d+\.\d+\.\d+\.\d+:\d+$')

try:
  from Products.TimerService import getTimerService
except ImportError:
  def getTimerService(self):
    pass

last_tic = time.time()
last_tic_lock = threading.Lock()

class AlarmTool(BaseTool):
  """
    This tool manages alarms.

    It is used as a central managment point for all alarms.

    Inside this tool we have a way to retrieve all reports comings
    from Alarms,...
  """
  id = 'portal_alarms'
  meta_type = 'ERP5 Alarm Tool'
  portal_type = 'Alarm Tool'

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
      alarm_list = [x.getObject() for x in catalog_search \
          if x.getObject().getAlarmDate()<=now]
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
    current_date = DateTime()
    for alarm in self.getAlarmList(to_active=1):
      if alarm is not None:
        user = alarm.getWrappedOwner()
        newSecurityManager(self.REQUEST, user)
        if alarm.isActive() or not alarm.isEnabled():
          # do nothing if already active, or not enabled
          continue
        alarm.activeSense()

  security.declareProtected(Permissions.ManageProperties, 'isSubscribed')
  def isSubscribed(self):
    """ return True, if we are subscribed to TimerService.
    Otherwise return False.
    """
    service = getTimerService(self)
    if not service:
      LOG('AlarmTool', INFO, 'TimerService not available')
      return False

    path = '/'.join(self.getPhysicalPath())
    if path in service.lisSubscriptions():
      return True
    return False

  security.declareProtected(Permissions.ManageProperties, 'subscribe')
  def subscribe(self):
    """
      Subscribe to the global Timer Service.
    """
    service = getTimerService(self)
    if not service:
      LOG('AlarmTool', INFO, 'TimerService not available')
      return
    service.subscribe(self)
    return "Subscribed to Timer Service"

  security.declareProtected(Permissions.ManageProperties, 'unsubscribe')
  def unsubscribe(self):
    """
      Unsubscribe from the global Timer Service.
    """
    service = getTimerService(self)
    if not service:
      LOG('AlarmTool', INFO, 'TimerService not available')
      return
    service.unsubscribe(self)
    return "Usubscribed from Timer Service"

  def manage_beforeDelete(self, item, container):
    self.unsubscribe()
    BaseTool.inheritedAttribute('manage_beforeDelete')(self, item, container)

  def manage_afterAdd(self, item, container):
    self.subscribe()
    BaseTool.inheritedAttribute('manage_afterAdd')(self, item, container)

  security.declarePrivate('process_timer')
  def process_timer(self, interval, tick, prev="", next=""):
    """
      Call tic() every x seconds. x is defined in self.interval
      This method is called by TimerService in the interval given
      in zope.conf. The Default is every 5 seconds.
    """
    # only start when we are the alarmNode or if it's empty
    if (self.alarmNode == self.getCurrentNode()) \
      or not self.alarmNode:
      global last_tic
      last_tic_lock.acquire(1)
      try:
        if tick.timeTime() - last_tic >= self.interval:
          self.tic()
          last_tic = tick.timeTime()
      finally:
        last_tic_lock.release()

  def getCurrentNode(self):
      """ Return current node in form ip:port """
      port = ''
      from asyncore import socket_map
      for k, v in socket_map.items():
          if hasattr(v, 'port'):
              # see Zope/lib/python/App/ApplicationManager.py: def getServers(self)
              type = str(getattr(v, '__class__', 'unknown'))
              if type == 'ZServer.HTTPServer.zhttp_server':
                  port = v.port
                  break
      ip = socket.gethostbyname(socket.gethostname())
      currentNode = '%s:%s' %(ip, port)
      return currentNode
      
  security.declarePublic('getAlarmNode')
  def getAlarmNode(self):
      """ Return the alarmNode """
      return self.alarmNode

  def _isValidNodeName(self, node_name) :
    """Check we have been provided a good node name"""
    return isinstance(node_name, str) and NODE_RE.match(node_name)
      
  security.declarePublic('manage_setAlarmNode')
  def manage_setAlarmNode(self, alarmNode, REQUEST=None):
      """ set the alarm node """   
      if not alarmNode or self._isValidNodeName(alarmNode):
        self.alarmNode = alarmNode
        if REQUEST is not None:
            REQUEST.RESPONSE.redirect(
                REQUEST.URL1 +
                '/manageAlarmNode?manage_tabs_message=' +
                urllib.quote("Distributing Node successfully changed."))
      else :
        if REQUEST is not None:
            REQUEST.RESPONSE.redirect(
                REQUEST.URL1 +
                '/manageAlarmNode?manage_tabs_message=' +
                urllib.quote("Malformed Distributing Node."))

