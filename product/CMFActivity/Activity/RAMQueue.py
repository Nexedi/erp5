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

from Products.CMFActivity.ActivityTool import registerActivity
from Queue import Queue
from Products.CMFActivity.ActiveObject import DISTRIBUTABLE_STATE, INVOKE_ERROR_STATE, VALIDATE_ERROR_STATE

class RAMQueue(Queue):
  """
    A simple RAM based queue
  """
  def __init__(self):
    Queue.__init__(self)
    self.queue = []
    self.last_uid = 0
    
  def finishQueueMessage(self, activity_tool, m):
    if m.is_registered:
      # XXX - Some lock is required on this section
      self.last_uid = self.last_uid + 1
      m.uid = self.last_uid
      self.queue.append(m)

  def finishDeleteMessage(self, activity_tool, m):
    i = 0
    for my_message in self.queue:
      if my_message.uid == m.uid:
        del self.queue[i]
        return
      i = i + 1
    
  def dequeueMessage(self, activity_tool, processing_node):
    if len(self.queue) is 0:
      return 1  # Go to sleep
    m = self.queue[0]
    activity_tool.invoke(m)
    self.deleteMessage(m)
    return 0    # Keep on ticking

  def hasActivity(self, activity_tool, object, **kw):
    object_path = object.getPhysicalPath()
    for m in self.queue:
      if m.object_path == object_path:
        return 1
    return 0

  def flush(self, activity_tool, object_path, invoke=0, method_id=None, **kw):
    # Parse each message in registered
    for m in activity_tool.getRegisteredMessageList(self):
      if object_path == m.object_path and (method_id is None or method_id == m.method_id):
        if invoke: activity_tool.invoke(m)
        self.unregisterMessage(m)
    # Parse each message in queue
    for m in self.queue:
      if object_path == m.object_path and (method_id is None or method_id == m.method_id):
        if invoke: activity_tool.invoke(m)
        self.deleteMessage(m)

  def getMessageList(self, activity_tool, processing_node=None):
    new_queue = []
    for m in self.queue:
      m.processing_node = 1
      m.priority = 0
      new_queue.append(m)
    return new_queue

registerActivity(RAMQueue)
