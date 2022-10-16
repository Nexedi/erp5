##############################################################################
#
# Copyright (c) 2011 Nexedi SARL and Contributors. All Rights Reserved.
#                    Julien Muchembled <jm@nexedi.com>
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

import errno, glob, os, threading
from Acquisition import aq_base
from Products.ERP5Type.Tool.BaseTool import BaseTool
from Products.ERP5Type.TransactionalVariable import TransactionalResource
from Products.ERP5.mixin.timer_service import TimerServiceMixin
from AccessControl.SecurityManagement import newSecurityManager, \
  getSecurityManager, setSecurityManager
import six

# TODO: Current API was designed to avoid compability issues in case it is
#       reimplemented using https://pypi.python.org/pypi/pyinotify

IN_CREATE = 1
IN_MODIFY = 2
IN_DELETE = 512

timerservice_lock = threading.Lock()
inotify_state_dict = {}

class InotifyTool(TimerServiceMixin, BaseTool):
  """
  """

  id = 'portal_inotify'
  meta_type = 'ERP5 Inotify Tool'
  portal_type = 'Inotify Tool'
  title = 'Inotifies'

  def resetCache(self):
    self._p_changed = 1
    try:
      del self._v_notify_list
    except AttributeError:
      pass

  def process_timer(self, tick, interval, prev="", next=""): # pylint: disable=redefined-builtin
    if timerservice_lock.acquire(0):
      try:
        try:
          notify_list = aq_base(self)._v_notify_list
        except AttributeError:
          current_node = self.getCurrentNode()
          self._v_notify_list = notify_list = [x.getId()
            for x in self.objectValues()
            if x.isEnabled() and current_node in x.getNodeList()]
        update_state_dict = {}
        original_security_manager = getSecurityManager()
        for notify_id in notify_list:
          notify = self._getOb(notify_id)
          newSecurityManager(None, notify.getWrappedOwner())
          try:
            inode_path = notify.getInodePath()
            if inode_path:
              path = notify.getPath()
              state = inotify_state_dict.get(path, {})
              new_state = {}
              for inode_path in glob.glob(inode_path):
                for name in os.listdir(inode_path):
                  p = os.path.join(inode_path, name)
                  try:
                    s = os.lstat(p)
                  except OSError as e:
                    if e.errno != errno.ENOENT:
                      raise
                  else:
                    new_state[p] = s.st_mtime, s.st_size
              if new_state != state:
                update_state_dict[path] = new_state
                events = [{'path': p, 'mask': IN_DELETE}
                  for p in set(state).difference(new_state)]
                for p, m in six.iteritems(new_state):
                  if p in state:
                    if m == state[p]:
                      continue
                    mask = IN_MODIFY
                  else:
                    mask = IN_CREATE
                  events.append({'path': p, 'mask': mask})
                getattr(notify, notify.getSenseMethodId())(events)
          finally:
            setSecurityManager(original_security_manager)

        if update_state_dict:
          TransactionalResource(tpc_finish=lambda txn:
            inotify_state_dict.update(update_state_dict))
      finally:
        timerservice_lock.release()
