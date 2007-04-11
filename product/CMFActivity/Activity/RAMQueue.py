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
from Queue import Queue, VALID

try:
  from transaction import get as get_transaction
except ImportError:
  pass

class RAMQueue(Queue):
  """
    A simple RAM based queue
  """
  def __init__(self):
    Queue.__init__(self)
    self.queue_dict = {}
    self.last_uid = 0

  def getQueue(self, activity_tool_path):
    return self.queue_dict.setdefault(activity_tool_path, [])

  def finishQueueMessage(self, activity_tool_path, m):
    if m.is_registered:
      # XXX - Some lock is required on this section
      self.last_uid = self.last_uid + 1
      m.uid = self.last_uid
      self.getQueue(activity_tool_path).append(m)

  def finishDeleteMessage(self, activity_tool_path, m):
    i = 0
    queue = self.getQueue(activity_tool_path)
    for my_message in queue:
      if my_message.uid == m.uid:
        del queue[i]
        return
      i = i + 1

  def dequeueMessage(self, activity_tool, processing_node):
    path = activity_tool.getPhysicalPath()
    for m in self.getQueue(path):
      if m.validate(self, activity_tool) is not VALID:
        self.deleteMessage(activity_tool, m) # Trash messages which are not validated (no error handling)
        get_transaction().commit() # Start a new transaction
        return 0    # Keep on ticking
      activity_tool.invoke(m)
      if m.is_executed:
        self.deleteMessage(activity_tool, m) # Trash messages which are not validated (no error handling)
        get_transaction().commit() # Start a new transaction
        return 0    # Keep on ticking
      else:
        # Start a new transaction and keep on to next message
        get_transaction().commit()
    return 1 # Go to sleep

  def countMessage(self, activity_tool,path=None,method_id=None,**kw):
    tool_path = activity_tool.getPhysicalPath()
    count = 0
    for m in self.getQueue(tool_path):
      add = 1
      if path is not None:
        object_path = '/'.join(m.object_path)
        if object_path != path:
          add = 0
      if method_id is not None:
        if m.method_id != method_id:
          add = 0
      count += add
    return count

  def hasActivity(self, activity_tool, object, **kw):
    if object is not None:
      object_path = object.getPhysicalPath()
    else:
      object_path = None  
    active_process = kw.get('active_process', None)
    path = activity_tool.getPhysicalPath()
    for m in self.getQueue(path):
      # Filter active process and path if defined
      if active_process is None or m.active_process == active_process:
        if object_path is None or m.object_path == object_path:
          return 1
    return 0

  def flush(self, activity_tool, object_path, invoke=0, method_id=None, **kw):
    # Parse each message in registered
    for m in activity_tool.getRegisteredMessageList(self):
      if object_path == m.object_path and (method_id is None or method_id == m.method_id):
        if m.validate(self, activity_tool) is not VALID: 
          activity_tool.unregisterMessage(self, m) # Trash messages which are not validated (no error handling)
        else:
          if invoke:
            activity_tool.invoke(m)
            if m.is_executed:
              activity_tool.unregisterMessage(self, m)
          else:
            activity_tool.unregisterMessage(self, m)
    # Parse each message in queue
    path = activity_tool.getPhysicalPath()
    for m in self.getQueue(path):
      if object_path == m.object_path and (method_id is None or method_id == m.method_id):
        if m.validate(self, activity_tool) is not VALID:
          self.deleteMessage(activity_tool, m) # Trash messages which are not validated (no error handling)
        else:
          if invoke:
            activity_tool.invoke(m)
            if m.is_executed:
              self.deleteMessage(activity_tool, m) # Only delete if no error happens
          else:
            self.deleteMessage(activity_tool, m)

  def getMessageList(self, activity_tool, processing_node=None,**kw):
    new_queue = []
    path = activity_tool.getPhysicalPath()
    for m in self.getQueue(path):
      m.processing_node = 1
      m.priority = 0
      new_queue.append(m)
    return new_queue

registerActivity(RAMQueue)
