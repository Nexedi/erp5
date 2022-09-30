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

from six import string_types as basestring
from six.moves import xrange
from Products.ERP5Type.Utils import bytes2str, ensure_list, str2bytes
from collections import defaultdict
from contextlib import contextmanager
from itertools import product, chain
import operator
import sys
import transaction
from random import getrandbits
import MySQLdb
from MySQLdb.constants.ER import DUP_ENTRY
from DateTime import DateTime
from Shared.DC.ZRDB.Results import Results
from zLOG import LOG, TRACE, INFO, WARNING, ERROR, PANIC
from ZODB.POSException import ConflictError
from Products.CMFActivity.ActivityTool import (
  Message, MESSAGE_NOT_EXECUTED, MESSAGE_EXECUTED, SkippedMessage)
from Products.CMFActivity.ActivityRuntimeEnvironment import (
  DEFAULT_MAX_RETRY, ActivityRuntimeEnvironment)
from .Queue import Queue, VALIDATION_ERROR_DELAY
from Products.CMFActivity.Errors import ActivityFlushError
from Products.ERP5Type import Timeout
from Products.ERP5Type.Timeout import Deadline
import six

# Stop validating more messages when this limit is reached
MAX_VALIDATED_LIMIT = 1000
# Read this many messages to validate.
READ_MESSAGE_LIMIT = 1000
INVOKE_ERROR_STATE = -2
DEPENDENCY_IGNORED_ERROR_STATE = -10
# Activity uids are stored as 64 bits unsigned integers.
# No need to depend on a database that supports unsigned integers.
# Numbers are far big enough without using the MSb. Assuming a busy activity
# table having one million activities, the probability of triggering a conflict
# when inserting one activity with 64 bits uid is 0.5e-13. With 63 bits it
# increases to 1e-13, which is still very low.
UID_SAFE_BITSIZE = 63
# Inserting an activity batch of 100 activities among one million existing
# activities has a probability of failing of 1e-11. While it should be low
# enough, retries can help lower that. Try 10 times, which should be short
# enough while yielding one order of magnitude collision probability
# improvement.
UID_ALLOCATION_TRY_COUNT = 10
# Limit the number of UNION-joined subqueries per query when looking for
# blocking activities. Used to take a slice from a list.
# XXX: 5000 is known to work on a case on "after_tag" dependency, which fails
# at 5400 with:
#   ProgrammingError: (1064, "memory exhausted near [...]")
_MAX_DEPENDENCY_UNION_SUBQUERY_COUNT = -5000

def sort_message_key(message):
  # same sort key as in SQLBase.getMessageList
  return message.line.priority, message.line.date, message.uid

class _DequeueMessageException(Exception):
  pass

_ITEMGETTER0 = operator.itemgetter(0)
_IDENTITY = lambda x: x

def render_datetime(x):
  return "%.4d-%.2d-%.2d %.2d:%.2d:%09.6f" % x.toZone('UTC').parts()[:6]

if six.PY2:
  _SQLTEST_NO_QUOTE_TYPE_SET = int, float, long
else:
  _SQLTEST_NO_QUOTE_TYPE_SET = int, float
_SQLTEST_NON_SEQUENCE_TYPE_SET = _SQLTEST_NO_QUOTE_TYPE_SET + (DateTime, basestring)

@contextmanager
def SQLLock(db, lock_name, timeout):
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
# sqltest_dict ({'condition_name': <render_function>}) defines how to render
# condition statements in the SQL query used by SQLBase.getMessageList
def sqltest_dict():
  sqltest_dict = {}
  def _(name, column=None, op="="):
    if column is None:
      column = name
    column_op = str2bytes(("%s %s " % (column, op)))
    def render(value, render_string):
      if isinstance(value, _SQLTEST_NO_QUOTE_TYPE_SET):
        return column_op + str2bytes(str(value))
      if isinstance(value, DateTime):
        value = render_datetime(value)
      if isinstance(value, basestring):
        return column_op + render_string(value)
      assert op == "=", value
      if value is None: # XXX: see comment in SQLBase._getMessageList
        return column + b" IS NULL"
      for x in value:
        return b"%s IN (%s)" % (column, str2bytes(', '.join(map(
          str if isinstance(x, _SQLTEST_NO_QUOTE_TYPE_SET) else
          render_datetime if isinstance(x, DateTime) else
          render_string, value))))
      return b"0"
    sqltest_dict[name] = render
  _('active_process_uid')
  _('group_method_id')
  _('method_id')
  _('path')
  _('processing_node')
  _('serialization_tag')
  _('tag')
  _('retry')
  _('to_date', column="date", op="<=")
  _('uid')
  def renderAbovePriorityDateUid(value, render_string):
    # Strictly dependent on _getMessageList's sort order: given a well-ordered
    # list of values, rendered condition will match the immediate next row in
    # that sort order.
    priority, date, uid = value
    assert isinstance(priority, _SQLTEST_NO_QUOTE_TYPE_SET)
    assert isinstance(uid, _SQLTEST_NO_QUOTE_TYPE_SET)
    return (
        b'(priority>%(priority)d OR (priority=%(priority)d AND '
        b'(date>%(date)s OR (date=%(date)s AND uid>%(uid)d))'
        b'))' % {
        b'priority': priority,
        # render_datetime raises if "date" lacks date API, so no need to check
        b'date': render_string(render_datetime(date)),
        b'uid': uid,
      }
    )
  sqltest_dict['above_priority_date_uid'] = renderAbovePriorityDateUid
  return sqltest_dict
