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
from SQLDict import SQLDict

from zLOG import LOG

class SQLQueue(SQLDict):
  """
    A simple OOBTree based queue. It should be compatible with transactions
    and provide sequentiality. Should not create conflict
    because use of OOBTree.
  """

  def queueMessage(self, activity_tool, m):
    activity_tool.SQLDict_writeMessage(path = '/'.join(m.object_path) , method_id = m.method_id, message = self.dumpMessage(m))

  def dequeueMessage(self, activity_tool, processing_node):
    #activity_tool.SQLDict_lockMessage() # Too slow...
    result = activity_tool.SQLDict_readMessage()
    if len(result) > 0:
      line = result[0]
      path = line.path
      method_id = line.method_id
      activity_tool.SQLDict_processMessage(path=path, method_id=method_id, processing_node=1)
      #activity_tool.SQLDict_unlockMessage() # Too slow...
      m = self.loadMessage(line.message)
      if m.validate(self, activity_tool):
        activity_tool.invoke(m)
      activity_tool.SQLDict_delMessage(message_id = 222) # We will need a message_id
      return 0
    #activity_tool.SQLDict_unlockMessage()
    return 1

  def hasActivity(self, activity_tool, object, method_id=None, **kw):
    my_object_path = '/'.join(object.getPhysicalPath())
    result = activity_tool.SQLDict_hasMessage(path=my_object_path, method_id=method_id)
    if len(result) > 0:
      return result[0].message_count > 0
    return 0

  def flush(self, activity_tool, object_path, invoke=0, method_id=None, **kw):
    """
      object_path is a tuple
    """
    path = '/'.join(object_path)
    # LOG('Flush', 0, str((path, invoke, method_id)))
    result = activity_tool.SQLDict_readMessageList(path=path, method_id=method_id)
    method_dict = {}
    if invoke:
      for line in result:
        path = line.path
        method_id = line.method_id
        if not method_dict.has_key(method_id):
          # Only invoke once (it would be different for a queue)
          method_dict[method_id] = 1
          m = self.loadMessage(line.message)
          if m.validate(self, activity_tool):
            activity_tool.invoke(m)
    activity_tool.SQLDict_delMessage(path=path, method_id=method_id)

  def getMessageList(self, activity_tool, processing_node=None):
    message_list = []
    result = activity_tool.SQLDict_readMessageList(path=None, method_id=None)
    for line in result:
      m = self.loadMessage(line.message)
      message_list.append(m)
    return message_list

registerActivity(SQLQueue)
