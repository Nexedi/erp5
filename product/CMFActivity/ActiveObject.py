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
from ZODB.POSException import ConflictError

from zLOG import LOG

DEFAULT_ACTIVITY = 'SQLDict'

# Processing node are used to store processing state or processing node
DISTRIBUTABLE_STATE = -1
INVOKE_ERROR_STATE = -2
VALIDATE_ERROR_STATE = -3
STOP_STATE = -4
POSITIVE_NODE_STATE = 'Positive Node State' # Special state which allows to select positive nodes

class ActiveObject(ExtensionClass.Base):

  security = ClassSecurityInfo()

  def activate(self, activity=DEFAULT_ACTIVITY, active_process=None, passive_commit=0, **kw):
    """
      Reserved Optional parameters
      
      at_date           --  request execution date for this activate call
      
      after_method_id   --  never validate message if after_method_id
                            is in the list of methods which are
                            going to be executed
    
      after_message_uid --  never validate message if after_message_uid
                            is in the list of messages which are
                            going to be executed
    
      after_path        --  never validate message if after_path
                            is in the list of path which are
                            going to be executed                                                              
      
    """
    activity_tool = getattr(self, 'portal_activities', None)
    if activity_tool is None: return self # Do nothing if no portal_activities
    # activate returns an ActiveWrapper
    # a queue can be provided as well as extra parameters
    # which can be used for example to define deferred tasks
    try:
      return activity_tool.activate(self, activity, active_process, **kw)
    except ConflictError:
      raise
    except:
      LOG("WARNING CMFActivity:",0, 'could not create activity for %s' % self.getRelativeUrl())
      # If the portal_activities were not created
      # return a passive object
      if passive_commit: get_transaction().commit()
      return self

  security.declareProtected( CMFCorePermissions.ModifyPortalContent, 'flushActivity' )
  def flushActivity(self, invoke=0, **kw):
    activity_tool = getattr(self, 'portal_activities', None)
    if activity_tool is None: return # Do nothing if no portal_activities
    # flush all activities related to this object
    #try:
    if 1:
      activity_tool.flush(self, invoke=invoke, **kw)
    #except:
    #  # If the portal_activities were not created
    #  # nothing to do
    #  pass

  security.declareProtected( CMFCorePermissions.ModifyPortalContent, 'recursiveFlushActivity' )
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
    activity_tool = getattr(self, 'portal_activities', None)
    if activity_tool is None: return 0 # Do nothing if no portal_activities
    try:
      return activity_tool.hasActivity(self, **kw)
    except ConflictError:
      raise
    except:
      # If the portal_activities were not created
      # there can not be any activity
      return 0

  security.declareProtected( CMFCorePermissions.View, 'hasErrorActivity' )
  def hasErrorActivity(self, **kw):
    """
      Tells if an object if active
    """
    return self.hasActivity(processing_node = INVOKE_ERROR_STATE)

  security.declareProtected( CMFCorePermissions.View, 'hasInvalidActivity' )
  def hasInvalidActivity(self, **kw):
    """
      Tells if an object if active
    """
    return self.hasActivity(processing_node = VALIDATE_ERROR_STATE)

  security.declareProtected( CMFCorePermissions.View, 'getActiveProcess' )
  def getActiveProcess(self):
    activity_tool = getattr(self, 'portal_activities', None)
    if activity_tool is None: return None # Do nothing if no portal_activities
    return self.portal_activities.getActiveProcess()
