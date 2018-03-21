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

import sys
import transaction
from random import getrandbits
import MySQLdb
from MySQLdb.constants.ER import DUP_ENTRY
from DateTime import DateTime
from Shared.DC.ZRDB.Results import Results
from Shared.DC.ZRDB.DA import DatabaseError
from zLOG import LOG, TRACE, INFO, WARNING, ERROR, PANIC
from ZODB.POSException import ConflictError
from Products.CMFActivity.ActivityTool import (
  Message, MESSAGE_NOT_EXECUTED, MESSAGE_EXECUTED, SkippedMessage)
from Products.CMFActivity.ActivityRuntimeEnvironment import (
  DEFAULT_MAX_RETRY, ActivityRuntimeEnvironment)
from Queue import Queue, VALIDATION_ERROR_DELAY, VALID, INVALID_PATH
from Products.CMFActivity.Errors import ActivityFlushError

# Stop validating more messages when this limit is reached
MAX_VALIDATED_LIMIT = 1000
# Read this many messages to validate.
READ_MESSAGE_LIMIT = 1000
# TODO: Limit by size in bytes instead of number of rows.
MAX_MESSAGE_LIST_SIZE = 100
INVOKE_ERROR_STATE = -2
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

def sort_message_key(message):
  # same sort key as in SQLBase.getMessageList
  return message.line.priority, message.line.date, message.uid

_DequeueMessageException = Exception()

# sqltest_dict ({'condition_name': <render_function>}) defines how to render
# condition statements in the SQL query used by SQLBase.getMessageList
def sqltest_dict():
  sqltest_dict = {}
  no_quote_type = int, float, long
  def _(name, column=None, op="="):
    if column is None:
      column = name
    column_op = "%s %s " % (column, op)
    def render(value, render_string):
      if isinstance(value, no_quote_type):
        return column_op + str(value)
      if isinstance(value, DateTime):
        value = value.toZone('UTC').ISO()
      if isinstance(value, basestring):
        return column_op + render_string(value)
      assert op == "=", value
      if value is None: # XXX: see comment in SQLBase._getMessageList
        return column + " IS NULL"
      for x in value:
        if isinstance(x, no_quote_type):
          render_string = str
        elif isinstance(x, DateTime):
          value = (x.toZone('UTC').ISO() for x in value)
        return "%s IN (%s)" % (column, ', '.join(map(render_string, value)))
      return "0"
    sqltest_dict[name] = render
  _('active_process_uid')
  _('group_method_id')
  _('method_id')
  _('path')
  _('processing')
  _('processing_node')
  _('serialization_tag')
  _('tag')
  _('retry')
  _('to_date', column="date", op="<=")
  _('uid')
  return sqltest_dict
sqltest_dict = sqltest_dict()

