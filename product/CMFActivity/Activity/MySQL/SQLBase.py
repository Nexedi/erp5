from __future__ import absolute_import
##############################################################################
#
# Copyright (c) 2007 Nexedi SA and Contributors. All Rights Reserved.
#                    Vincent Pelletier <vincent@nexedi.com>
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

from contextlib import contextmanager
from itertools import chain
from random import getrandbits
import six
from six.moves import xrange
import MySQLdb
from MySQLdb.constants.ER import DUP_ENTRY
from Products.ERP5Type.Utils import str2bytes, bytes2str
from Shared.DC.ZRDB.Results import Results
from Products.CMFActivity.ActivityTool import Message
from ..Common.SQLBase import (
  SQLBase as _SQLBase,
  sort_message_key,
  render_datetime,
  sqltest_dict,
  INVOKE_ERROR_STATE,
  DEPENDENCY_IGNORED_ERROR_STATE,
  MAX_VALIDATED_LIMIT,
  READ_MESSAGE_LIMIT,
  UID_SAFE_BITSIZE,
  UID_ALLOCATION_TRY_COUNT,
)


class SQLBase(_SQLBase):

  # Limit the number of UNION-joined subqueries per query when looking for
  # blocking activities. Used to take a slice from a list.
  # XXX: 5000 is known to work on a case on "after_tag" dependency, which fails
  # at 5400 with:
  #   ProgrammingError: (1064, "memory exhausted near [...]")
  _MAX_DEPENDENCY_UNION_SUBQUERY_COUNT = -5000

  _insert_template = (b"INSERT INTO %s (uid,"
    b" path, active_process_uid, date, method_id, processing_node,"
    b" priority, node, group_method_id, tag, serialization_tag,"
    b" message) VALUES\n(%s)")
  _insert_separator = b"),\n("

  def initialize(self, activity_tool, clear):
    super(SQLBase, self).initialize(activity_tool, clear)
    db = activity_tool.getSQLConnection()
    self._insert_max_payload = (db.getMaxAllowedPacket()
      + len(self._insert_separator)
      - len(self._insert_template % (str2bytes(self.sql_table), b'')))

  def _dependencySubqueryPrefix(self, column_list):
    return b'(SELECT %s FROM ' % (
      b','.join([str2bytes(c) for c in column_list]),
    )

  def hasActivitySQL(self, quote, only_valid=False, only_invalid=False, **kw):
    # Joined with UNION ALL by ActivityTool.hasActivity; parens around each
    # leg let MySQL accept LIMIT per leg.
    where = [sqltest_dict[k](v, quote) for (k, v) in six.iteritems(kw) if v]
    if only_valid:
      where.append(b'processing_node > %d' % INVOKE_ERROR_STATE)
    if only_invalid:
      where.append(b'processing_node <= %d' % INVOKE_ERROR_STATE)
    return b"(SELECT 1 FROM %s WHERE %s LIMIT 1)" % (
      str2bytes(self.sql_table), b" AND ".join(where) or b"1")

  @contextmanager
  def SQLLock(self, db, lock_name, timeout):
    """
    Attemp to acquire a named SQL lock. The outcome of this acquisition is
    returned to the context statement and MUST be checked:
    1: lock acquired
    0: timeout
    """
    lock_name = db.string_literal(lock_name)
    query = db.query
    (_, ((acquired, ), )) = query(
      b'SELECT GET_LOCK(%s, %f)' % (lock_name, timeout),
      max_rows=0,
    )
    if acquired is None:
      raise ValueError('Error acquiring lock')
    try:
      yield acquired
    finally:
      if acquired:
        query(
          b'SELECT RELEASE_LOCK(%s)' % (lock_name, ),
          max_rows=0,
        )

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
        raise RuntimeError("Maximum retry for prepareQueueMessageList reached")
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
          b'@uid+%d' % i,
          quote('/'.join(m.object_path)),
          b'NULL' if active_process_uid is None else str2bytes(str(active_process_uid)),
          b"UTC_TIMESTAMP(6)" if date is None else quote(render_datetime(date)),
          quote(m.method_id),
          b'-1' if hasDependency(m) else b'0',
          str2bytes(str(m.activity_kw.get('priority', 1))),
          str2bytes(str(m.activity_kw.get('node', 0))),
          quote(m.getGroupId()),
          quote(m.activity_kw.get('tag', b'')),
          quote(m.activity_kw.get('serialization_tag', b'')),
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

  def _selectPriority(self, db, processing_node, node_set):
    query = db.query
    if node_set is None:
      return query(
        b"SELECT 3*priority, date"
        b" FROM %s"
        b" WHERE"
        b"  processing_node=0 AND"
        b"  date <= UTC_TIMESTAMP(6)"
        b" ORDER BY priority, date"
        b" LIMIT 1" % str2bytes(self.sql_table),
        0,
      )[1]
    # MariaDB often choose processing_node_priority_date index
    # but node2_priority_date is much faster if there exist
    # many node < 0 non-groupable activities.
    force_index = 'FORCE INDEX (node2_priority_date)'
    subquery = lambda *a, **k: str2bytes(bytes2str(b"("
      b"SELECT 3*priority{} AS effective_priority, date"
      b" FROM %s"
      b" {}"
      b" WHERE"
      b"  {} AND"
      b"  processing_node=0 AND"
      b"  date <= UTC_TIMESTAMP(6)"
      b" ORDER BY priority, date"
      b" LIMIT 1"
    b")" % str2bytes(self.sql_table)).format(*a, **k))
    result = query(
      b"SELECT *"
      b" FROM (%s) AS t"
      b" ORDER BY effective_priority, date"
      b" LIMIT 1" % (
        b" UNION ALL ".join(
          chain(
            (
              subquery('-1', force_index, 'node = %i' % processing_node),
              subquery('', force_index, 'node=0'),
            ),
            (
              subquery('-1', force_index, 'node = %i' % x)
              for x in node_set
            ),
          ),
        )
      ),
      0,
    )[1]
    if not result:
      # We did not find any activity matching our node (by number nor by
      # family), nor by having no node preference. Look for any other
      # activity we could be allowed to execute.
      # This is slower than the above queries, because it does a range
      # scan, either on the "node" column to sort the set, or on the
      # sorted set to filter negative node values.
      # This is why this query is only executed when the previous one
      # did not find anything.
      result = query(subquery('+1', '', 'node>0'), 0)[1]
    return result

  def _selectReservedMessageList(self, db, date, processing_node, limit,
                                 group_method_id, node_set):
    quote = db.string_literal
    query = db.query
    args = (
      str2bytes(self.sql_table),
      sqltest_dict['to_date'](date, quote),
      (
        b' AND group_method_id=' + quote(group_method_id)
        if group_method_id else
        b''
      ),
      limit,
      b' SKIP LOCKED' if db.has_skip_locked else b'',
    )
    if node_set is None:
      return Results(query(
        b"SELECT *"
        b" FROM %s"
        b" WHERE"
        b"  processing_node=0 AND"
        b"  %s%s"
        b" ORDER BY priority, date"
        b" LIMIT %i"
        b" FOR UPDATE%s" % args,
        0,
      ))
    if group_method_id:
      force_index = ''
    else:
      # MariaDB often choose processing_node_priority_date index
      # but node2_priority_date is much faster if there exist
      # many node < 0 non-groupable activities.
      force_index = 'FORCE INDEX (node2_priority_date)'
    subquery = lambda *a, **k: str2bytes(bytes2str(b"("
      b"SELECT *, 3*priority{} AS effective_priority"
      b" FROM %s"
      b" {}"
      b" WHERE"
      b"  {} AND"
      b"  processing_node=0 AND"
      b"  %s%s"
      b" ORDER BY priority, date"
      b" LIMIT %i"
      b" FOR UPDATE%s"
    b")" % args).format(*a, **k))
    result = Results(query(
      b"SELECT *"
      b" FROM (%s) AS t"
      b" ORDER BY effective_priority, date"
      b" LIMIT %i" % (
        b" UNION ALL ".join(
          chain(
            (
              subquery('-1', force_index, 'node = %i' % processing_node),
              subquery('', force_index, 'node=0'),
            ),
            (
              subquery('-1', force_index, 'node = %i' % x)
              for x in node_set
            ),
          ),
        ),
        limit,
      ),
      0,
    ))
    if not result:
      # We did not find any activity matching our node (by number nor by
      # family), nor by having no node preference. Look for any other
      # activity we could be allowed to execute.
      # This is slower than the above queries, because it does a range
      # scan, either on the "node" column to sort the set, or on the
      # sorted set to filter negative node values.
      # This is why this query is only executed when the previous one
      # did not find anything.
      result = Results(query(subquery('+1', '', 'node>0'), 0))
    return result

  def assignMessageList(self, db, state, uid_list):
    """
      Put messages back in given processing_node.
    """
    db.query(str2bytes("UPDATE %s SET processing_node=%s WHERE uid IN (%s)\0COMMIT" % (
      self.sql_table, state, ','.join(map(str, uid_list)))))

  def deleteMessageList(self, db, uid_list):
    db.query(str2bytes("DELETE FROM %s WHERE uid IN (%s)" % (
      self.sql_table, ','.join(map(str, uid_list)))))

  def reactivateMessageList(self, db, uid_list, delay, retry):
    db.query(str2bytes("UPDATE %s SET"
      " date = DATE_ADD(UTC_TIMESTAMP(6), INTERVAL %s SECOND)"
      "%s WHERE uid IN (%s)" % (
        self.sql_table, delay,
        ", retry = retry + 1" if retry else "",
        ",".join(map(str, uid_list)))))

  # Required for tests
  def timeShift(self, activity_tool, delay, processing_node=None):
    """
      To simulate time shift, we simply substract delay from
      all dates in message(_queue) table
    """
    activity_tool.getSQLConnection().query(str2bytes("UPDATE %s SET"
      " date = DATE_SUB(date, INTERVAL %s SECOND)"
      % (self.sql_table, delay)
      + ('' if processing_node is None else
         "WHERE processing_node=%s" % processing_node)))

  def createTableSQL(self):
    return """\
CREATE TABLE %s (
  `uid` BIGINT UNSIGNED NOT NULL,
  `date` DATETIME(6) NOT NULL,
  `path` VARCHAR(255) NOT NULL,
  `active_process_uid` BIGINT UNSIGNED NULL,
  `method_id` VARCHAR(255) NOT NULL,
  `processing_node` SMALLINT NOT NULL DEFAULT -1,
  `priority` TINYINT NOT NULL DEFAULT 0,
  `node` SMALLINT NOT NULL DEFAULT 0,
  `group_method_id` VARCHAR(255) NOT NULL DEFAULT '',
  `tag` VARCHAR(255) NOT NULL,
  `serialization_tag` VARCHAR(255) NOT NULL,
  `retry` TINYINT UNSIGNED NOT NULL DEFAULT 0,
  `message` LONGBLOB NOT NULL,
  PRIMARY KEY (`uid`),
  KEY `processing_node_priority_date` (`processing_node`, `priority`, `date`),
  KEY `node2_priority_date` (`processing_node`, `node`, `priority`, `date`),
  KEY `node_group_priority_date` (`processing_node`, `group_method_id`, `priority`, `date`),
  KEY `node2_group_priority_date` (`processing_node`, `node`, `group_method_id`, `priority`, `date`),
  KEY `serialization_tag_processing_node` (`serialization_tag`, `processing_node`),
  KEY (`path`, `processing_node`),
  KEY (`active_process_uid`),
  KEY (`method_id`, `processing_node`),
  KEY (`tag`, `processing_node`)
) ENGINE=InnoDB""" % self.sql_table
