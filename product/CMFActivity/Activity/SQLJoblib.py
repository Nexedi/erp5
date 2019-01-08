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

from random import getrandbits
from zLOG import LOG, TRACE, INFO, WARNING, ERROR, PANIC
import MySQLdb
from MySQLdb.constants.ER import DUP_ENTRY
from SQLBase import (
  SQLBase, sort_message_key, MAX_MESSAGE_LIST_SIZE,
  UID_SAFE_BITSIZE, UID_ALLOCATION_TRY_COUNT,
)
from Products.CMFActivity.ActivityTool import Message
from SQLDict import SQLDict

class SQLJoblib(SQLDict):
  """
    An extention of SQLDict, It is non transatactional and follow always-excute paradigm.
    It uses a dictionary to store results and with hash of arguments as keys  
  """
  sql_table = 'message_job'
  uid_group = 'portal_activity_job'

  _createMessageTable = 'SQLJoblib_createMessageTable'

  def generateMessageUID(self, m):
    return (tuple(m.object_path), m.method_id, m.activity_kw.get('signature'),
                  m.activity_kw.get('tag'), m.activity_kw.get('group_id'))

  def prepareQueueMessageList(self, activity_tool, message_list):
    registered_message_list = [m for m in message_list if m.is_registered]
    portal = activity_tool.getPortalObject()
    for i in xrange(0, len(registered_message_list), MAX_MESSAGE_LIST_SIZE):
      message_list = registered_message_list[i:i+MAX_MESSAGE_LIST_SIZE]
      path_list = ['/'.join(m.object_path) for m in message_list]
      active_process_uid_list = [m.active_process_uid for m in message_list]
      method_id_list = [m.method_id for m in message_list]
      priority_list = [m.activity_kw.get('priority', 1) for m in message_list]
      date_list = [m.activity_kw.get('at_date') for m in message_list]
      group_method_id_list = [m.getGroupId() for m in message_list]
      tag_list = [m.activity_kw.get('tag', '') for m in message_list]
      signature_list=[m.activity_kw.get('signature', '') for m in message_list]
      serialization_tag_list = [m.activity_kw.get('serialization_tag', '')
                                for m in message_list]
      processing_node_list = []
      for m in message_list:
        m.order_validation_text = x = self.getOrderValidationText(m)
        processing_node_list.append(0 if x == 'none' else -1)
      for _ in xrange(UID_ALLOCATION_TRY_COUNT):
        try:
          portal.SQLJoblib_writeMessage(
            uid_list=[
              getrandbits(UID_SAFE_BITSIZE)
              for _ in xrange(len(message_list))
            ],
            path_list=path_list,
            active_process_uid_list=active_process_uid_list,
            method_id_list=method_id_list,
            priority_list=priority_list,
            message_list=map(Message.dump, message_list),
            group_method_id_list=group_method_id_list,
            date_list=date_list,
            tag_list=tag_list,
            processing_node_list=processing_node_list,
            signature_list=signature_list,
            serialization_tag_list=serialization_tag_list)
        except MySQLdb.IntegrityError, (code, _):
          if code != DUP_ENTRY:
            raise
        else:
          break
      else:
        raise ValueError("Maximum retry for SQLBase_writeMessageList reached")

  def getProcessableMessageLoader(self, db, processing_node):
    path_and_method_id_dict = {}
    quote = db.string_literal
    def load(line):
      # getProcessableMessageList already fetch messages with the same
      # group_method_id, so what remains to be filtered on are path, method_id
      # and signature
      path = line.path
      method_id = line.method_id
      key = path, method_id
      uid = line.uid
      original_uid = path_and_method_id_dict.get(key)
      if original_uid is None:
        m = Message.load(line.message, uid=uid, line=line)
        try:
          # Select duplicates.
          result = db.query("SELECT uid FROM message_job"
            " WHERE processing_node = 0 AND path = %s AND signature = %s"
            " AND method_id = %s AND group_method_id = %s FOR UPDATE" % (
              quote(path), quote(line.signature),
              quote(method_id), quote(line.group_method_id),
            ), 0)[1]
          uid_list = [x for x, in result]
          if uid_list:
            db.query(
              "UPDATE message_job SET processing_node=%s WHERE uid IN (%s)" % (
                processing_node, ','.join(map(str, uid_list)),
              ))
          db.query("COMMIT")
        except:
          self._log(WARNING, 'Failed to reserve duplicates')
          db.query("ROLLBACK")
          raise
        if uid_list:
          self._log(TRACE, 'Reserved duplicate messages: %r' % uid_list)
        path_and_method_id_dict[key] = uid
        return m, uid, uid_list
      # We know that original_uid != uid because caller skips lines we returned
      # earlier.
      return None, original_uid, [uid]
    return load