class SQLBase(Queue):
  """
    Define a set of common methods for SQL-based storage of activities.
  """
  def initialize(self, activity_tool, clear):
    folder = activity_tool.getPortalObject().portal_skins.activity
    try:
      createMessageTable = folder.SQLBase_createMessageTable
    except AttributeError:
      return
    if clear:
      folder.SQLBase_dropMessageTable(table=self.sql_table)
      createMessageTable(table=self.sql_table)
    else:
      src = createMessageTable._upgradeSchema(create_if_not_exists=1,
                                              initialize=self._initialize,
                                              table=self.sql_table)
      if src:
        LOG('CMFActivity', INFO, "%r table upgraded\n%s"
            % (self.sql_table, src))

  def _initialize(self, db, column_list):
      LOG('CMFActivity', ERROR, "Non-empty %r table upgraded."
          " The following added columns could not be initialized: %s"
          % (self.sql_table, ", ".join(column_list)))

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
      serialization_tag_list = [m.activity_kw.get('serialization_tag', '')
                                for m in message_list]
      processing_node_list = []
      for m in message_list:
        m.order_validation_text = x = self.getOrderValidationText(m)
        processing_node_list.append(0 if x == 'none' else -1)
      for _ in xrange(UID_ALLOCATION_TRY_COUNT):
        try:
          portal.SQLBase_writeMessageList(
            table=self.sql_table,
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
            serialization_tag_list=serialization_tag_list)
        except MySQLdb.IntegrityError, (code, _):
          if code != DUP_ENTRY:
            raise
        else:
          break
      else:
        raise ValueError("Maximum retry for SQLBase_writeMessageList reached")

  def getNow(self, context):
    """
      Return the current value for SQL server's NOW().
      Note that this value is not cached, and is not transactionnal on MySQL
      side.
    """
    result = context.SQLBase_getNow()
    assert len(result) == 1
    assert len(result[0]) == 1
    return result[0][0]

  def _getMessageList(self, activity_tool, offset=0, count=1000, src__=0, **kw):
    # XXX: Because most columns have NOT NULL constraint, conditions with None
    #      value should be ignored, instead of trying to render them
    #      (with comparisons with NULL).
    sql_connection = activity_tool.getPortalObject().cmf_activity_sql_connection
    q = sql_connection.sql_quote__
    if offset:
      limit = '\nLIMIT %d,%d' % (offset, sys.maxint if count is None else count)
    else:
      limit = '' if count is None else '\nLIMIT %d' % count
    sql = '\n  AND '.join(sqltest_dict[k](v, q) for k, v in kw.iteritems())
    sql = "SELECT * FROM %s%s\nORDER BY priority, date, uid%s" % (
      self.sql_table, sql and '\nWHERE ' + sql, limit)
    return sql if src__ else Results(sql_connection().query(sql, max_rows=0))

  def getMessageList(self, *args, **kw):
    result = self._getMessageList(*args, **kw)
    if type(result) is str: # src__ == 1
      return result,
    class_name = self.__class__.__name__
    return [Message.load(line.message,
                             activity=class_name,
                             uid=line.uid,
                             processing_node=line.processing_node,
                             retry=line.retry,
                             processing=line.processing)
      for line in result]

  def countMessage(self, activity_tool, tag=None, path=None,
                   method_id=None, message_uid=None, **kw):
    """Return the number of messages which match the given parameters.
    """
    if isinstance(tag, str):
      tag = [tag]
    if isinstance(path, str):
      path = [path]
    if isinstance(method_id, str):
      method_id = [method_id]
    result = activity_tool.SQLBase_validateMessageList(table=self.sql_table,
                                                       method_id=method_id,
                                                       path=path,
                                                       message_uid=message_uid,
                                                       tag=tag,
                                                       serialization_tag=None,
                                                       count=1)
    return result[0].uid_count

  def hasActivity(self, activity_tool, object, method_id=None, only_valid=None,
                  active_process_uid=None,
                  only_invalid=False):
    hasMessage = getattr(activity_tool, 'SQLBase_hasMessage', None)
    if hasMessage is not None:
      if object is None:
        path = None
      else:
        path = '/'.join(object.getPhysicalPath())
      try:
        result = hasMessage(table=self.sql_table, path=path, method_id=method_id,
          only_valid=only_valid, active_process_uid=active_process_uid,
          only_invalid=only_invalid)
      except DatabaseError:
        LOG(
          'SQLBase',
          ERROR,
          '%r raised, considering there are no activities' % (
            hasMessage,
          ),
          error=True,
        )
      else:
        return result[0].message_count > 0
    return 0

  def getPriority(self, activity_tool):
    result = activity_tool.SQLBase_getPriority(table=self.sql_table)
    if result:
      result, = result
      return result['priority'], result['date']
    return Queue.getPriority(self, activity_tool)

  def _retryOnLockError(self, method, args=(), kw={}):
    while True:
      try:
        return method(*args, **kw)
      except ConflictError:
        # Note that this code assumes that a database adapter translates
        # a lock error into a conflict error.
        LOG('SQLBase', INFO, 'Got a lock error, retrying...')

  # Validation private methods
  def _validate(self, activity_tool, method_id=None, message_uid=None, path=None, tag=None,
                serialization_tag=None):
    if isinstance(method_id, str):
      method_id = [method_id]
    if isinstance(path, str):
      path = [path]
    if isinstance(tag, str):
      tag = [tag]

    if method_id or message_uid or path or tag or serialization_tag:
      result = activity_tool.SQLBase_validateMessageList(table=self.sql_table,
          method_id=method_id,
          message_uid=message_uid,
          path=path,
          tag=tag,
          count=False,
          serialization_tag=serialization_tag)
      message_list = []
      for line in result:
        m = Message.load(line.message,
                         line=line,
                         uid=line.uid,
                         date=line.date,
                         processing_node=line.processing_node)
        if not hasattr(m, 'order_validation_text'): # BBB
          m.order_validation_text = self.getOrderValidationText(m)
        message_list.append(m)
      return message_list

  def _validate_after_method_id(self, activity_tool, message, value):
    return self._validate(activity_tool, method_id=value)

  def _validate_after_path(self, activity_tool, message, value):
    return self._validate(activity_tool, path=value)

  def _validate_after_message_uid(self, activity_tool, message, value):
    return self._validate(activity_tool, message_uid=value)

  def _validate_after_path_and_method_id(self, activity_tool, message, value):
    if not (isinstance(value, (tuple, list)) and len(value) == 2):
      LOG('CMFActivity', WARNING,
          'unable to recognize value for after_path_and_method_id: %r' % (value,))
      return []
    return self._validate(activity_tool, path=value[0], method_id=value[1])

  def _validate_after_tag(self, activity_tool, message, value):
    return self._validate(activity_tool, tag=value)

  def _validate_after_tag_and_method_id(self, activity_tool, message, value):
    # Count number of occurances of tag and method_id
    if not (isinstance(value, (tuple, list)) and len(value) == 2):
      LOG('CMFActivity', WARNING,
          'unable to recognize value for after_tag_and_method_id: %r' % (value,))
      return []
    return self._validate(activity_tool, tag=value[0], method_id=value[1])

  def _validate_serialization_tag(self, activity_tool, message, value):
    return self._validate(activity_tool, serialization_tag=value)

  def _log(self, severity, summary):
    LOG(self.__class__.__name__, severity, summary,
        error=severity>INFO and sys.exc_info() or None)

  def distribute(self, activity_tool, node_count):
    assignMessage = getattr(activity_tool, 'SQLBase_assignMessage', None)
    if assignMessage is None:
      return
    offset = 0
    now_date = self.getNow(activity_tool)
    validated_count = 0
    while 1:
      result = self._getMessageList(
        activity_tool,
        processing_node=-1,
        to_date=now_date,
        offset=offset,
        count=READ_MESSAGE_LIMIT,
      )
      if not result:
        return
      transaction.commit()

      validation_text_dict = {'none': 1}
      message_dict = {}
      for line in result:
        message = Message.load(line.message, uid=line.uid, line=line)
        if not hasattr(message, 'order_validation_text'): # BBB
          message.order_validation_text = self.getOrderValidationText(message)
        self.getExecutableMessageList(activity_tool, message, message_dict,
                                      validation_text_dict, now_date=now_date)
      if message_dict:
        distributable_uid_set = set()
        serialization_tag_dict = {}
        for message in message_dict.itervalues():
          serialization_tag = message.activity_kw.get('serialization_tag')
          if serialization_tag is None:
            distributable_uid_set.add(message.uid)
          else:
            serialization_tag_dict.setdefault(serialization_tag,
                                              []).append(message)
        for message_list in serialization_tag_dict.itervalues():
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
          assignMessage(table=self.sql_table,
            processing_node=0, uid=tuple(distributable_uid_set))
          validated_count += distributable_count
          if validated_count >= MAX_VALIDATED_LIMIT:
            return
      offset += READ_MESSAGE_LIMIT

  def getReservedMessageList(self, activity_tool, date, processing_node,
                             limit=None, group_method_id=None):
    """
      Get and reserve a list of messages.
      limit
        Maximum number of messages to fetch.
        This number is not garanted to be reached, because of:
         - not enough messages being pending execution
         - race condition (other nodes reserving the same messages at the same
           time)
        This number is guaranted not to be exceeded.
        If None (or not given) no limit apply.
    """
    assert limit
    # Do not check already-assigned messages when trying to reserve more
    # activities, because in such case we will find one reserved activity.
    result = activity_tool.SQLBase_selectReservedMessageList(
      table=self.sql_table,
      count=limit,
      processing_node=processing_node,
      group_method_id=group_method_id,
    )
    limit -= len(result)
    if limit:
      reservable = activity_tool.SQLBase_getReservableMessageList(
        table=self.sql_table,
        count=limit,
        processing_node=processing_node,
        to_date=date,
        group_method_id=group_method_id,
      )
      if reservable:
        activity_tool.SQLBase_reserveMessageList(
          uid=[x.uid for x in reservable],
          table=self.sql_table,
          processing_node=processing_node,
        )
        # DC.ZRDB.Results.Results does not implement concatenation
        # Implement an imperfect (but cheap) concatenation. Do not update
        # __items__ nor _data_dictionary.
        assert result._names == reservable._names, (result._names,
          reservable._names)
        result._data += reservable._data
    return result

  def makeMessageListAvailable(self, activity_tool, uid_list):
    """
      Put messages back in processing_node=0 .
    """
    if len(uid_list):
      activity_tool.SQLBase_makeMessageListAvailable(table=self.sql_table,
                                                     uid=uid_list)

  def getProcessableMessageLoader(self, activity_tool, processing_node):
    # do not merge anything
    def load(line):
      uid = line.uid
      m = Message.load(line.message, uid=uid, line=line)
      return m, uid, ()
    return load

  def getProcessableMessageList(self, activity_tool, processing_node):
    """
      Always true:
        For each reserved message, delete redundant messages when it gets
        reserved (definitely lost, but they are expandable since redundant).

      - reserve a message
      - set reserved message to processing=1 state
      - if this message has a group_method_id:
        - reserve a bunch of messages
        - until the total "cost" of the group goes over 1
          - get one message from the reserved bunch (this messages will be
            "needed")
          - update the total cost
        - set "needed" reserved messages to processing=1 state
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
    def getReservedMessageList(limit, group_method_id=None):
      line_list = self.getReservedMessageList(activity_tool=activity_tool,
                                              date=now_date,
                                              processing_node=processing_node,
                                              limit=limit,
                                              group_method_id=group_method_id)
      if line_list:
        self._log(TRACE, 'Reserved messages: %r' % [x.uid for x in line_list])
      return line_list
    now_date = self.getNow(activity_tool)
    uid_to_duplicate_uid_list_dict = {}
    try:
      result = getReservedMessageList(1)
      if result:
        load = self.getProcessableMessageLoader(activity_tool, processing_node)
        m, uid, uid_list = load(result[0])
        message_list = [m]
        uid_to_duplicate_uid_list_dict[uid] = uid_list
        group_method_id = m.line.group_method_id
        if group_method_id != '\0':
          # Count the number of objects to prevent too many objects.
          cost = m.activity_kw.get('group_method_cost', .01)
          assert 0 < cost <= 1, (self.sql_table, uid)
          count = m.getObjectCount(activity_tool)
          # this is heuristic (messages with same group_method_id
          # are likely to have the same group_method_cost)
          limit = int(1. / cost + 1 - count)
          if limit > 1: # <=> cost * count < 1
            cost *= count
            # Retrieve objects which have the same group method.
            result = iter(getReservedMessageList(limit, group_method_id))
            for line in result:
              if line.uid in uid_to_duplicate_uid_list_dict:
                continue
              m, uid, uid_list = load(line)
              if m is None:
                uid_to_duplicate_uid_list_dict[uid] += uid_list
                continue
              uid_to_duplicate_uid_list_dict[uid] = uid_list
              cost += m.getObjectCount(activity_tool) * \
                      m.activity_kw.get('group_method_cost', .01)
              message_list.append(m)
              if cost >= 1:
                # Unreserve extra messages as soon as possible.
                self.makeMessageListAvailable(activity_tool=activity_tool,
                  uid_list=[line.uid for line in result if line.uid != uid])
        activity_tool.SQLBase_processMessage(table=self.sql_table,
          uid=uid_to_duplicate_uid_list_dict.keys())
        return message_list, group_method_id, uid_to_duplicate_uid_list_dict
    except:
      self._log(WARNING, 'Exception while reserving messages.')
      if uid_to_duplicate_uid_list_dict:
        to_free_uid_list = uid_to_duplicate_uid_list_dict.keys()
        for uid_list in uid_to_duplicate_uid_list_dict.itervalues():
          to_free_uid_list += uid_list
        try:
          self.makeMessageListAvailable(activity_tool=activity_tool,
                                        uid_list=to_free_uid_list)
        except:
          self._log(ERROR, 'Failed to free messages: %r' % to_free_uid_list)
        else:
          if to_free_uid_list:
            self._log(TRACE, 'Freed messages %r' % to_free_uid_list)
      else:
        self._log(TRACE, '(no message was reserved)')
    return [], None, uid_to_duplicate_uid_list_dict

  def _abort(self):
    try:
      transaction.abort()
    except:
      # Unfortunately, database adapters may raise an exception against abort.
      self._log(PANIC,
          'abort failed, thus some objects may be modified accidentally')
      raise

  # Queue semantic
  def dequeueMessage(self, activity_tool, processing_node):
    message_list, group_method_id, uid_to_duplicate_uid_list_dict = \
      self.getProcessableMessageList(activity_tool, processing_node)
    if message_list:
      # Remove group_id parameter from group_method_id
      if group_method_id is not None:
        group_method_id = group_method_id.split('\0')[0]
      if group_method_id not in (None, ""):
        method  = activity_tool.invokeGroup
        args = (group_method_id, message_list, self.__class__.__name__,
                hasattr(self, 'generateMessageUID'))
        activity_runtime_environment = ActivityRuntimeEnvironment(None)
      else:
        method = activity_tool.invoke
        message = message_list[0]
        args = (message, )
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
        with activity_runtime_environment:
          method(*args)
        # Abort if at least 1 message failed. On next tic, only those that
        # succeeded will be selected because their at_date won't have been
        # increased.
        for m in message_list:
          if m.getExecutionState() == MESSAGE_NOT_EXECUTED:
            raise _DequeueMessageException
        transaction.commit()
      except:
        exc_info = sys.exc_info()
        if exc_info[1] is not _DequeueMessageException:
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
    return not message_list

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
            activity_tool.SQLBase_reactivate(table=self.sql_table,
                                             uid=[uid],
                                             delay=delay,
                                             retry=1)
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
        self._retryOnLockError(activity_tool.SQLBase_delMessage,
                               kw={'table': self.sql_table,
                                   'uid': deletable_uid_list})
      except:
        self._log(ERROR, 'Failed to delete messages %r' % deletable_uid_list)
      else:
        self._log(TRACE, 'Deleted messages %r' % deletable_uid_list)
    if delay_uid_list:
      try:
        # If this is a conflict error, do not increase 'retry' but only delay.
        activity_tool.SQLBase_reactivate(table=self.sql_table,
          uid=delay_uid_list, delay=VALIDATION_ERROR_DELAY, retry=None)
      except:
        self._log(ERROR, 'Failed to delay %r' % delay_uid_list)
    if final_error_uid_list:
      try:
        activity_tool.SQLBase_assignMessage(table=self.sql_table,
          uid=final_error_uid_list, processing_node=INVOKE_ERROR_STATE)
      except:
        self._log(ERROR, 'Failed to set message to error state for %r'
                         % final_error_uid_list)
    if make_available_uid_list:
      try:
        self.makeMessageListAvailable(activity_tool=activity_tool,
                                      uid_list=make_available_uid_list)
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

  def flush(self, activity_tool, object_path, invoke=0, method_id=None, **kw):
    """
      object_path is a tuple
    """
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
        validate_value = VALID if line and line.processing_node != -1 else \
                         message.validate(self, activity_tool)
        if validate_value == VALID:
          # Try to invoke the message - what happens if invoke calls flushActivity ??
          with ActivityRuntimeEnvironment(message):
            activity_tool.invoke(message)
          if message.getExecutionState() != MESSAGE_EXECUTED:
            raise ActivityFlushError('Could not invoke %s on %s'
                                     % (message.method_id, path))
        elif validate_value is INVALID_PATH:
          raise ActivityFlushError('The document %s does not exist' % path)
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
    for line in self._getMessageList(activity_tool, path=path, processing=0,
        **({'method_id': method_id} if method_id else {})):
      uid_list.append(line.uid)
      if invoke:
        invoke(Message.load(line.message, uid=line.uid, line=line))
    if uid_list:
      activity_tool.SQLBase_delMessage(table=self.sql_table, uid=uid_list)

  # Required for tests
  def timeShift(self, activity_tool, delay, processing_node=None):
    """
      To simulate time shift, we simply substract delay from
      all dates in message(_queue) table
    """
    activity_tool.SQLBase_timeShift(table=self.sql_table, delay=delay,
                                    processing_node=processing_node)