sqltest_dict = sqltest_dict()

def _validate_after_path_and_method_id(value, render_string):
  path, method_id = value
  return (
    sqltest_dict['method_id'](method_id, render_string) +
    b' AND ' +
    sqltest_dict['path'](path, render_string)
  )

def _validate_after_tag_and_method_id(value, render_string):
  tag, method_id = value
  return (
    sqltest_dict['method_id'](method_id, render_string) +
    b' AND ' +
    sqltest_dict['tag'](tag, render_string)
  )

# Definition of activity dependencies
# key: dependency name (as passed to ActiveObject.activate() & friends)
# value:
# - tuple of column names. If there is more than one, they must be in the
#   same order as the dependency value items expected by the next item
# - callable rendering given values into an SQL condition
#   (value, render_string) -> str
# - minimal applicable processing_node value (excluded)
_DEPENDENCY_TESTER_DICT = {
  'after_method_id': (
    ('method_id', ),
    sqltest_dict['method_id'],
    DEPENDENCY_IGNORED_ERROR_STATE,
  ),
  'after_path': (
    ('path', ),
    sqltest_dict['path'],
    DEPENDENCY_IGNORED_ERROR_STATE,
  ),
  'after_message_uid': (
    ('uid', ),
    sqltest_dict['uid'],
    DEPENDENCY_IGNORED_ERROR_STATE,
  ),
  'after_path_and_method_id': (
    ('path', 'method_id'),
    _validate_after_path_and_method_id,
    DEPENDENCY_IGNORED_ERROR_STATE,
  ),
  'after_tag': (
    ('tag', ),
    sqltest_dict['tag'],
    DEPENDENCY_IGNORED_ERROR_STATE,
  ),
  'after_tag_and_method_id': (
    ('tag', 'method_id'),
    _validate_after_tag_and_method_id,
    DEPENDENCY_IGNORED_ERROR_STATE,
  ),
  'serialization_tag': (
    ('serialization_tag', ),
    sqltest_dict['serialization_tag'],
    -1,
  ),
}

def getNow(db):
  """
    Return the UTC date from the point of view of the SQL server.
    Note that this value is not cached, and is not transactionnal on MySQL
    side.
  """
  return db.query("SELECT UTC_TIMESTAMP(6)", 0)[1][0][0]

