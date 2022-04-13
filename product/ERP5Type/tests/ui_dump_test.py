##############################################################################
#
# Copyright (c) 2009 Nexedi SARL and Contributors. All Rights Reserved.
#                    Julien Muchembled <jm@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly advised to contract a Free Software
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

import os, sys, weakref
from difflib import unified_diff
from pprint import pprint, pformat
from AccessControl.SecurityManagement \
  import getSecurityManager, setSecurityManager
from Products.DCWorkflow.DCWorkflow import Unauthorized
from Testing import ZopeTestCase
from zLOG import LOG
import six


class ui_dump_test(object):
  """
  User Interface dump generator while running unit test.

  This class is usually subclassed. If you wish to store dump file,
  you should export os environment variable "save_<subclass_name>=1"
  """

  _enabled = None

  def __hook(*method_path_list):
    """Helper function to easily inject code at the end of methods

    Note: Methods are hooked permanently (when this module is imported), in
          order to avoid any conflict with interaction workflows.
    """
    def _setHook(wrapped, method_path):
      module_path, class_name, method_name = method_path.rsplit('.', 2)
      cls = getattr(__import__(module_path, fromlist=(class_name,), level=0),
                    class_name)
      original_method = getattr(cls, method_name)
      def hook(*args, **kw):
        result = original_method(*args, **kw)
        if ui_dump_test._enabled:
          wrapped(ui_dump_test._enabled, result, *args, **kw)
        return result
      hook.__doc__ = original_method.__doc__
      hook.__name__ = original_method.__name__
      setattr(cls, method_name, hook)
    def setHook(wrapped):
      for method_path in method_path_list:
        _setHook(wrapped, method_path)
      return classmethod(wrapped)
    return setHook

  def __new__(cls, wrapped):
    def wrapper(*args, **kw):
      self = object.__new__(cls)
      self.__init__(*args, **kw)
      try:
        try:
          ui_dump_test._enabled = self
          result = wrapped(*args, **kw)
        finally:
          ui_dump_test._enabled = None
        self.check()
      finally:
        del self.context
      return result
    wrapper.__doc__ = wrapped.__doc__
    wrapper.__name__ = wrapped.__name__
    return wrapper

  def __init__(self, context, *args, **kw):
    self.object_set = set()
    self.last_id_dict = {}
    self.virtual_path_dict = {}
    self.track_object_dict = {}
    self.dump = []
    self.dump_index = 0
    self.last_dump_dict = {}
    self.context = context
    self = weakref.proxy(self)
    context.checkUISecurity = lambda ob: self.trackObject(
      ob.getPhysicalPath()[2:], ob)

  # TODO: hook LocalRoleAssignorMixIn.updateLocalRolesOnDocument

  @__hook('Products.ERP5Type.Core.Folder.Folder._setObject')
  def Folder__setObject(__self, __result, self, id, object, *args, **kw):
    container = self.getPhysicalPath()[2:]
    path = container + (__result,)
    __self.last_id_dict.setdefault(container, 0)
    __self.last_id_dict[path] = None
    __self.trackObject(path, object)

  @__hook('Products.DCWorkflow.DCWorkflow'
          '.DCWorkflowDefinition._executeTransition')
  def DCWorkflowDefinition__executeTransition(__self, __result,
      self, ob, *args, **kw):
    __self.trackObject(ob.getPhysicalPath()[2:], ob)

  _module_tracking_blacklist = {
    'portal_simulation',
    'portal_solver_processes',
    'portal_activities',
  }

  def trackObject(self, path, ob):
    if (len(path) > 1
        and path[0] not in self._module_tracking_blacklist
        and not path[0].startswith('fake_')
        and not getattr(ob, 'isTempObject', bool)()):
      self.object_set.add(path)

  def getVirtualId(self, obj):
    """Return the id for children of tracked objects

    This allows to produce stable dumps.
    """
    return obj.getId()

  def getVirtualPath(self, path, obj, raise_if_new=0):
    virtual_path = self.virtual_path_dict.get(path)
    if not virtual_path:
      container = path[:-1]
      virtual_id = self.last_id_dict.get(container, 1)
      if virtual_id is None:
        container = self.getVirtualPath(container, obj.getParentValue(), 1)
        virtual_id = self.getVirtualId(obj)
      else:
        assert not raise_if_new, "Tracking a subobject of a new and" \
                                 " untracked object produces unstable dumps."
        self.last_id_dict[container] = virtual_id + 1
      self.virtual_path_dict[path] = virtual_path = container + (virtual_id,)
    return virtual_path

  def diff(self, expected_string):
    diff = tuple(unified_diff(pformat(eval(expected_string)).splitlines(),
                              pformat(self.dump).splitlines(),
                              n=6, lineterm=''))
    if diff:
      return '\n'.join(diff[2:])

  def check(self):
    context = self.context
    test_file = sys.modules[context.__class__.__module__].__file__
    dump_name = self.__class__.__name__
    dump_path = os.path.join(os.path.abspath(os.path.dirname(test_file)),
                             dump_name, '%s.py' % context.id())
    save_env_name = 'save_' + dump_name
    if os.environ.get(save_env_name) == '1':
      with open(dump_path, 'w') as f:
        pprint(self.dump, f)
    else:
      # The following 2 lines are only for debugging purpose: it saves the
      # actual results in a temporary place, so that when the diff is not
      # clear enough, one can inspect them in whole.
      with open(dump_path, 'w') as f:
        pprint(self.dump, f)
      with open(dump_path) as f:
        diff = self.diff(f.read())
      if diff:
        msg = ("UI dump for %r changed:\n%s\n\nTo update the dump, please"
               " run the test again setting the environment variable %r to 1.")
        context.fail(msg % (dump_path, diff, save_env_name))

  def getTrackingKey(self, path, obj):
    """Return the 'type' of object (only 1 object per 'type' is tracked)

    For each 'type' of object, we only dump data for the object with the
    smallest sorting key. This provides a way to avoid dumplicate dumps for
    similar objects.
    """
    return path[0], obj.getParentValue().getPortalType(), obj.getPortalType()

  def getSortingKey(self, obj):
    """Return a key to decide which object should be tracked

    When there are several candidate objects for the same tracking key,
    only the object with the smallest sorting key will be tracked.
    This allows to produce stable dumps.
    """
    return obj.getId()

  def getTrackedObjectList(self):
    # Because objects may be created in a random order, we must filter objects
    # to track at the last moment and provide an API so that the unit test can
    # decide which object to keep.
    best_object_dict = {}
    traverse = self.context.portal.unrestrictedTraverse
    for path in self.object_set:
      obj = traverse(path)
      key = self.getTrackingKey(path, obj)
      tracked_object = self.track_object_dict.get(key)
      if tracked_object == path:
        yield path, obj
      elif tracked_object is None:
        best_object = best_object_dict.setdefault(key, [])
        sorting_key = tuple(self.getSortingKey(x)
                            for x in obj.aq_chain[len(path)-1::-1])
        if not best_object or sorting_key < best_object[0]:
          best_object[:] = sorting_key, path, obj
    for key, (sorting_key, path, obj) in six.iteritems(best_object_dict):
      self.track_object_dict[key] = path
      yield path, obj

  @__hook('Products.ERP5Type.tests.ProcessingNodeTestCase.ProcessingNodeTestCase.tic')
  def flush(self, result, *args, **kw):
    if not self.object_set:
      return
    context = self.context
    security_manager = getSecurityManager()
    dump_list = []
    # sort by path, to process parent objects before children
    for path, obj in sorted(self.getTrackedObjectList()):
      dump_dict = {}
      for user_id in sorted(self.getUserList()):
        context.login(user_id)
        if context.portal.restrictedTraverse(path, None) is None:
          continue
        has_permission = getSecurityManager().getUser().has_permission
        permission = ''.join(sorted(permission_code
                                    for permission_code, permission in
                                      six.iteritems(self.getPermissionDict())
                                    if has_permission(permission, obj)))
        dump = dict(permission=permission)
        if 'V' in permission:
          try:
            dump.update((action_type,
                         sorted(action['id']
                                for action in action_list
                                if action['id'] != 'consistency'))
              for action_type, action_list in six.iteritems(context.portal.portal_actions
                .listFilteredActionsFor(obj))
              if action_list and action_type in ('object_view',
                                                 'object_action',
                                                 'object_jump',
                                                 'workflow'))
          except Unauthorized:
            pass
        dump_dict.setdefault(repr(dump), dump) \
                 .setdefault('user', []).append(user_id)
      # switch back to previous user here, because the current user may
      # not have permission to call some script used by getVirtualPath
      setSecurityManager(security_manager)
      path = self.getVirtualPath(path, obj)
      dump = (path, dict(x for x in obj.getWorkflowStateItemList() if x[1]),
                    sorted(six.itervalues(dump_dict), key=lambda x: x['user']))
      if dump != self.last_dump_dict.get(path):
        self.last_dump_dict[path] = dump
        dump_list.append(dump)
    if dump_list:
      dump_list.sort() # sort again by virtual path
      self.dump += self.dump_index, dump_list
      ZopeTestCase._print("\n    Dumping UI with index : %i" % self.dump_index)
      self.dump_index += 1
    self.object_set.clear()

  def getUserList(self):
    return self.context.portal.acl_users.zodb_users.listUserIds()

  def getPermissionDict(self):
    return {
      'A': 'Access contents information',
      'C': 'Add portal content',
      'M': 'Modify portal content',
      'V': 'View',
    }

  del __hook
