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
from Acquisition import aq_base
from ZODB.POSException import ConflictError
from Products.CMFCore.utils import getToolByName
from Products.ERP5Type.TransactionalVariable import getTransactionalVariable
from ActivityRuntimeEnvironment import getActivityRuntimeEnvironment

try:
  from Products.CMFCore import permissions
except ImportError:
  from Products.CMFCore import CMFCorePermissions as permissions

from zLOG import LOG, WARNING
import sys

DEFAULT_ACTIVITY = 'SQLDict'

# Processing node are used to store processing state or processing node
DISTRIBUTABLE_STATE = -1
INVOKE_ERROR_STATE = -2
VALIDATE_ERROR_STATE = -3
STOP_STATE = -4
# Special state which allows to select positive nodes
POSITIVE_NODE_STATE = 'Positive Node State'

class ActiveObject(ExtensionClass.Base):
  """Active Object Mixin Class.

  Active object are objects whose methods are lazilly evaluated in the
  Activity Queue. To use an active object, you just have to call the
  method on the wrapper returned by the `activate` method like this:

  >>> obj.activate().aMethod()

  This will defer the call to obj.aMethod() 
  """

  security = ClassSecurityInfo()

  def activate(self, activity=DEFAULT_ACTIVITY, active_process=None,
               passive_commit=0, activate_kw=None, **kw):
    """Returns an active wrapper for this object.

      Reserved Optional parameters:

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

      after_path_and_method_id
                        -- never validate message if a message for
                           method_id on path is in the queue.

      tag               -- add a tag to a message

      after_tag         -- never validate message if there is a message
                           tagged with this tag.

    """
    # Get activate values from activate_kw, then default_activate_parameter
    # transactional variable only if they are not set directly as arguments
    # to activate()
    if activate_kw is not None:
      for k, v in activate_kw.iteritems():
        if k not in kw:
          kw[k] = v

    # Get default parameters from a transactional variable.
    tv = getTransactionalVariable(self)
    key = ('default_activate_parameter', id(aq_base(self)))
    try:
      for k, v in tv[key].iteritems():
        if k not in kw:
          kw[k] = v
    except KeyError:
      pass

    if kw.get('group_id', '') is None:
      raise ValueError, "Cannot defined a group_id with value None"
    elif kw.get('group_method_id') is None and kw.get('group_id') is not None:
      raise ValueError, "Cannot defined a group_id without group_method_id"

    portal = self.getPortalObject()
    if isinstance(active_process, basestring):
      active_process = portal.unrestrictedTraverse(active_process)

    activity_tool = getattr(portal, 'portal_activities', None)
    if activity_tool is None: return self # Do nothing if no portal_activities
    # activate returns an ActiveWrapper
    # a queue can be provided as well as extra parameters
    # which can be used for example to define deferred tasks
    return activity_tool.activateObject(self, activity, active_process, **kw)

  security.declareProtected( permissions.ModifyPortalContent, 'flushActivity' )
  def flushActivity(self, invoke=0, **kw):
    activity_tool = getToolByName(self, 'portal_activities', None)
    if activity_tool is None: return # Do nothing if no portal_activities
    # flush all activities related to this object
    activity_tool.flush(self, invoke=invoke, **kw)

  security.declareProtected( permissions.ModifyPortalContent,
                             'recursiveFlushActivity' )
  def recursiveFlushActivity(self, invoke=0, **kw):
    # flush all activities related to this object
    self.flushActivity(invoke=invoke, **kw)
    if getattr(aq_base(self), 'objectValues', None) is not None:
      for o in self.objectValues():
        if getattr(aq_base(o), 'recursiveFlushActivity', None) is not None:
          o.recursiveFlushActivity(invoke=invoke, **kw)

  security.declareProtected( permissions.View, 'hasActivity' )
  def hasActivity(self, **kw):
    """Tells if there is pending activities for this object.
    """
    activity_tool = getToolByName(self, 'portal_activities', None)
    if activity_tool is None:
      return 0 # Do nothing if no portal_activities
    return activity_tool.hasActivity(self, **kw)

  security.declareProtected( permissions.View, 'hasErrorActivity' )
  def hasErrorActivity(self, **kw):
    """Tells if there is failed activities for this object.
    """
    return self.hasActivity(processing_node = INVOKE_ERROR_STATE)

  security.declareProtected( permissions.View, 'hasInvalidActivity' )
  def hasInvalidActivity(self, **kw):
    """Tells if there is invalied activities for this object.
    """
    return self.hasActivity(processing_node = VALIDATE_ERROR_STATE)

  security.declareProtected( permissions.View, 'getActiveProcess' )
  def getActiveProcess(self):
    activity_tool = getToolByName(self, 'portal_activities', None)
    if activity_tool is None: return None # Do nothing if no portal_activities
    return activity_tool.getActiveProcess()

  security.declareProtected( permissions.ModifyPortalContent, 'setDefaultActivateParameters' )
  def setDefaultActivateParameters(self, **kw):
    # This method sets the default keyword parameters to activate. This is useful
    # when you need to specify special parameters implicitly (e.g. to reindexObject).
    tv = getTransactionalVariable(self)
    key = ('default_activate_parameter', id(aq_base(self)))
    tv[key] = kw

  security.declareProtected( permissions.View, 'getDefaultActivateParameterDict' )
  def getDefaultActivateParameterDict(self, inherit_placeless=True):
    # This method returns default activate parameters to self.
    # The result can be either a dict object or None.
    tv = getTransactionalVariable(self)
    if inherit_placeless:
      placeless = tv.get(('default_activate_parameter', ))
      if placeless is not None:
        placeless = placeless.copy()
    else:
      placeless = None
    local = tv.get(('default_activate_parameter', id(aq_base(self))))
    if local is None:
      result = placeless
    else:
      if placeless is None:
        result = local.copy()
      else:
        # local defaults takes precedence over placeless defaults.
        result = {}
        result.update(placeless)
        result.update(local)
    return result

  def getActivityRuntimeEnvironment(self):
    return getActivityRuntimeEnvironment()