class SQLBase(Queue):
  """
    Define a set of common methods for SQL-based storage of activities.
  """
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

  def initialize(self, activity_tool, clear):
    db = activity_tool.getSQLConnection()
    create = self.createTableSQL()
    if clear:
      db.query("DROP TABLE IF EXISTS " + self.sql_table)
      db.query(create)
    else:
      src = db.upgradeSchema(create, create_if_not_exists=1,
                                     initialize=self._initialize)
      if src:
        LOG('CMFActivity', INFO, "%r table upgraded\n%s"
            % (self.sql_table, src))
    self._insert_max_payload = (db.getMaxAllowedPacket()
      + len(self._insert_separator)
      - len(self._insert_template % (str2bytes(self.sql_table), b'')))

  def _initialize(self, db, column_list):
      LOG('CMFActivity', ERROR, "Non-empty %r table upgraded."
          " The following added columns could not be initialized: %s"
          % (self.sql_table, ", ".join(column_list)))

  _insert_template = (b"INSERT INTO %s (uid,"
    b" path, active_process_uid, date, method_id, processing_node,"
    b" priority, node, group_method_id, tag, serialization_tag,"
    b" message) VALUES\n(%s)")
  _insert_separator = b"),\n("

  def _hasDependency(self, message):
    get = message.activity_kw.get
    return any(
      get(x) is not None
      for x in _DEPENDENCY_TESTER_DICT
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

  def _getMessageList(self, db, count=1000, src__=0, **kw):
    # XXX: Because most columns have NOT NULL constraint, conditions with None
    #      value should be ignored, instead of trying to render them
    #      (with comparisons with NULL).
    q = db.string_literal
    sql = b'\n  AND '.join(sqltest_dict[k](v, q) for k, v in six.iteritems(kw))
    sql = b"SELECT * FROM %s%s\nORDER BY priority, date, uid%s" % (
      str2bytes(self.sql_table),
      sql and b'\nWHERE ' + sql,
      b'' if count is None else b'\nLIMIT %d' % count,
    )
    return sql if src__ else Results(db.query(sql, max_rows=0))

  def getMessageList(self, activity_tool, *args, **kw):
    result = self._getMessageList(activity_tool.getSQLConnection(), *args, **kw)
    if type(result) is str: # src__ == 1
      return result,
    class_name = self.__class__.__name__
    return [Message.load(line.message,
                             activity=class_name,
                             uid=line.uid,
                             processing_node=line.processing_node,
                             retry=line.retry)
      for line in result]

  def countMessageSQL(self, quote, **kw):
    return b"SELECT count(*) FROM %s WHERE processing_node > %d AND %s" % (
      str2bytes(self.sql_table), DEPENDENCY_IGNORED_ERROR_STATE, b" AND ".join(
        sqltest_dict[k](v, quote) for (k, v) in six.iteritems(kw) if v
        ) or b"1")

  def hasActivitySQL(self, quote, only_valid=False, only_invalid=False, **kw):
    where = [sqltest_dict[k](v, quote) for (k, v) in six.iteritems(kw) if v]
    if only_valid:
      where.append(b'processing_node > %d' % INVOKE_ERROR_STATE)
    if only_invalid:
      where.append(b'processing_node <= %d' % INVOKE_ERROR_STATE)
    return b"SELECT 1 FROM %s WHERE %s LIMIT 1" % (
      str2bytes(self.sql_table), b" AND ".join(where) or b"1")

  def getPriority(self, activity_tool, processing_node, node_set=None):
    query = activity_tool.getSQLConnection().query
    if node_set is None:
      result = query(
        b"SELECT 3*priority, date"
        b" FROM %s"
        b" WHERE"
        b"  processing_node=0 AND"
        b"  date <= UTC_TIMESTAMP(6)"
        b" ORDER BY priority, date"
        b" LIMIT 1" % str2bytes(self.sql_table),
        0,
      )[1]
    else:
      subquery = lambda *a, **k: str2bytes(bytes2str(b"("
        b"SELECT 3*priority{} AS effective_priority, date"
        b" FROM %s"
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
                subquery('-1', 'node = %i' % processing_node),
                subquery('', 'node=0'),
              ),
              (
                subquery('-1', 'node = %i' % x)
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
        result = query(subquery('+1', 'node>0'), 0)[1]
    if result:
      return result[0]
    return Queue.getPriority(self, activity_tool, processing_node, node_set)

  def _retryOnLockError(self, method, args=(), kw={}):
    while True:
      try:
        return method(*args, **kw)
      except ConflictError:
        # Note that this code assumes that a database adapter translates
        # a lock error into a conflict error.
        LOG('SQLBase', INFO, 'Got a lock error, retrying...')

  def _log(self, severity, summary):
    LOG(self.__class__.__name__, severity, summary,
        error=severity > INFO)

  def _getExecutableMessageSet(self, activity_tool, db, message_list):
    """
    Return, from given message list, the set of messages which have all their
    dependencies satisfied.
    """
    # Principle of operation:
    # For each dependency type used in given message list, find all messages
    # matching any of the dependency values used in given message list.
    # This provides the SQL database with structurally simple queries that it
    # should be able to optimise easily.
    # Further refinements:
    # - Any blocked message is ignored in further dendency type lookups (we
    #   already know it is blocked, no point in checking further).
    # - Test the most popular dependency types first, with the expectation
    #   that these will find most of the blockers, reducing the set of
    #   activities left to test and (with the refinement above) reducing the
    #   probability of having to run further queries (if there are other
    #   dependency types to test)
    dependency_tester_dict = _DEPENDENCY_TESTER_DICT
    # dependency_name (str): Something like 'serialization_tag', etc
    # dependency_value (any): dependency_name-dependent structure and meaning.
    # dependency_dict: define the dependencies to check, and which messages are
    # blocked by each found blocker.
    #   [dependency_name][dependency_value] -> message set
    dependency_dict = defaultdict(lambda: defaultdict(set))
    # message_dependency_dict: define which message has which dependencies, to
    # efficiently remove a message from dependency_dict once it is found to be
    # blocked.
    #   [message][dependency_name] -> dependency_value
    message_dependency_dict = defaultdict(dict)
    for message in message_list:
      for (
        dependency_name,
        dependency_value,
      ) in six.iteritems(message.activity_kw):
        try:
          column_list, _, _ = dependency_tester_dict[dependency_name]
        except KeyError:
          continue
        # There are 2 types of dependencies:
        # - monovalued (most), which accepts a single value and a vector of
        #   values.
        # - n-valued (after_path_and_method_id and after_tag_and_method_id)
        #   which accept a n-vector, each item being a single value or a vector
        #   of values.
        # Convert every form into its vector equivalent form, ignoring
        # conditions which cannot match any activity, and (for n-valued)
        # enumerate all possible combinations for later reverse-lookup.
        column_count = len(column_list)
        if column_count == 1:
          if dependency_value is None:
            continue
          dependency_value_list = [
            x
            for x in (
              (dependency_value, )
              if isinstance(
                dependency_value,
                _SQLTEST_NON_SEQUENCE_TYPE_SET,
              ) else
              dependency_value
            )
            # None values cannot match any activity, ignore them.
            if x is not None
          ]
        else:
          try:
            if (
              len(dependency_value) != column_count or
              None in dependency_value
            ):
              # Malformed or impossible to match dependency, ignore.
              continue
          except TypeError:
            # Malformed dependency, ignore.
            continue
          # Note: it any resulting item ends up empty (ex: it only contained
          # None), product will return an empty list.
          dependency_value_list = list(product(*(
            (
              (dependency_column_value, )
              if isinstance(
                dependency_column_value,
                _SQLTEST_NON_SEQUENCE_TYPE_SET,
              ) else
              (x for x in dependency_column_value if x is not None)
            )
            for dependency_column_value in dependency_value
          )))
        if not dependency_value_list:
          continue
        message_dependency_dict[message][dependency_name] = dependency_value_list
        dependency_value_dict = dependency_dict[dependency_name]
        for dependency_value in dependency_value_list:
          dependency_value_dict[dependency_value].add(message)
    # Messages are supposed valid until blockage is found.
    result = set(message_list)
    # Messages for which a blockage is found, so removal of this message from
    # further dependency processing is delayed to the next iteration, to avoid
    # doing such work if there is no such further iteration.
    new_blocked_message_set = set()
    quote = db.string_literal
    table_name_list = activity_tool.getSQLTableNameSet()
    for (
      dependency_name,
      dependency_value_dict,
    ) in sorted(
      six.iteritems(dependency_dict),
      # Test first the condition with the most values.
      # XXX: after_path=('foo', 'bar') counts as 2 points for after_path
      # despite being a single activity. Is there a fairer (while cheap) way ?
      key=lambda dependency_dict_item: sum(
        len(message_set)
        for message_set in six.itervalues(dependency_dict_item[1])
      ),
      reverse=True,
    ):
      # Previous iteration found blocked messages.
      # Find which activities, and remove their values from dependency_dict
      # so these activities are not tested in further queries (we already
      # know they are blocked).
      while new_blocked_message_set:
        blocked_message = new_blocked_message_set.pop()
        for (
          message_dependency_name,
          message_dependency_value_list,
        ) in six.iteritems(message_dependency_dict[blocked_message]):
          message_dependency_value_dict = dependency_dict[message_dependency_name]
          if not message_dependency_value_dict:
            # This dependency was already dropped or evaluated, nothing to
            # cleanup here.
            continue
          for message_dependency_value in message_dependency_value_list:
            message_set = message_dependency_value_dict[message_dependency_value]
            message_set.remove(blocked_message)
            if not message_set:
              # No more message wait for this value for this dependency, drop
              # the entry.
              del message_dependency_value_dict[message_dependency_value]
          # Note: no point in editing dependency_dict if
          # message_dependency_value_dict is empty, the outer loop is working
          # on a copy.
      if not dependency_value_dict:
        # No more non-blocked message for this dependency, skip it.
        continue
      column_list, to_sql, min_processing_node = dependency_tester_dict[
        dependency_name
      ]
      row2key = (
        _ITEMGETTER0
        if len(column_list) == 1 else
        _IDENTITY
      )
      base_sql_suffix = b' WHERE processing_node > %i AND (%%s) LIMIT 1)' % (
        min_processing_node,
      )
      sql_suffix_list = [
        base_sql_suffix % to_sql(dependency_value, quote)
        for dependency_value in dependency_value_dict
      ]
      base_sql_prefix = b'(SELECT %s FROM ' % (
        b','.join([ str2bytes(c) for c in column_list ]),
      )
      subquery_list = [
        base_sql_prefix + str2bytes(table_name) + sql_suffix
        for table_name in table_name_list
        for sql_suffix in sql_suffix_list
      ]
      while subquery_list:
        # Join queries with a UNION, to reduce per-query latency.
        # Also, limit the number of subqueries per query, as their number can
        # largely exceed the number of activities being considered multiplied
        # by the number of activty tables: it is also proportional to the
        # number of distinct values being looked for in the current column.
        for row in db.query(
          b' UNION '.join(subquery_list[_MAX_DEPENDENCY_UNION_SUBQUERY_COUNT:]),
          max_rows=0,
        )[1]:
          # Each row is a value which blocks some activities.
          dependent_message_set = dependency_value_dict[row2key(row)]
          # queue blocked messages for processing in the beginning of next
          # outermost iteration.
          new_blocked_message_set |= dependent_message_set
          # ...but update result immediately, in case there is no next
          # outermost iteration.
          result -= dependent_message_set
        del subquery_list[_MAX_DEPENDENCY_UNION_SUBQUERY_COUNT:]
      dependency_value_dict.clear()
    return result

  def distribute(self, activity_tool, node_count):
    db = activity_tool.getSQLConnection()
    where_kw = {
      'processing_node': -1,
      'to_date': getNow(db),
      'count': READ_MESSAGE_LIMIT,
    }
    validated_count = 0
    while 1:
      result = self._getMessageList(db, **where_kw)
      if not result:
        transaction.commit()
        return False
      message_list = [Message.load(line.message, uid=line.uid, line=line)
                      for line in result]
      message_set = self._getExecutableMessageSet(activity_tool, db, message_list)
      transaction.commit()
      if message_set:
        distributable_uid_set = set()
        serialization_tag_dict = {}
        for message in message_set:
          serialization_tag = message.activity_kw.get('serialization_tag')
          if serialization_tag is None:
            distributable_uid_set.add(message.uid)
          else:
            serialization_tag_dict.setdefault(serialization_tag,
                                              []).append(message)
        for message_list in six.itervalues(serialization_tag_dict):
          # Sort list of messages to validate the message with highest score
          message_list.sort(key=sort_message_key)
          distributable_uid_set.add(message_list[0].uid)
          group_method_id = message_list[0].line.group_method_id
          if group_method_id == '\0':
            continue
          for message in message_list[1:]:
            if group_method_id == message.line.group_method_id:
              distributable_uid_set.add(message.uid)
        distributable_count = len(distributable_uid_set)
        if distributable_count:
          self.assignMessageList(db, 0, distributable_uid_set)
          validated_count += distributable_count
          if validated_count >= MAX_VALIDATED_LIMIT:
            transaction.commit()
            return True
      line = result[-1]
      where_kw['above_priority_date_uid'] = (line.priority, line.date, line.uid)

  def getReservedMessageList(self, db, date, processing_node, limit,
                             group_method_id=None, node_set=None):
    """
      Get and reserve a list of messages.
      limit
        Maximum number of messages to fetch.
        This number is not garanted to be reached, because of not enough
        messages being pending execution.
    """
    assert limit
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
    )

    # Note: Not all write accesses to our table are protected by this lock.
    # This lock is not here for data consistency reasons, but to avoid wasting
    # time on SQL deadlocks caused by the varied lock ordering chosen by the
    # database. These queries specifically seem to be extremely prone to such
    # deadlocks, so prevent them from attempting to run in parallel on a given
    # activity table.
    # If more accesses are found to cause a significant waste of time because
    # of deadlocks, then they should acquire such lock as well. But
    # preemptively applying such lock everywhere without checking the amount
    # of waste is unlikely to produce a net gain.
    # XXX: timeout may benefit from being tweaked, but one second seem like a
    # reasonable starting point.
    # XXX: locking could probably be skipped altogether on clusters with few
    # enough processing nodes, as there should be little deadlocks and the
    # tradeoff becomes unfavorable to explicit locks. What threshold to
    # choose ?
    with SQLLock(db, self.sql_table, timeout=1) as acquired:
      if not acquired:
        # This table is busy, check for work to do elsewhere
        return ()
      # Get reservable messages.
      # During normal operation, sorting by date (as last criteria) is fairer
      # for users and reduce the probability to do the same work several times
      # (think of an object that is modified several times in a short period of
      # time).
      if node_set is None:
        result = Results(query(
          b"SELECT *"
          b" FROM %s"
          b" WHERE"
          b"  processing_node=0 AND"
          b"  %s%s"
          b" ORDER BY priority, date"
          b" LIMIT %i"
          b" FOR UPDATE" % args,
          0,
        ))
      else:
        subquery = lambda *a, **k: str2bytes(bytes2str(b"("
          b"SELECT *, 3*priority{} AS effective_priority"
          b" FROM %s"
          b" WHERE"
          b"  {} AND"
          b"  processing_node=0 AND"
          b"  %s%s"
          b" ORDER BY priority, date"
          b" LIMIT %i"
        b")" % args).format(*a, *k))
        result = Results(query(
          b"SELECT *"
          b" FROM (%s) AS t"
          b" ORDER BY effective_priority, date"
          b" LIMIT %i" % (
            b" UNION ALL ".join(
              chain(
                (
                  subquery('-1', 'node = %i' % processing_node),
                  subquery('', 'node=0'),
                ),
                (
                  subquery('-1', 'node = %i' % x)
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
          result = Results(query(subquery('+1', 'node>0'), 0))
      if result:
        # Reserve messages.
        uid_list = [x.uid for x in result]
        self.assignMessageList(db, processing_node, uid_list)
        self._log(TRACE, 'Reserved messages: %r' % uid_list)
        return result
    return ()

  def assignMessageList(self, db, state, uid_list):
    """
      Put messages back in given processing_node.
    """
    db.query("UPDATE %s SET processing_node=%s WHERE uid IN (%s)\0COMMIT" % (
      self.sql_table, state, ','.join(map(str, uid_list))))

  def getProcessableMessageLoader(self, db, processing_node):
    # do not merge anything
    def load(line):
      uid = line.uid
      m = Message.load(line.message, uid=uid, line=line)
      return m, uid, ()
    return load

  def getProcessableMessageList(self, activity_tool, processing_node,
                                node_family_id_list):
    """
      Always true:
        For each reserved message, delete redundant messages when it gets
        reserved (definitely lost, but they are expandable since redundant).

      - reserve a message
      - if this message has a group_method_id:
        - reserve a bunch of messages
        - until the total "cost" of the group goes over 1
          - get one message from the reserved bunch (this messages will be
            "needed")
          - update the total cost
        - unreserve "unneeded" messages
      - return still-reserved message list and a group_method_id

      If any error happens in above described process, try to unreserve all
      messages already reserved in that process.
      If it fails, complain loudly that some messages might still be in an
      unclean state.

      Returned values:
        4-tuple:
          - list of messages
          - group_method_id
          - uid_to_duplicate_uid_list_dict
    """
    db = activity_tool.getSQLConnection()
    now_date = getNow(db)
    uid_to_duplicate_uid_list_dict = {}
    try:
      while 1: # not a loop
        # Select messages that were either assigned manually or left
        # unprocessed after a shutdown. Most of the time, there's none.
        # To minimize the probability of deadlocks, we also COMMIT so that a
        # new transaction starts on the first 'FOR UPDATE' query, which is all
        # the more important as the current on started with getPriority().
        result = db.query(b"SELECT * FROM %s WHERE processing_node=%d"
          b" ORDER BY priority, date LIMIT 1\0COMMIT" % (
          str2bytes(self.sql_table), processing_node), 0)
        already_assigned = result[1]
        if already_assigned:
          result = Results(result)
        else:
          result = self.getReservedMessageList(db, now_date, processing_node,
                                               1, node_set=node_family_id_list)
          if not result:
            break
          # So reserved documents are properly released even if load raises.
          for line in result:
            uid_to_duplicate_uid_list_dict[line.uid] = []
        load = self.getProcessableMessageLoader(db, processing_node)
        m, uid, uid_list = load(result[0])
        message_list = [m]
        uid_to_duplicate_uid_list_dict[uid] = uid_list
        group_method_id = m.line.group_method_id
        if group_method_id[0] != '\0':
          # Count the number of objects to prevent too many objects.
          cost = m.getGroupMethodCost()
          assert 0 < cost <= 1, (self.sql_table, uid)
          count = m.getObjectCount(activity_tool)
          # this is heuristic (messages with same group_method_id
          # are likely to have the same group_method_cost)
          limit = int(1. / cost + 1 - count)
          if limit > 1: # <=> cost * count < 1
            cost *= count
            # Retrieve objects which have the same group method.
            result = iter(already_assigned
              and Results(db.query(b"SELECT * FROM %s"
                b" WHERE processing_node=%d AND group_method_id=%s"
                b" ORDER BY priority, date LIMIT %d" % (
                str2bytes(self.sql_table), processing_node,
                db.string_literal(group_method_id), limit), 0))
                # Do not optimize rare case: keep the code simple by not
                # adding more results from getReservedMessageList if the
                # limit is not reached.
              or self.getReservedMessageList(db, now_date, processing_node,
                limit, group_method_id, node_family_id_list))
            for line in result:
              if line.uid in uid_to_duplicate_uid_list_dict:
                continue
              m, uid, uid_list = load(line)
              if m is None:
                uid_to_duplicate_uid_list_dict[uid] += uid_list
                continue
              uid_to_duplicate_uid_list_dict[uid] = uid_list
              cost += m.getObjectCount(activity_tool) * \
                      m.getGroupMethodCost()
              message_list.append(m)
              if cost >= 1:
                # Unreserve extra messages as soon as possible.
                uid_list = [line.uid for line in result if line.uid != uid]
                if uid_list:
                  self.assignMessageList(db, 0, uid_list)
        return message_list, group_method_id, uid_to_duplicate_uid_list_dict
    except:
      self._log(WARNING, 'Exception while reserving messages.')
      if uid_to_duplicate_uid_list_dict:
        to_free_uid_list = ensure_list(uid_to_duplicate_uid_list_dict.keys())
        for uid_list in six.itervalues(uid_to_duplicate_uid_list_dict):
          to_free_uid_list += uid_list
        try:
          self.assignMessageList(db, 0, to_free_uid_list)
        except:
          self._log(ERROR, 'Failed to free messages: %r' % to_free_uid_list)
        else:
          if to_free_uid_list:
            self._log(TRACE, 'Freed messages %r' % to_free_uid_list)
      else:
        self._log(TRACE, '(no message was reserved)')
    return (), None, None

  def _abort(self):
    try:
      transaction.abort()
    except:
      # Unfortunately, database adapters may raise an exception against abort.
      self._log(PANIC,
          'abort failed, thus some objects may be modified accidentally')
      raise

  # Queue semantic
  def dequeueMessage(self, activity_tool, processing_node,
                     node_family_id_list):
    message_list, group_method_id, uid_to_duplicate_uid_list_dict = \
      self.getProcessableMessageList(activity_tool, processing_node,
        node_family_id_list)
    if message_list:
      # Remove group_id parameter from group_method_id
      group_method_id = group_method_id.split('\0')[0]
      if group_method_id != "":
        method = activity_tool.invokeGroup
        args = (group_method_id, message_list, self.__class__.__name__,
                hasattr(self, 'generateMessageUID'))
        activity_runtime_environment = ActivityRuntimeEnvironment(
          None,
          priority=min(x.line.priority for x in message_list),
        )
      else:
        method = activity_tool.invoke
        message, = message_list
        args = message_list
        activity_runtime_environment = ActivityRuntimeEnvironment(message)
      # Commit right before executing messages.
      # As MySQL transaction does not start exactly at the same time as ZODB
      # transactions but a bit later, messages available might be called
      # on objects which are not available - or available in an old
      # version - to ZODB connector.
      # So all connectors must be committed now that we have selected
      # everything needed from MySQL to get a fresh view of ZODB objects.
      transaction.commit()
      transaction.begin()
      # Try to invoke
      try:
        # Refer Timeout.activity_timeout instead of
        #   from Products.ERP5Type.Timeout import activity_timeout
        # so that we can override the value in Timeout namescope in unit tests.
        offset = Timeout.activity_timeout
        with activity_runtime_environment, Deadline(offset):
          method(*args)
        # Abort if at least 1 message failed. On next tic, only those that
        # succeeded will be selected because their at_date won't have been
        # increased.
        for m in message_list:
          if m.getExecutionState() == MESSAGE_NOT_EXECUTED:
            raise _DequeueMessageException()
        transaction.commit()
      except:
        exc_info = sys.exc_info()
        if not isinstance(exc_info[1], _DequeueMessageException):
          self._log(WARNING,
            'Exception raised when invoking messages (uid, path, method_id) %r'
            % [(m.uid, m.object_path, m.method_id) for m in message_list])
          for m in message_list:
            m.setExecutionState(MESSAGE_NOT_EXECUTED, exc_info, log=False)
        self._abort()
        exc_info = message_list[0].exc_info
        if exc_info:
          try:
            # Register it again.
            with activity_runtime_environment:
              cancel = message.on_error_callback(*exc_info)
            del exc_info, message.exc_info
            transaction.commit()
            if cancel:
              message.setExecutionState(MESSAGE_EXECUTED)
          except:
            self._log(WARNING, 'Exception raised when processing error callbacks')
            message.setExecutionState(MESSAGE_NOT_EXECUTED)
            self._abort()
      self.finalizeMessageExecution(activity_tool, message_list,
                                    uid_to_duplicate_uid_list_dict)
    transaction.commit()
    return bool(message_list)

  def deleteMessageList(self, db, uid_list):
    db.query("DELETE FROM %s WHERE uid IN (%s)" % (
      self.sql_table, ','.join(map(str, uid_list))))

  def reactivateMessageList(self, db, uid_list, delay, retry):
    db.query("UPDATE %s SET"
      " date = DATE_ADD(UTC_TIMESTAMP(6), INTERVAL %s SECOND)"
      "%s WHERE uid IN (%s)" % (
        self.sql_table, delay,
        ", retry = retry + 1" if retry else "",
        ",".join(map(str, uid_list))))

  def finalizeMessageExecution(self, activity_tool, message_list,
                               uid_to_duplicate_uid_list_dict=None):
    """
      If everything was fine, delete all messages.
      If anything failed, make successful messages available (if any), and
      the following rules apply to failed messages:
        - Failures due to ConflictErrors cause messages to be postponed,
          but their retry count is *not* increased.
        - Failures of messages already above maximum retry count cause them to
          be put in a permanent-error state.
        - In all other cases, retry count is increased and message is delayed.
    """
    db = activity_tool.getSQLConnection()
    deletable_uid_list = []
    delay_uid_list = []
    final_error_uid_list = []
    make_available_uid_list = []
    notify_user_list = []
    executed_uid_list = deletable_uid_list
    if uid_to_duplicate_uid_list_dict is not None:
      for m in message_list:
        if m.getExecutionState() == MESSAGE_NOT_EXECUTED:
          executed_uid_list = make_available_uid_list
          break
    for m in message_list:
      uid = m.uid
      if m.getExecutionState() == MESSAGE_EXECUTED:
        executed_uid_list.append(uid)
        if uid_to_duplicate_uid_list_dict is not None:
          executed_uid_list += uid_to_duplicate_uid_list_dict.get(uid, ())
      elif m.getExecutionState() == MESSAGE_NOT_EXECUTED:
        # Should duplicate messages follow strictly the original message, or
        # should they be just made available again ?
        if uid_to_duplicate_uid_list_dict is not None:
          make_available_uid_list += uid_to_duplicate_uid_list_dict.get(uid, ())
        if (m.exc_type and # m.exc_type may be None
            (m.conflict_retry if issubclass(m.exc_type, ConflictError) else
             m.exc_type is SkippedMessage)):
          delay_uid_list.append(uid)
        else:
          max_retry = m.max_retry
          retry = m.line.retry
          if max_retry is not None and retry >= max_retry:
            # Always notify when we stop retrying.
            notify_user_list.append((m, False))
            final_error_uid_list.append(uid)
            continue
          # In case of infinite retry, notify the user
          # when the default limit is reached.
          if max_retry is None and retry == DEFAULT_MAX_RETRY:
            notify_user_list.append((m, True))
          delay = m.delay
          if delay is None:
            # By default, make delay quadratic to the number of retries.
            delay = VALIDATION_ERROR_DELAY * (retry * retry + 1) * 2
          try:
            # Immediately update, because values different for every message
            self.reactivateMessageList(db, (uid,), delay, True)
          except:
            self._log(WARNING, 'Failed to reactivate %r' % uid)
        make_available_uid_list.append(uid)
      else: # MESSAGE_NOT_EXECUTABLE
        # 'path' does not point to any object. Activities are normally flushed
        # (without invoking them) when an object is deleted, but this is only
        # an optimisation. There is no efficient and reliable way to do such
        # this, because a concurrent and very long transaction may be about to
        # activate this object, without conflict.
        # So we have to clean up any remaining activity.
        deletable_uid_list.append(uid)
    if deletable_uid_list:
      try:
        self._retryOnLockError(self.deleteMessageList, (db, deletable_uid_list))
      except:
        self._log(ERROR, 'Failed to delete messages %r' % deletable_uid_list)
      else:
        self._log(TRACE, 'Deleted messages %r' % deletable_uid_list)
    if delay_uid_list:
      try:
        # If this is a conflict error, do not increase 'retry' but only delay.
        self.reactivateMessageList(db, delay_uid_list,
                                   VALIDATION_ERROR_DELAY, False)
      except:
        self._log(ERROR, 'Failed to delay %r' % delay_uid_list)
    if final_error_uid_list:
      try:
        self.assignMessageList(db, INVOKE_ERROR_STATE, final_error_uid_list)
      except:
        self._log(ERROR, 'Failed to set message to error state for %r'
                         % final_error_uid_list)
    if make_available_uid_list:
      try:
        self.assignMessageList(db, 0, make_available_uid_list)
      except:
        self._log(ERROR, 'Failed to unreserve %r' % make_available_uid_list)
      else:
        self._log(TRACE, 'Freed messages %r' % make_available_uid_list)
    try:
      for m, retry in notify_user_list:
        m.notifyUser(activity_tool, retry)
    except:
      # Notification failures must not cause this method to raise.
      self._log(WARNING,
        'Exception during notification phase of finalizeMessageExecution')

  def flush(self, activity_tool, object_path, invoke=0, method_id=None, only_safe=False, **kw):
    """
      object_path is a tuple
    """
    db = activity_tool.getSQLConnection()
    path = '/'.join(object_path)
    if invoke:
      invoked = set()
      def invoke(message):
        try:
          key = self.generateMessageUID(message)
          if key in invoked:
            return
          invoked.add(key)
        except AttributeError:
          pass
        line = getattr(message, 'line', None)
        if (line and line.processing_node != -1 or
            self._getExecutableMessageSet(activity_tool, db, [message])):
          # Try to invoke the message - what happens if invoke calls flushActivity ??
          with ActivityRuntimeEnvironment(message):
            activity_tool.invoke(message)
          if message.getExecutionState() != MESSAGE_EXECUTED:
            raise ActivityFlushError('Could not invoke %s on %s'
                                     % (message.method_id, path))
        else:
          raise ActivityFlushError('Could not validate %s on %s'
                                   % (message.method_id, path))
    for m in activity_tool.getRegisteredMessageList(self):
      if object_path == m.object_path and (
         method_id is None or method_id == m.method_id):
        if invoke:
          invoke(m)
        activity_tool.unregisterMessage(self, m)
    uid_list = []
    for line in self._getMessageList(db, path=path,
        **({'method_id': method_id} if method_id else {})):
      if only_safe and line.processing_node > -2:
        continue
      uid_list.append(line.uid)
      if invoke and line.processing_node <= 0:
        invoke(Message.load(line.message, uid=line.uid, line=line))
    if uid_list:
      self.deleteMessageList(db, uid_list)

  # Required for tests
  def timeShift(self, activity_tool, delay, processing_node=None):
    """
      To simulate time shift, we simply substract delay from
      all dates in message(_queue) table
    """
    activity_tool.getSQLConnection().query("UPDATE %s SET"
      " date = DATE_SUB(date, INTERVAL %s SECOND)"
      % (self.sql_table, delay)
      + ('' if processing_node is None else
         "WHERE processing_node=%s" % processing_node))
