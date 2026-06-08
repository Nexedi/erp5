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
from random import getrandbits
import MySQLdb
from MySQLdb.constants.ER import DUP_ENTRY
from Products.ERP5Type.Utils import str2bytes
from Products.CMFActivity.ActivityTool import Message
from ..SQLBase import (
  render_datetime,
  UID_SAFE_BITSIZE,
  UID_ALLOCATION_TRY_COUNT,
)
from ..SQLJoblib import SQLJoblib as _SQLJoblib
from .SQLDict import SQLDict


class SQLJoblib(_SQLJoblib, SQLDict):

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
          db.query(b"SET @uid := %d" % getrandbits(UID_SAFE_BITSIZE))
        try:
          db.query(self._insert_template % (str2bytes(self.sql_table), values))
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
          b'@uid+%s' % str2bytes(str(i)),
          quote('/'.join(m.object_path)),
          b'NULL' if active_process_uid is None else str2bytes(str(active_process_uid)),
          b"UTC_TIMESTAMP(6)" if date is None else quote(render_datetime(date)),
          quote(m.method_id),
          b'-1' if hasDependency(m) else b'0',
          str2bytes(str(m.activity_kw.get('priority', 1))),
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

  def _selectDuplicates(self, db, path, signature, method_id, group_method_id):
    quote = db.string_literal
    sql = b"SELECT uid FROM message_job" \
      b" WHERE processing_node = 0 AND path = %s AND signature = %s" \
      b" AND method_id = %s AND group_method_id = %s FOR UPDATE%s" % (
        quote(path), quote(signature),
        quote(method_id), quote(group_method_id),
        b' SKIP LOCKED' if db.has_skip_locked else b'',
      )
    return db.query(sql, 0)[1]

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
