# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2004-2011 Nexedi SARL and Contributors. All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly advised to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
##############################################################################

import warnings, six
from AccessControl import ClassSecurityInfo
from Products.ERP5Type.Globals import InitializeClass
from Products.CMFActivity.ActivityTool import ActivityTool
from Products.ERP5Type import Permissions
try:
  from Products.TimerService import getTimerService
except ImportError:
  def getTimerService(self):
    warnings.warn('TimerService not available')


class TimerServiceMixin(object):

  security = ClassSecurityInfo()

  security.declareProtected(Permissions.AccessContentsInformation,
                            'isSubscribed')
  def isSubscribed(self):
    """Return True if we are subscribed to TimerService, otherwise return False
    """
    service = getTimerService(self)
    return service and \
      '/'.join(self.getPhysicalPath()) in service.lisSubscriptions()

  security.declareProtected(Permissions.ManageProperties, 'subscribe')
  def subscribe(self):
    """Subscribe to the global Timer Service"""
    service = getTimerService(self)
    if service:
      service.subscribe(self)
      return "Subscribed to Timer Service"
    return "TimerService not available"

  security.declareProtected(Permissions.ManageProperties, 'unsubscribe')
  def unsubscribe(self):
    """Unsubscribe from the global Timer Service"""
    service = getTimerService(self)
    if service:
      service.unsubscribe(self)
      return "Usubscribed from Timer Service"
    return "TimerService not available"

  security.declarePrivate('manage_beforeDelete')
  def manage_beforeDelete(self, *args, **kw):
    self.unsubscribe()
    super(TimerServiceMixin, self).manage_beforeDelete(*args, **kw)

  security.declarePrivate('manage_afterAdd')
  def manage_afterAdd(self, *args, **kw):
    self.subscribe()
    super(TimerServiceMixin, self).manage_afterAdd(*args, **kw)

  if six.PY2:
    security.declarePublic('getCurrentNode')
    getCurrentNode = ActivityTool.getCurrentNode.__func__
    security.declarePublic('getServerAddress')
    getServerAddress = ActivityTool.getServerAddress.__func__
    _isValidNodeName = ActivityTool._isValidNodeName.__func__
  else:
    # no more unbound in py3, we got the function directly
    security.declarePublic('getCurrentNode')
    getCurrentNode = ActivityTool.getCurrentNode
    security.declarePublic('getServerAddress')
    getServerAddress = ActivityTool.getServerAddress
    _isValidNodeName = ActivityTool._isValidNodeName


InitializeClass(TimerServiceMixin)
