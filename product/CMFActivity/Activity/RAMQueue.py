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

class RAMQueue(Queue):
  """
    A simple RAM based queue
  """

  def __init__(self):
    Queue.__init__(self)
    self.queue = []

  def queueMessage(self, activity_tool, m):
    self.queue.append(m)

  def dequeueMessage(self, activity_tool, processing_node):
    if len(self.queue) is 0:
      return 1  # Go to sleep
    m = self.queue[0]
    activity_tool.invoke(m)
    del self.queue[0]
    return 0    # Keep on ticking

  def hasActivity(self, object, method_id=None, **kw):
    object_path = object.getPhysicalPath()
    for m in self.queue:
      if m.object_path == object_path:
        return 1
    return 0

  def flush(self, activity_tool, object_path, **kw):
    new_queue = []
    for m in self.queue:
      if m.object_path == object_path:
        activity_tool.invoke(m)
        del self.dict[key]
      else:
        new_queue.append(m)
    self.queue = new_queue

  def getMessageList(self, activity_tool, processing_node=None):
    return self.queue

registerActivity(RAMQueue)
