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

from zLOG import LOG

class RAMDict(Queue):
  """
    A simple RAM based queue. It is not compatible with transactions which
    means methods can be called before an object even exists or before
    it is modified. This also means there is no garantee on any kind of sequenciality.

    Dictionnary is global.
  """

  def __init__(self):
    Queue.__init__(self)
    self.dict = {}

  def finishQueueMessage(self, activity_tool, m):
    if m.is_registered:
      self.dict[(tuple(m.object_path), m.method_id)] = m

  def finishDeleteMessage(self, activity_tool, message):
    for key, m in self.dict.items():
      if m.object_path == message.object_path and m.method_id == message.method_id:
          del self.dict[(tuple(m.object_path), m.method_id)]

  def registerActivityBuffer(self, activity_buffer):
    class_name = self.__class__.__name__
    setattr(activity_buffer, '_%s_message_list' % class_name, [])
    setattr(activity_buffer, '_%s_uid_dict' % class_name, {})

  def isMessageRegistered(self, activity_buffer, activity_tool, m):
    class_name = self.__class__.__name__
    return getattr(activity_buffer, '_%s_uid_dict' % class_name).has_key((tuple(m.object_path), m.method_id))

  def registerMessage(self, activity_buffer, activity_tool, m):
    class_name = self.__class__.__name__
    getattr(activity_buffer, '_%s_message_list' % class_name).append(m)
    getattr(activity_buffer, '_%s_uid_dict' % class_name)[(tuple(m.object_path), m.method_id)] = 1
    m.is_registered = 1

  def dequeueMessage(self, activity_tool, processing_node):
    if len(self.dict.keys()) is 0:
      return 1  # Go to sleep
    for key, m in self.dict.items():
      if m.validate(self, activity_tool):
        activity_tool.invoke(m)
        del self.dict[key]
        get_transaction().commit()
        return 0
    return 1

  def hasActivity(self, activity_tool, object, **kw):
    if object is not None:
      object_path = object.getPhysicalPath()
      for m in self.dict.values():
        if m.object_path == object_path:
          return 1
    else:
      return 1 # Default behaviour if no object specified is to return 1 until active_process implemented
    return 0

  def flush(self, activity_tool, object_path, invoke=0, method_id=None, **kw):
    path = '/'.join(object_path)
    # LOG('Flush', 0, str((path, invoke, method_id)))
    method_dict = {}
    # Parse each message in registered
    for m in activity_tool.getRegisteredMessageList(self):
      if object_path == m.object_path and (method_id is None or method_id == m.method_id):
        activity_tool.unregisterMessage(self, m)
        if not method_dict.has_key(method_id):
          if invoke:
            # First Validate
            if m.validate(self, activity_tool):
              activity_tool.invoke(m) # Try to invoke the message - what happens if invoke calls flushActivity ??
              if not m.is_executed:                                                 # Make sure message could be invoked
                # The message no longer exists
                raise ActivityFlushError, (
                    'Could not evaluate %s on %s' % (method_id , path))
            else:
              # The message no longer exists
              raise ActivityFlushError, (
                  'The document %s does not exist' % path)               
    # Parse each message in RAM dict
    for key, m in self.dict.items():
      if object_path == m.object_path and (method_id is None or method_id == m.method_id):
        LOG('CMFActivity RAMDict: ', 0, 'flushing object %s' % '/'.join(m.object_path))
        if invoke: activity_tool.invoke(m)
        self.deleteMessage(activity_tool, m)

  def getMessageList(self, activity_tool, processing_node=None):
    return self.dict.values()

registerActivity(RAMDict)
