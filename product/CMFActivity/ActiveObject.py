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
import warnings
from contextlib import contextmanager
from AccessControl import ClassSecurityInfo
from Acquisition import aq_base
from Products.ERP5Type.Globals import InitializeClass
from Products.ERP5Type.TransactionalVariable import getTransactionalVariable
from ActivityRuntimeEnvironment import getActivityRuntimeEnvironment
from AccessControl import Unauthorized
from Products.CMFCore import permissions

DEFAULT_ACTIVITY = 'SQLDict'

_DEFAULT_ACTIVATE_PARAMETER_KEY = 'default_activate_parameter'

class ActiveObject(ExtensionClass.Base):
  """Active Object Mixin Class.

  Active object are objects whose methods are lazilly evaluated in the
  Activity Queue. To use an active object, you just have to call the
  method on the wrapper returned by the `activate` method like this:

  >>> obj.activate().aMethod()

  This will defer the call to obj.aMethod()
  """

  security = ClassSecurityInfo()

  security.declarePublic('activate')
  def activate(self, activity=DEFAULT_ACTIVITY, active_process=None,
               activate_kw=None, REQUEST=None, **kw):
    """Returns an active wrapper for this object.

      priority          --  any integer between -128 and 127 included
                            (default: 1)

      node              --  can be one of the following values:
        - "same": prefer execution on this node, to make
                  better use of the ZODB Storage cache
        - "": no node preference

      at_date           --  request execution date for this activate call
                            (default: date of commit)

      Messages are executed according to the following ordering:

        priority, node_preference, date

      where node_preference is:

        -1 -> same node
         0 -> no preferred node
         1 -> another node

      Validation parameters:

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
    if REQUEST is not None:
      # Prevent publication loudly.
      raise Unauthorized
    # Get activate values from activate_kw, then default_activate_parameter
    # transactional variable only if they are not set directly as arguments
    # to activate()
    new_kw = self.getDefaultActivateParameterDict()
    if activate_kw:
      new_kw.update(activate_kw)
    new_kw.update(kw)

    try:
      activity_tool = self.getPortalObject().portal_activities
    except AttributeError:
      return self # Do nothing if no portal_activities
    # activate returns an ActiveWrapper
    # a queue can be provided as well as extra parameters
    # which can be used for example to define deferred tasks
    return activity_tool.activateObject(
      self, activity, active_process, **new_kw)

  security.declareProtected( permissions.ModifyPortalContent, 'flushActivity' )
  def flushActivity(self, invoke=0, **kw):
    try:
      activity_tool = self.getPortalObject().portal_activities
    except AttributeError:
      return # Do nothing if no portal_activities
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
    try:
      activity_tool = self.getPortalObject().portal_activities
    except AttributeError:
      return 0 # Do nothing if no portal_activities
    return activity_tool.hasActivity(self, **kw)

  security.declareProtected( permissions.View, 'hasErrorActivity' )
  def hasErrorActivity(self, **kw):
    """Tells if there is failed activities for this object.
    """
    return self.hasActivity(only_invalid=True)

  def getActiveProcess(self):
    path = getActivityRuntimeEnvironment()._message.active_process
    if path:
      return self.unrestrictedTraverse(path)

  # XXX: Use something else than 'id(aq_base(self)))' because it
  #      would fail if object is ejected from connection cache.

  @contextmanager
  def defaultActivateParameterDict(self, parameter_dict, placeless=False):
    # XXX: Should we be more strict about reentrant calls ?
    #      - should they be forbidden ?
    #      - or should we merge entries ?
    if parameter_dict is None:
      yield
    else:
      tv = getTransactionalVariable()
      key = (_DEFAULT_ACTIVATE_PARAMETER_KEY,) if placeless else \
            (_DEFAULT_ACTIVATE_PARAMETER_KEY, id(aq_base(self)))
      old_kw = tv.get(key)
      tv[key] = parameter_dict.copy()
      try:
        yield
      finally:
        if old_kw is None:
          del tv[key]
        else:
          tv[key] = old_kw

  def setDefaultActivateParameterDict(self, parameter_dict, placeless=False):
    # This method sets the default keyword parameters to activate. This is
    # useful when you need to specify special parameters implicitly (e.g. to
    # reindexObject).
    tv = getTransactionalVariable()
    if placeless:
      key = (_DEFAULT_ACTIVATE_PARAMETER_KEY, )
    else:
      key = (_DEFAULT_ACTIVATE_PARAMETER_KEY, id(aq_base(self)))
    tv[key] = parameter_dict.copy()

  def setDefaultActivateParameters(self, placeless=False, **kw):
    warnings.warn('setDefaultActivateParameters is deprecated in favour of '
      'setDefaultActivateParameterDict.', DeprecationWarning)
    self.setDefaultActivateParameterDict(kw, placeless=placeless)

  def getDefaultActivateParameterDict(self, inherit_placeless=True):
    # This method returns default activate parameters to self.
    # The result is a dict object.
    default = {}
    tv = getTransactionalVariable()
    if inherit_placeless:
      placeless = tv.get((_DEFAULT_ACTIVATE_PARAMETER_KEY,), default)
    else:
      placeless = default
    local = tv.get((_DEFAULT_ACTIVATE_PARAMETER_KEY, id(aq_base(self))),
                   default)
    result = placeless.copy()
    # local defaults takes precedence over placeless defaults.
    result.update(local)
    return result

  def getActivityRuntimeEnvironment(self):
    return getActivityRuntimeEnvironment()

InitializeClass(ActiveObject)
