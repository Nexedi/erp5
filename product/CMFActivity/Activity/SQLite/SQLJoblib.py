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

import sqlite3
from six.moves import xrange
from random import getrandbits
from Products.ERP5Type.Utils import str2bytes
from Products.CMFActivity.ActivityTool import Message
from ..Common.SQLBase import (
  render_datetime,
  UID_SAFE_BITSIZE,
  UID_ALLOCATION_TRY_COUNT,
)
from ..Common.SQLJoblib import SQLJoblib as _SQLJoblib
from .SQLDict import SQLDict


class SQLJoblib(_SQLJoblib, SQLDict):

  _insert_template = (b"INSERT INTO %s (uid,"
    b" path, active_process_uid, date, method_id, processing_node,"
    b" priority, group_method_id, tag, signature, serialization_tag,"
    b" message) VALUES\n")

  def _selectDuplicates(self, db, path, signature, method_id, group_method_id):
    sql = (b"SELECT uid FROM message_job"
      b" WHERE processing_node = 0 AND path = ? AND signature = ?"
      b" AND method_id = ? AND group_method_id = ?")
    args = (path, signature, method_id, group_method_id)
    return db.query(sql, 0, args=args)[1]

  def prepareQueueMessageList(self, activity_tool, message_list):
    db = activity_tool.getSQLConnection()
    insert_prefix = self._insert_template % str2bytes(self.sql_table)
    sep = self._insert_separator
    hasDependency = self._hasDependency
    def insert(rows):
      for _ in xrange(UID_ALLOCATION_TRY_COUNT):
        base = getrandbits(UID_SAFE_BITSIZE)
        row_sql_list = []
        all_args = []
        for i, (row_sql, row_args) in enumerate(rows):
          row_sql_list.append(row_sql)
          all_args.append(base + i)
          all_args.extend(row_args)
        sql = insert_prefix + sep.join(row_sql_list)
        try:
          db.query(sql, args=tuple(all_args))
        except sqlite3.IntegrityError as e:
          msg = str(e)
          if 'UNIQUE constraint failed' not in msg and 'PRIMARY KEY' not in msg:
            raise
        else:
          return
      raise ValueError("Maximum retry for prepareQueueMessageList reached")
    rows_list = []
    for m in message_list:
      if m.is_registered:
        date = m.activity_kw.get('at_date')
        if date is None:
          date_sql = b"UTC_TIMESTAMP(6)"
          date_args = ()
        else:
          date_sql = b'?'
          date_args = (render_datetime(date),)
        row_sql = b'(?,?,?,' + date_sql + b',?,?,?,?,?,?,?,?)'
        row_args = (
          '/'.join(m.object_path),
          m.active_process_uid,
          ) + date_args + (
          m.method_id,
          -1 if hasDependency(m) else 0,
          m.activity_kw.get('priority', 1),
          m.getGroupId(),
          m.activity_kw.get('tag', ''),
          m.activity_kw.get('signature', ''),
          m.activity_kw.get('serialization_tag', ''),
          Message.dump(m))
        rows_list.append((row_sql, row_args))
    if rows_list:
      insert(rows_list)

  def createTableSQL(self):
    return """\
CREATE TABLE %s (
  uid INTEGER NOT NULL,
  date TEXT NOT NULL,
  path TEXT NOT NULL,
  active_process_uid INTEGER,
  method_id TEXT NOT NULL,
  processing_node INTEGER NOT NULL DEFAULT -1,
  priority INTEGER NOT NULL DEFAULT 0,
  group_method_id TEXT NOT NULL DEFAULT '',
  tag TEXT NOT NULL,
  signature BLOB NOT NULL,
  serialization_tag TEXT NOT NULL,
  retry INTEGER NOT NULL DEFAULT 0,
  message BLOB NOT NULL,
  PRIMARY KEY (uid)
);
\0
CREATE INDEX IF NOT EXISTS %s_idx_processing_node_priority_date ON %s (processing_node, priority, date);
\0
CREATE INDEX IF NOT EXISTS %s_idx_node_group_priority_date ON %s (processing_node, group_method_id, priority, date);
\0
CREATE INDEX IF NOT EXISTS %s_idx_serialization_tag_processing_node ON %s (serialization_tag, processing_node);
\0
CREATE INDEX IF NOT EXISTS %s_idx_path ON %s (path);
\0
CREATE INDEX IF NOT EXISTS %s_idx_active_process_uid ON %s (active_process_uid);
\0
CREATE INDEX IF NOT EXISTS %s_idx_method_id ON %s (method_id);
\0
CREATE INDEX IF NOT EXISTS %s_idx_tag ON %s (tag);
""" % ((self.sql_table,) * 15)
