##############################################################################
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
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

import ExtensionClass
from AccessControl import ClassSecurityInfo
from Products.CMFCore import CMFCorePermissions
from Acquisition import aq_base

from zLOG import LOG

DEFAULT_ACTIVITY = 'SQLDict'
#DEFAULT_ACTIVITY = 'ZODBDict'
#DEFAULT_ACTIVITY = 'RAMDict'


class ActiveObject(ExtensionClass.Base):

  security = ClassSecurityInfo()

  def activate(self, activity=DEFAULT_ACTIVITY, active_process=None, **kw):
    # activate returns an ActiveWrapper
    # a queue can be provided as well as extra parameters
    # which can be used for example to define deferred tasks
    try:
    #if 1:
      return self.portal_activities.activate(self, activity, active_process, **kw)
    #else:
    except:
      LOG("WARNING CMFActivity:",0, 'could not create activity for %s' % self.getRelativeUrl())
      # If the portal_activities were not created
      # return a passive object
      return self

  security.declareProtected( CMFCorePermissions.ModifyPortalContent, 'hasActivity' )
  def flushActivity(self, invoke=0, **kw):
    # flush all activities related to this object
    #try:
    if 1:
      self.portal_activities.flush(self, invoke=invoke, **kw)
    #except:
    #  # If the portal_activities were not created
    #  # nothing to do
    #  pass

  security.declareProtected( CMFCorePermissions.ModifyPortalContent, 'hasActivity' )
  def recursiveFlushActivity(self, invoke=0, **kw):
    # flush all activities related to this object
    self.flushActivity(invoke=invoke, **kw)
    if hasattr(aq_base(self), 'objectValues'):
      for o in self.objectValues():
        if hasattr(aq_base(self), 'recursiveFlushActivity'):
          o.recursiveFlushActivity(invoke=invoke, **kw)

  security.declareProtected( CMFCorePermissions.View, 'hasActivity' )
  def hasActivity(self, **kw):
    """
      Tells if an object if active
    """
    try:
      return self.portal_activities.hasActivity(self, **kw)
    except:
      # If the portal_activities were not created
      # there can not be any activity
      return 0

  security.declareProtected( CMFCorePermissions.View, 'hasActivity' )
  def getActiveProcess(self):
    return self.portal_activities.getActiveProcess()
