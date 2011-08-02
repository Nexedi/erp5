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
from zLOG import LOG, TRACE, INFO, WARNING, ERROR, PANIC
from ZODB.POSException import ConflictError
from Products.CMFActivity.ActivityTool import (
  MESSAGE_NOT_EXECUTED, MESSAGE_EXECUTED)
from Products.CMFActivity.ActiveObject import (
  INVOKE_ERROR_STATE, VALIDATE_ERROR_STATE)
from Products.CMFActivity.ActivityRuntimeEnvironment import (
  ActivityRuntimeEnvironment, getTransactionalVariable)
from Queue import VALIDATION_ERROR_DELAY

def sort_message_key(message):
  # same sort key as in SQL{Dict,Queue}_readMessageList
  return message.line.priority, message.line.date, message.uid


class SQLBase:
  """
    Define a set of common methods for SQL-based storage of activities.
  """
 
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

  def getMessageList(self, activity_tool, processing_node=None,
                     include_processing=0, **kw):
    # YO: reading all lines might cause a deadlock
    class_name = self.__class__.__name__
    readMessageList = getattr(activity_tool,
                              class_name + '_readMessageList',
                              None)
    if readMessageList is None:
      return []
    return [self.loadMessage(line.message,
                             activity=class_name,
                             uid=line.uid,
                             processing_node=line.processing_node,
                             retry=line.retry,
                             processing=line.processing)
            for line in readMessageList(path=None,
                                        method_id=None,
                                        processing_node=processing_node,
                                        to_date=None,
                                        include_processing=include_processing)]

  def _getPriority(self, activity_tool, method, default):
    result = method()
    assert len(result) == 1
    priority = result[0]['priority']
    if priority is None:
      priority = default
    return priority

  def _retryOnLockError(self, method, args=(), kw={}):
    while True:
      try:
        return method(*args, **kw)
      except ConflictError:
        # Note that this code assumes that a database adapter translates
        # a lock error into a conflict error.
        LOG('SQLBase', INFO, 'Got a lock error, retrying...')

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
    select = activity_tool.SQLBase_selectReservedMessageList
    result = not group_method_id and select(table=self.sql_table, count=limit,
                                            processing_node=processing_node)
    if not result:
      activity_tool.SQLBase_reserveMessageList(table=self.sql_table,
        count=limit, processing_node=processing_node, to_date=date,
        group_method_id=group_method_id)
      result = select(table=self.sql_table,
                      processing_node=processing_node, count=limit)
    return result

  def makeMessageListAvailable(self, activity_tool, uid_list):
    """
      Put messages back in processing_node=0 .
    """
    if len(uid_list):
      activity_tool.SQLBase_makeMessageListAvailable(table=self.sql_table,
                                                     uid=uid_list)

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
      if len(line_list):
        self._log(TRACE, 'Reserved messages: %r' % [x.uid for x in line_list])
      return line_list
    def getDuplicateMessageUidList(line):
      uid_list = self.getDuplicateMessageUidList(activity_tool=activity_tool,
        line=line, processing_node=processing_node)
      if len(uid_list):
        self._log(TRACE, 'Reserved duplicate messages: %r' % (uid_list, ))
      return uid_list
    now_date = self.getNow(activity_tool)
    message_list = []
    group_method_id = None
    try:
      result = getReservedMessageList(limit=1)
      uid_to_duplicate_uid_list_dict = {}
      if len(result) > 0:
        line = result[0]
        uid = line.uid
        m = self.loadMessage(line.message, uid=uid, line=line)
        message_list.append(m)
        group_method_id = line.group_method_id
        activity_tool.SQLBase_processMessage(table=self.sql_table, uid=[uid])
        uid_to_duplicate_uid_list_dict.setdefault(uid, []) \
          .extend(getDuplicateMessageUidList(line))
        if group_method_id != '\0':
          # Count the number of objects to prevent too many objects.
          cost = m.activity_kw.get('group_method_cost', .01)
          assert 0 < cost <= 1, (self.sql_table, uid)
          count = len(m.getObjectList(activity_tool))
          # this is heuristic (messages with same group_method_id
          # are likely to have the same group_method_cost)
          limit = int(1. / cost + 1 - count)
          if limit > 1: # <=> cost * count < 1
            cost *= count
            # Retrieve objects which have the same group method.
            result = getReservedMessageList(limit=limit,
                                            group_method_id=group_method_id)
            path_and_method_id_dict = {}
            unreserve_uid_list = []
            for line in result:
              if line.uid == uid:
                continue
              # All fetched lines have the same group_method_id and
              # processing_node.
              # Their dates are lower-than or equal-to now_date.
              # We read each line once so lines have distinct uids.
              # So what remains to be filtered on are path, method_id and
              # order_validation_text.
              try:
                key = line.path, line.method_id, line.order_validation_text
              except AttributeError:
                pass # message_queue does not have 'order_validation_text'
              else:
                original_uid = path_and_method_id_dict.get(key)
                if original_uid is not None:
                  uid_to_duplicate_uid_list_dict.setdefault(original_uid, []) \
                  .append(line.uid)
                  continue
                path_and_method_id_dict[key] = line.uid
                uid_to_duplicate_uid_list_dict.setdefault(line.uid, []) \
                .extend(getDuplicateMessageUidList(line))
              if cost < 1:
                m = self.loadMessage(line.message, uid=line.uid, line=line)
                cost += len(m.getObjectList(activity_tool)) * \
                        m.activity_kw.get('group_method_cost', .01)
                message_list.append(m)
              else:
                unreserve_uid_list.append(line.uid)
            activity_tool.SQLBase_processMessage(table=self.sql_table,
              uid=[m.uid for m in message_list])
            # Unreserve extra messages as soon as possible.
            self.makeMessageListAvailable(activity_tool=activity_tool,
                                          uid_list=unreserve_uid_list)
      return message_list, group_method_id, uid_to_duplicate_uid_list_dict
    except:
      self._log(WARNING, 'Exception while reserving messages.')
      if len(message_list):
        to_free_uid_list = [m.uid for m in message_list]
        try:
          self.makeMessageListAvailable(activity_tool=activity_tool,
                                        uid_list=to_free_uid_list)
        except:
          self._log(ERROR, 'Failed to free messages: %r' % to_free_uid_list)
        else:
          if len(to_free_uid_list):
            self._log(TRACE, 'Freed messages %r' % to_free_uid_list)
      else:
        self._log(TRACE, '(no message was reserved)')
      return [], 0, None, {}

  # Queue semantic
  def dequeueMessage(self, activity_tool, processing_node):
    def makeMessageListAvailable(uid_list, uid_to_duplicate_uid_list_dict):
      final_uid_list = []
      for uid in uid_list:
        final_uid_list.append(uid)
        final_uid_list.extend(uid_to_duplicate_uid_list_dict.get(uid, []))
      self.makeMessageListAvailable(activity_tool=activity_tool,
                                    uid_list=final_uid_list)
    message_list, group_method_id, uid_to_duplicate_uid_list_dict = \
      self.getProcessableMessageList(activity_tool, processing_node)
    if message_list:
      # Remove group_id parameter from group_method_id
      if group_method_id is not None:
        group_method_id = group_method_id.split('\0')[0]
      if group_method_id not in (None, ""):
        method  = activity_tool.invokeGroup
        args = (group_method_id, message_list, self.__class__.__name__,
                self.merge_duplicate)
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
      tv = getTransactionalVariable()
      tv['activity_runtime_environment'] = activity_runtime_environment
      # Try to invoke
      try:
        method(*args)
      except:
        self._log(WARNING,
          'Exception raised when invoking messages (uid, path, method_id) %r'
          % [(m.uid, m.object_path, m.method_id) for m in message_list])
        try:
          transaction.abort()
        except:
          # Unfortunately, database adapters may raise an exception against
          # abort.
          self._log(PANIC,
              'abort failed, thus some objects may be modified accidentally')
          raise
        # XXX Is it still useful to free messages now that this node is able
        #     to reselect them ?
        to_free_uid_list = [x.uid for x in message_list]
        try:
          makeMessageListAvailable(to_free_uid_list,
                                   uid_to_duplicate_uid_list_dict)
        except:
          self._log(ERROR, 'Failed to free messages: %r' % to_free_uid_list)
        else:
          self._log(TRACE, 'Freed messages %r' % to_free_uid_list)
      # Abort if something failed.
      if [m for m in message_list if m.getExecutionState() == MESSAGE_NOT_EXECUTED]:
        endTransaction = transaction.abort
      else:
        endTransaction = transaction.commit
      try:
        endTransaction()
      except:
        self._log(WARNING,
          'Failed to end transaction for messages (uid, path, method_id) %r'
          % [(m.uid, m.object_path, m.method_id) for m in message_list])
        if endTransaction == transaction.abort:
          self._log(PANIC, 'Failed to abort executed messages.'
            ' Some objects may be modified accidentally.')
        else:
          try:
            transaction.abort()
          except:
            self._log(PANIC, 'Failed to abort executed messages which also'
              ' failed to commit. Some objects may be modified accidentally.')
            raise
        exc_info = sys.exc_info()
        for m in message_list:
          m.setExecutionState(MESSAGE_NOT_EXECUTED, exc_info, log=False)
        try:
          makeMessageListAvailable([x.uid for x in message_list],
                                   uid_to_duplicate_uid_list_dict)
        except:
          self._log(ERROR, 'Failed to free remaining messages: %r'
                           % (message_list, ))
        else:
          self._log(TRACE, 'Freed messages %r' % (message_list, ))
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
    non_executable_message_list = []
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
        # BACK: Only exceptions can be classes in Python 2.6.
        # Once we drop support for Python 2.4,
        # please, remove the "type(m.exc_type) is type(ConflictError)" check
        # and leave only the "issubclass(m.exc_type, ConflictError)" check.
        if type(m.exc_type) is type(ConflictError) and \
           m.conflict_retry and issubclass(m.exc_type, ConflictError):
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
          if max_retry is None and retry == m.__class__.max_retry:
            notify_user_list.append((m, True))
          delay = m.delay
          if delay is None:
            # By default, make delay quadratic to the number of retries.
            delay = VALIDATION_ERROR_DELAY * (retry * retry + 1) / 2
          try:
            # Immediately update, because values different for every message
            activity_tool.SQLBase_reactivate(table=self.sql_table,
                                             uid=[uid],
                                             delay=delay,
                                             retry=1)
          except:
            self._log(WARNING, 'Failed to reactivate %r' % uid)
        make_available_uid_list.append(uid)
      else:
        # Internal CMFActivity error: the message can not be executed because
        # something is missing (context object cannot be found, method cannot
        # be accessed on object).
        non_executable_message_list.append(uid)
        notify_user_list.append((m, False))
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
    if non_executable_message_list:
      try:
        activity_tool.SQLBase_assignMessage(table=self.sql_table,
          uid=non_executable_message_list, processing_node=VALIDATE_ERROR_STATE)
      except:
        self._log(ERROR, 'Failed to set message to invalid path state for %r'
                         % non_executable_message_list)
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
