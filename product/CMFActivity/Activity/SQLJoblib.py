from __future__ import absolute_import
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
from .SQLBase import (
  SQLBase, sort_message_key,
  UID_SAFE_BITSIZE, UID_ALLOCATION_TRY_COUNT,
)
from Products.CMFActivity.ActivityTool import Message
from .SQLDict import SQLDict
from six.moves import xrange

class SQLJoblib(SQLDict):
  """
    An extention of SQLDict, It is non transatactional and follow always-excute paradigm.
    It uses a dictionary to store results and with hash of arguments as keys
  """
  sql_table = 'message_job'
  uid_group = 'portal_activity_job'

  def createTableSQL(self):
    return """\
CREATE TABLE %s (
  `uid` BIGINT UNSIGNED NOT NULL,
  `date` DATETIME(6) NOT NULL,
  `path` VARCHAR(255) NOT NULL,
  `active_process_uid` INT UNSIGNED NULL,
  `method_id` VARCHAR(255) NOT NULL,
  `processing_node` SMALLINT NOT NULL DEFAULT -1,
  `priority` TINYINT NOT NULL DEFAULT 0,
  `group_method_id` VARCHAR(255) NOT NULL DEFAULT '',
  `tag` VARCHAR(255) NOT NULL,
  `signature` BINARY(16) NOT NULL,
  `serialization_tag` VARCHAR(255) NOT NULL,
  `retry` TINYINT UNSIGNED NOT NULL DEFAULT 0,
  `message` LONGBLOB NOT NULL,
  PRIMARY KEY (`uid`),
  KEY `processing_node_priority_date` (`processing_node`, `priority`, `date`),
  KEY `node_group_priority_date` (`processing_node`, `group_method_id`, `priority`, `date`),
  KEY `serialization_tag_processing_node` (`serialization_tag`, `processing_node`),
  KEY (`path`),
  KEY (`active_process_uid`),
  KEY (`method_id`),
  KEY (`tag`)
) ENGINE=InnoDB""" % self.sql_table

  def generateMessageUID(self, m):
    return (tuple(m.object_path), m.method_id, m.activity_kw.get('signature'),
                  m.activity_kw.get('tag'), m.activity_kw.get('group_id'))

  _insert_template = (b"INSERT INTO %s (uid,"
    b" path, active_process_uid, date, method_id, processing_node,"
    b" priority, group_method_id, tag, signature, serialization_tag,"
    b" message) VALUES\n(%s)")

  def prepareQueueMessageList(self, activity_tool, message_list):
    db = activity_tool.getSQLConnection()
    quote = db.string_literal
    def insert(reset_uid):
      values = self._insert_separator.join(values_list)
      del values_list[:]
      for _ in xrange(UID_ALLOCATION_TRY_COUNT):
        if reset_uid:
          reset_uid = False
          # Overflow will result into IntegrityError.
          db.query(b"SET @uid := %s" % str(getrandbits(UID_SAFE_BITSIZE)).encode())
        try:
          db.query(self._insert_template % (self.sql_table.encode(), values))
        except MySQLdb.IntegrityError as e:
          if e.args[0] != DUP_ENTRY:
            raise
          reset_uid = True
        else:
          break
      else:
        raise ValueError("Maximum retry for prepareQueueMessageList reached")
    i = 0
    reset_uid = True
    values_list = []
    max_payload = self._insert_max_payload
    sep_len = len(self._insert_separator)
    hasDependency = self._hasDependency
    for m in message_list:
      if m.is_registered:
        active_process_uid = m.active_process_uid
        date = m.activity_kw.get('at_date')
        row = b','.join((
          b'@uid+%s' % str(i).encode(),
          quote('/'.join(m.object_path)),
          b'NULL' if active_process_uid is None else str(active_process_uid).encode(),
          b"UTC_TIMESTAMP(6)" if date is None else quote(render_datetime(date)),
          quote(m.method_id),
          b'-1' if hasDependency(m) else b'0',
          str(m.activity_kw.get('priority', 1)).encode(),
          quote(m.getGroupId()),
          quote(m.activity_kw.get('tag', '')),
          quote(m.activity_kw.get('signature', '')),
          quote(m.activity_kw.get('serialization_tag', '')),
          quote(Message.dump(m))))
        i += 1
        n = sep_len + len(row)
        max_payload -= n
        if max_payload < 0:
          if values_list:
            insert(reset_uid)
            reset_uid = False
            max_payload = self._insert_max_payload - n
          else:
            raise ValueError("max_allowed_packet too small to insert message")
        values_list.append(row)
    if values_list:
      insert(reset_uid)

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
          result = db.query(b"SELECT uid FROM message_job"
            b" WHERE processing_node = 0 AND path = %s AND signature = %s"
            b" AND method_id = %s AND group_method_id = %s FOR UPDATE" % (
              quote(path), quote(line.signature),
              quote(method_id), quote(line.group_method_id),
            ), 0)[1]
          uid_list = [x for x, in result]
          if uid_list:
            self.assignMessageList(db, processing_node, uid_list)
          else:
            db.query(b"COMMIT") # XXX: useful ?
        except:
          self._log(WARNING, 'Failed to reserve duplicates')
          db.query(b"ROLLBACK")
          raise
        if uid_list:
          self._log(TRACE, 'Reserved duplicate messages: %r' % uid_list)
        path_and_method_id_dict[key] = uid
        return m, uid, uid_list
      # We know that original_uid != uid because caller skips lines we returned
      # earlier.
      return None, original_uid, [uid]
    return load

  def getPriority(self, activity_tool, processing_node, node_set):
    return SQLDict.getPriority(self, activity_tool, processing_node)

  def getReservedMessageList(self, db, date, processing_node,
                             limit=None, group_method_id=None, node_set=None):
    return SQLDict.getReservedMessageList(self, db,
      date, processing_node, limit, group_method_id)
