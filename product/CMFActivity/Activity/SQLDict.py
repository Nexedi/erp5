##############################################################################
#
# Copyright (c) 2002,2007 Nexedi SA and Contributors. All Rights Reserved.
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

from Products.CMFActivity.ActivityTool import Message
import sys
#from time import time
from SQLBase import SQLBase, sort_message_key

import transaction

from zLOG import TRACE, WARNING

# Stop validating more messages when this limit is reached
MAX_VALIDATED_LIMIT = 1000
# Read up to this number of messages to validate.
READ_MESSAGE_LIMIT = 1000

class SQLDict(SQLBase):
  """
    A simple OOBTree based queue. It should be compatible with transactions
    and provide sequentiality. Should not create conflict
    because use of OOBTree.
  """
  sql_table = 'message'
  uid_group = 'portal_activity'

  def generateMessageUID(self, m):
    return (tuple(m.object_path), m.method_id, m.activity_kw.get('tag'), m.activity_kw.get('group_id'))

  def isMessageRegistered(self, activity_buffer, activity_tool, m):
    # BBB: deprecated
    return self.generateMessageUID(m) in activity_buffer.getUidSet(self)

  def registerMessage(self, activity_buffer, activity_tool, m):
    message_id = self.generateMessageUID(m)
    uid_set = activity_buffer.getUidSet(self)
    if message_id in uid_set:
      return
    uid_set.add(message_id)
    super(SQLDict, self).registerMessage(activity_buffer, activity_tool, m)

  def unregisterMessage(self, activity_buffer, activity_tool, m):
    m.is_registered = False # This prevents from inserting deleted messages into the queue
    class_name = self.__class__.__name__
    uid_set = activity_buffer.getUidSet(self)
    uid_set.discard(self.generateMessageUID(m))

  def getRegisteredMessageList(self, activity_buffer, activity_tool):
    message_list = activity_buffer.getMessageList(self)
    return [m for m in message_list if m.is_registered]

  def getProcessableMessageLoader(self, activity_tool, processing_node):
    path_and_method_id_dict = {}
    def load(line):
      # getProcessableMessageList already fetch messages with the same
      # group_method_id, so what remains to be filtered on are path and
      # method_id.
      # XXX: What about tag ?
      path = line.path
      method_id = line.method_id
      key = path, method_id
      uid = line.uid
      original_uid = path_and_method_id_dict.get(key)
      if original_uid is None:
        m = Message.load(line.message, uid=uid, line=line)
        merge_parent = m.activity_kw.get('merge_parent')
        try:
          if merge_parent:
            path_list = []
            while merge_parent != path:
              path = path.rsplit('/', 1)[0]
              assert path
              original_uid = path_and_method_id_dict.get((path, method_id))
              if original_uid is not None:
                return None, original_uid, [uid]
              path_list.append(path)
            uid_list = []
            if path_list:
              result = activity_tool.SQLDict_selectParentMessage(
                path=path_list,
                method_id=method_id,
                group_method_id=line.group_method_id,
                processing_node=processing_node)
              if result: # found a parent
                # mark child as duplicate
                uid_list.append(uid)
                # switch to parent
                line = result[0]
                key = line.path, method_id
                uid = line.uid
                m = Message.load(line.message, uid=uid, line=line)
            # return unreserved similar children
            result = activity_tool.SQLDict_selectChildMessageList(
              path=line.path,
              method_id=method_id,
              group_method_id=line.group_method_id)
            reserve_uid_list = [x.uid for x in result]
            uid_list += reserve_uid_list
            if not line.processing_node:
              # reserve found parent
              reserve_uid_list.append(uid)
          else:
            result = activity_tool.SQLDict_selectDuplicatedLineList(
              path=path,
              method_id=method_id,
              group_method_id=line.group_method_id)
            reserve_uid_list = uid_list = [x.uid for x in result]
          if reserve_uid_list:
            activity_tool.SQLDict_reserveDuplicatedLineList(
              processing_node=processing_node, uid=reserve_uid_list)
          else:
            activity_tool.SQLDict_commit() # release locks
        except:
          self._log(WARNING, 'getDuplicateMessageUidList got an exception')
          activity_tool.SQLDict_rollback() # release locks
          raise
        if uid_list:
          self._log(TRACE, 'Reserved duplicate messages: %r' % uid_list)
        path_and_method_id_dict[key] = uid
        return m, uid, uid_list
      # We know that original_uid != uid because caller skips lines we returned
      # earlier.
      return None, original_uid, [uid]
    return load
