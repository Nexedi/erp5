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

from six.moves import xrange
from zLOG import TRACE, WARNING
from Products.ERP5Type.Utils import str2bytes
from Products.CMFActivity.ActivityTool import Message
from .SQLBase import (
  _render_arg,
  render_datetime,
  UID_SAFE_BITSIZE,
  UID_ALLOCATION_TRY_COUNT,
)
from .SQLDict import SQLDict
from random import getrandbits

class SQLJoblib(SQLDict):
  """
    An extention of SQLDict, It is non transatactional and follow always-excute paradigm.
    It uses a dictionary to store results and with hash of arguments as keys
  """
  sql_table = 'message_job'
  uid_group = 'portal_activity_job'

  _insert_template = (b"INSERT INTO %s (uid,"
    b" path, active_process_uid, date, method_id, processing_node,"
    b" priority, group_method_id, tag, signature, serialization_tag,"
    b" message) VALUES\n")

  def generateMessageUID(self, m):
    return (tuple(m.object_path), m.method_id, m.activity_kw.get('signature'),
                  m.activity_kw.get('tag'), m.activity_kw.get('group_id'))

  def _beforeReserveDuplicates(self, db):
    pass

  def prepareQueueMessageList(self, activity_tool, message_list):
    db = activity_tool.getSQLConnection()
    quote = db.string_literal
    now_sql = self._now_sql_expr
    insert_prefix = self._insert_template % str2bytes(self.sql_table)
    sep = self._insert_separator
    sep_len = len(sep)
    # Worst-case digit width of a uid value, derived from UID_SAFE_BITSIZE.
    uid_width = len(str((1 << UID_SAFE_BITSIZE) - 1))
    def insert(rows, base, offset):
      for _ in xrange(UID_ALLOCATION_TRY_COUNT):
        if base is None:
          base = getrandbits(UID_SAFE_BITSIZE)
          offset = 0
        row_sql_list = []
        all_args = []
        for i, (row_sql, row_args) in enumerate(rows):
          row_sql_list.append(row_sql)
          all_args.append(base + offset + i)
          all_args.extend(row_args)
        sql = insert_prefix + sep.join(row_sql_list)
        try:
          self._executeQuery(db, sql, tuple(all_args))
        except self._integrity_error_class as e:
          if not self._isDuplicateEntryError(e):
            raise
          base = None
        else:
          return base, offset + len(rows)
      raise ValueError("Maximum retry for prepareQueueMessageList reached")
    rows_list = []
    max_payload = self._insert_max_payload
    hasDependency = self._hasDependency
    base = None
    offset = 0
    for m in message_list:
      if m.is_registered:
        active_process_uid = m.active_process_uid
        date = m.activity_kw.get('at_date')
        if date is None:
          date_sql = now_sql
          date_args = ()
        else:
          date_sql = b'?'
          date_args = (render_datetime(date),)
        row_sql = b'(?,?,?,' + date_sql + b',?,?,?,?,?,?,?,?)'
        row_args = (
          '/'.join(m.object_path),
          active_process_uid,
          ) + date_args + (
          m.method_id,
          -1 if hasDependency(m) else 0,
          m.activity_kw.get('priority', 1),
          m.getGroupId(),
          m.activity_kw.get('tag', ''),
          m.activity_kw.get('signature', ''),
          m.activity_kw.get('serialization_tag', ''),
          Message.dump(m))
        # Rendered byte size of this row once `?` placeholders are substituted
        # (MySQL path). Equals row_sql length minus its `?` chars, plus the
        # uid width, plus the actual rendered length of each value.
        n = sep_len + len(row_sql) - (len(row_args) + 1) + uid_width + sum(
          len(_render_arg(a, quote)) for a in row_args
        )
        max_payload -= n
        if max_payload < 0:
          if rows_list:
            base, offset = insert(rows_list, base, offset)
            del rows_list[:]
            max_payload = self._insert_max_payload - n
          else:
            raise ValueError("max_allowed_packet too small to insert message")
        rows_list.append((row_sql, row_args))
    if rows_list:
      insert(rows_list, base, offset)

  def getProcessableMessageLoader(self, db, processing_node):
    path_and_method_id_dict = {}
    for_update = self._for_update_sql + self._skip_locked_sql(db)
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
          self._beforeReserveDuplicates(db)
          # Select duplicates.
          sql = (b"SELECT uid FROM message_job"
            b" WHERE processing_node = 0 AND path = ? AND signature = ?"
            b" AND method_id = ? AND group_method_id = ?" + for_update)
          args = (path, line.signature, method_id, line.group_method_id)
          result = self._executeQuery(db, sql, args, max_rows=0)[1]
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
