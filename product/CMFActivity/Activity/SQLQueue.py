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

from Products.CMFActivity.ActivityTool import registerActivity, MESSAGE_NOT_EXECUTED, MESSAGE_EXECUTED
from RAMQueue import RAMQueue
from Queue import VALID, INVALID_PATH, VALIDATION_ERROR_DELAY, \
        abortTransactionSynchronously
from Products.CMFActivity.ActiveObject import INVOKE_ERROR_STATE, VALIDATE_ERROR_STATE
from Products.CMFActivity.Errors import ActivityFlushError
from ZODB.POSException import ConflictError
from types import ClassType
import sys
from time import time
from sets import ImmutableSet
from SQLBase import SQLBase
from Products.CMFActivity.ActivityRuntimeEnvironment import setActivityRuntimeValue, updateActivityRuntimeValue, clearActivityRuntimeEnvironment
from zExceptions import ExceptionFormatter

try:
  from transaction import get as get_transaction
except ImportError:
  pass

from zLOG import LOG, WARNING, ERROR, INFO, PANIC, TRACE

MAX_PRIORITY = 5
# Stop validating more messages when this limit is reached
MAX_VALIDATED_LIMIT = 1000
# Read this many messages to validate.
READ_MESSAGE_LIMIT = 1000
# Process this many messages in each dequeueMessage call.
MESSAGE_BUNDLE_SIZE = 10

class SQLQueue(RAMQueue, SQLBase):
  """
    A simple OOBTree based queue. It should be compatible with transactions
    and provide sequentiality. Should not create conflict
    because use of OOBTree.
  """

  def prepareQueueMessageList(self, activity_tool, message_list):
    registered_message_list = [m for m in message_list if m.is_registered]
    if len(registered_message_list):
      uid_list = activity_tool.getPortalObject().portal_ids.generateNewLengthIdList(
        id_group='portal_activity_queue', id_count=len(registered_message_list),
        store=0)
      path_list = ['/'.join(m.object_path) for m in registered_message_list]
      method_id_list = [m.method_id for m in registered_message_list]
      priority_list = [m.activity_kw.get('priority', 1) for m in registered_message_list]
      date_list = [m.activity_kw.get('at_date', None) for m in registered_message_list]
      tag_list = [m.activity_kw.get('tag', '') for m in registered_message_list]
      serialization_tag_list = [m.activity_kw.get('serialization_tag', '') for m in registered_message_list]
      message_list = [self.dumpMessage(m) for m in registered_message_list]
      activity_tool.SQLQueue_writeMessageList(uid_list=uid_list,
                                              path_list=path_list,
                                              method_id_list=method_id_list,
                                              priority_list=priority_list,
                                              message_list=message_list,
                                              date_list=date_list,
                                              tag_list=tag_list,
                                              serialization_tag_list=serialization_tag_list)

  def prepareDeleteMessage(self, activity_tool, m):
    # Erase all messages in a single transaction
    #LOG("prepareDeleteMessage", 0, str(m.__dict__))
    activity_tool.SQLQueue_delMessage(uid = [m.uid])

  def finishQueueMessage(self, activity_tool_path, m):
    # Nothing to do in SQLQueue.
    pass

  def finishDeleteMessage(self, activity_tool_path, m):
    # Nothing to do in SQLQueue.
    pass

  def getReservedMessageList(self, activity_tool, date, processing_node, limit=None):
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
    result = activity_tool.SQLQueue_selectReservedMessageList(processing_node=processing_node, count=limit)
    if len(result) == 0:
      activity_tool.SQLQueue_reserveMessageList(count=limit, processing_node=processing_node, to_date=date)
      result = activity_tool.SQLQueue_selectReservedMessageList(processing_node=processing_node, count=limit)
    return result

  def makeMessageListAvailable(self, activity_tool, uid_list):
    """
      Put messages back in processing_node=0 .
    """
    if len(uid_list):
      activity_tool.SQLQueue_makeMessageListAvailable(uid_list=uid_list)

  def getProcessableMessageList(self, activity_tool, processing_node):
    """
      Always true:
        For each reserved message, delete redundant messages when it gets
        reserved (definitely lost, but they are expandable since redundant).

      - reserve a message
      - set reserved message to processing=1 state
      - if this message has a group_method_id:
        - reserve a bunch of BUNDLE_MESSAGE_COUNT messages
        - untill number of impacted objects goes over MAX_GROUPED_OBJECTS
          - get one message from the reserved bunch (this messages will be
            "needed")
          - increase the number of impacted object
        - set "needed" reserved messages to processing=1 state
        - unreserve "unneeded" messages
      - return still-reserved message list

      If any error happens in above described process, try to unreserve all
      messages already reserved in that process.
      If it fails, complain loudly that some messages might still be in an
      unclean state.

      Returned values:
        list of 3-tuple:
          - message uid
          - message
          - priority
    """
    def getReservedMessageList(limit):
      line_list = self.getReservedMessageList(activity_tool=activity_tool,
                                              date=now_date,
                                              processing_node=processing_node,
                                              limit=limit)
      if len(line_list):
        LOG('SQLQueue', TRACE, 'Reserved messages: %r' % ([x.uid for x in line_list]))
      return line_list
    def makeMessageListAvailable(uid_list):
      self.makeMessageListAvailable(activity_tool=activity_tool, uid_list=uid_list)
    now_date = self.getNow(activity_tool)
    message_list = []
    def append(line, message):
      uid = line.uid
      message_list.append((uid, message, line.priority))
    try:
      result = getReservedMessageList(limit=MESSAGE_BUNDLE_SIZE)
      for line in result:
        m = self.loadMessage(line.message, uid=line.uid)
        append(line, m)
      if len(message_list):
        activity_tool.SQLQueue_processMessage(uid=[x[0] for x in message_list])
      return message_list
    except:
      LOG('SQLQueue', WARNING, 'Exception while reserving messages.', error=sys.exc_info())
      if len(message_list):
        to_free_uid_list = [x[0] for x in message_list]
        try:
          makeMessageListAvailable(to_free_uid_list)
        except:
          LOG('SQLQueue', ERROR, 'Failed to free messages: %r' % (to_free_uid_list, ), error=sys.exc_info())
        else:
          if len(to_free_uid_list):
            LOG('SQLQueue', TRACE, 'Freed messages %r' % (to_free_uid_list, ))
      else:
        LOG('SQLQueue', TRACE, '(no message was reserved)')
      return []

  def finalizeMessageExecution(self, activity_tool, message_uid_priority_list):
    def makeMessageListAvailable(uid_list):
      self.makeMessageListAvailable(activity_tool=activity_tool, uid_list=uid_list)
    deletable_uid_list = []
    delay_uid_list = []
    final_error_uid_list = []
    message_with_active_process_list = []
    notify_user_list = []
    non_executable_message_list = []
    for uid, m, priority in message_uid_priority_list:
      if m.getExecutionState() == MESSAGE_EXECUTED:
        deletable_uid_list.append(uid)
        if m.active_process:
          message_with_active_process_list.append(m)
      elif m.getExecutionState() == MESSAGE_NOT_EXECUTED:
        if type(m.exc_type) is ClassType and \
           issubclass(m.exc_type, ConflictError):
          delay_uid_list.append(uid)
        elif priority > MAX_PRIORITY:
          notify_user_list.append(m)
          final_error_uid_list.append(uid)
        else:
          try:
            # Immediately update, because values different for every message
            activity_tool.SQLQueue_setPriority(
              uid=[uid],
              delay=VALIDATION_ERROR_DELAY,
              priority=priority + 1)
          except:
            LOG('SQLQueue', WARNING, 'Failed to increase priority of %r' % (uid, ), error=sys.exc_info())
          try:
            makeMessageListAvailable(delay_uid_list)
          except:
            LOG('SQLQueue', ERROR, 'Failed to unreserve %r' % (uid, ), error=sys.exc_info())
          else:
            LOG('SQLQueue', TRACE, 'Freed message %r' % (uid, ))
      else:
        # Internal CMFActivity error: the message can not be executed because
        # something is missing (context object cannot be found, method cannot
        # be accessed on object).
        non_executable_message_list.append(uid)
    if len(deletable_uid_list):
      try:
        self._retryOnLockError(activity_tool.SQLQueue_delMessage, kw={'uid': deletable_uid_list})
      except:
        LOG('SQLQueue', ERROR, 'Failed to delete messages %r' % (deletable_uid_list, ), error=sys.exc_info())
      else:
        LOG('SQLQueue', TRACE, 'Deleted messages %r' % (deletable_uid_list, ))
    if len(delay_uid_list):
      try:
        # If this is a conflict error, do not lower the priority but only delay.
        activity_tool.SQLQueue_setPriority(uid=delay_uid_list, delay=VALIDATION_ERROR_DELAY)
      except:
        LOG('SQLQueue', ERROR, 'Failed to delay %r' % (delay_uid_list, ), error=sys.exc_info())
      try:
        makeMessageListAvailable(delay_uid_list)
      except:
        LOG('SQLQueue', ERROR, 'Failed to unreserve %r' % (delay_uid_list, ), error=sys.exc_info())
      else:
        LOG('SQLQueue', TRACE, 'Freed messages %r' % (delay_uid_list, ))
    if len(final_error_uid_list):
      try:
        activity_tool.SQLQueue_assignMessage(uid=final_error_uid_list,
                                             processing_node=INVOKE_ERROR_STATE)
      except:
        LOG('SQLQueue', ERROR, 'Failed to set message to error state for %r' % (final_error_uid_list, ), error=sys.exc_info())
    if len(non_executable_message_list):
      try:
        activity_tool.SQLQueue_assignMessage(uid=non_executable_message_list,
                                             processing_node=VALIDATE_ERROR_STATE)
      except:
        LOG('SQLQueue', ERROR, 'Failed to set message to invalid path state for %r' % (final_error_uid_list, ), error=sys.exc_info())
    try:
      for m in notify_user_list:
        m.notifyUser(activity_tool)
      for m in message_with_active_process_list:
        active_process = activity_tool.unrestrictedTraverse(m.active_process)
        if not active_process.hasActivity():
          # No more activity
          m.notifyUser(activity_tool, message="Process Finished") # XXX commit bas ???
    except:
      # Notification failures must not cause this method to raise.
      LOG('SQLQueue', WARNING, 'Exception during notification phase of finalizeMessageExecution', error=sys.exc_info())

  def dequeueMessage(self, activity_tool, processing_node):
    def makeMessageListAvailable(uid_list):
      self.makeMessageListAvailable(activity_tool=activity_tool, uid_list=uid_list)
    message_uid_priority_list = \
      self.getProcessableMessageList(activity_tool, processing_node)
    if len(message_uid_priority_list):
      processing_stop_time = time() + 30 # Stop processing after more than 10 seconds were spent
      processed_message_uid_list = []
      # Commit right before executing messages.
      # As MySQL transaction do no start exactly at the same time as ZODB
      # transactions but a bit later, messages available might be called
      # on objects which are not available - or available in an old
      # version - to ZODB connector.
      # So all connectors must be commited now that we have selected
      # everything needed from MySQL to get a fresh view of ZODB objects.
      get_transaction().commit()
      for value in message_uid_priority_list:
        clearActivityRuntimeEnvironment()
        updateActivityRuntimeValue({'processing_node': processing_node,
                                    'activity_kw': value[1].activity_kw,
                                    'priority': value[2],
                                    'uid': value[0]})
        processed_message_uid_list.append(value)
        # Try to invoke
        try:
          activity_tool.invoke(value[1])
          if value[1].getExecutionState() != MESSAGE_NOT_EXECUTED:
            # Commit so that if a message raises it doesn't causes previous
            # successfull messages to be rolled back. This commit might fail,
            # so it is protected the same way as activity execution by the
            # same "try" block.
            get_transaction().commit()
          else:
            # This message failed, revert.
            abortTransactionSynchronously()
        except:
          LOG('SQLQueue', WARNING, 'Exception raised when invoking message (uid, path, method_id) %r' % ((value[0], value[1].object_path, value[1].method_id), ), error=sys.exc_info())
          try:
            abortTransactionSynchronously()
          except:
            # Unfortunately, database adapters may raise an exception against abort.
            LOG('SQLQueue', PANIC, 'abort failed, thus some objects may be modified accidentally')
            raise
          # We must make sure that the message is not set as executed.
          # It is possible that the message is executed but the commit
          # of the transaction fails
          value[1].setExecutionState(MESSAGE_NOT_EXECUTED, context=activity_tool)
          try:
            makeMessageListAvailable([value[0]])
          except:
            LOG('SQLQueue', ERROR, 'Failed to free message: %r' % (value, ), error=sys.exc_info())
          else:
            LOG('SQLQueue', TRACE, 'Freed message %r' % (value, ))
        if time() > processing_stop_time:
          LOG('SQLQueue', TRACE, 'Stop processing message batch because processing delay exceeded')
          break
      # Release all unprocessed messages
      processed_uid_set = ImmutableSet([x[0] for x in processed_message_uid_list])
      to_free_uid_list = [x[0] for x in message_uid_priority_list if x[0] not in processed_uid_set]
      if len(to_free_uid_list):
        try:
          makeMessageListAvailable(to_free_uid_list)
        except:
          LOG('SQLQueue', ERROR, 'Failed to free remaining messages: %r' % (to_free_uid_list, ), error=sys.exc_info())
        else:
          LOG('SQLQueue', TRACE, 'Freed messages %r' % (to_free_uid_list, ))
      self.finalizeMessageExecution(activity_tool, processed_message_uid_list)
    get_transaction().commit()
    return not len(message_uid_priority_list)


  def hasActivity(self, activity_tool, object, **kw):
    hasMessage = getattr(activity_tool, 'SQLQueue_hasMessage', None)
    if hasMessage is not None:
      if object is not None:
        my_object_path = '/'.join(object.getPhysicalPath())
        result = hasMessage(path=my_object_path, **kw)
        if len(result) > 0:
          return result[0].message_count > 0
      else:
        return 1 # Default behaviour if no object specified is to return 1 until active_process implemented
    return 0

  def flush(self, activity_tool, object_path, invoke=0, method_id=None, commit=0, **kw):
    """
      object_path is a tuple

      commit allows to choose mode
        - if we commit, then we make sure no locks are taken for too long
        - if we do not commit, then we can use flush in a larger transaction

      commit should in general not be used

      NOTE: commiting is very likely nonsenses here. We should just avoid to flush as much as possible
    """
    readMessageList = getattr(activity_tool, 'SQLQueue_readMessageList', None)
    if readMessageList is not None:
      #return # Do nothing here to precent overlocking
      path = '/'.join(object_path)
      # Parse each message in registered
      for m in activity_tool.getRegisteredMessageList(self):
        if object_path == m.object_path and (method_id is None or method_id == m.method_id):
          if invoke:
            # First Validate
            validate_value = m.validate(self, activity_tool)
            if validate_value is VALID:
              activity_tool.invoke(m) # Try to invoke the message - what happens if invoke calls flushActivity ??
              if m.getExecutionState() != MESSAGE_EXECUTED:                                                 # Make sure message could be invoked
                # The message no longer exists
                raise ActivityFlushError, (
                    'Could not evaluate %s on %s' % (m.method_id , path))
            elif validate_value is INVALID_PATH:
              # The message no longer exists
              raise ActivityFlushError, (
                  'The document %s does not exist' % path)
            else:
              raise ActivityFlushError, (
                  'Could not validate %s on %s' % (m.method_id , path))
          activity_tool.unregisterMessage(self, m)
      # Parse each message in SQL queue
      result = readMessageList(path=path, method_id=method_id, processing_node=None)
      for line in result:
        path = line.path
        method_id = line.method_id
        m = self.loadMessage(line.message, uid = line.uid)
        if invoke:
          # First Validate (only if message is marked as new)
          if line.processing_node == -1:
            validate_value = m.validate(self, activity_tool)
          else:
            validate_value = VALID
          if validate_value is VALID:
            activity_tool.invoke(m) # Try to invoke the message - what happens if invoke calls flushActivity ??
            if m.getExecutionState() != MESSAGE_EXECUTED:                                                 # Make sure message could be invoked
              # The message no longer exists
              raise ActivityFlushError, (
                  'Could not evaluate %s on %s' % (method_id , path))
          elif validate_value is INVALID_PATH:
            # The message no longer exists
            raise ActivityFlushError, (
                'The document %s does not exist' % path)
          else:
            raise ActivityFlushError, (
                'Could not validate %s on %s' % (m.method_id , path))

      if len(result):
        activity_tool.SQLQueue_delMessage(uid = [line.uid for line in result])

  # def start(self, activity_tool, active_process=None):
  #   uid_list = activity_tool.SQLQueue_readUidList(path=path, active_process=active_process)
  #   activity_tool.SQLQueue_assignMessage(uid = uid_list, processing_node = DISTRIBUTABLE_STATE)

  # def stop(self, activity_tool, active_process=None):
  #   uid_list = activity_tool.SQLQueue_readUidList(path=path, active_process=active_process)
  #   activity_tool.SQLQueue_assignMessage(uid = uid_list, processing_node = STOP_STATE)

  def getMessageList(self, activity_tool, processing_node=None,**kw):
    message_list = []
    readMessageList = getattr(activity_tool, 'SQLQueue_readMessageList', None)
    if readMessageList is not None:
      result = readMessageList(path=None, method_id=None, processing_node=None)
      for line in result:
        m = self.loadMessage(line.message)
        m.processing_node = line.processing_node
        m.priority = line.priority
        message_list.append(m)
    return message_list

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
    result = activity_tool.SQLQueue_validateMessageList(method_id=method_id, 
                                                        path=path,
                                                        message_uid=message_uid, 
                                                        tag=tag,
                                                        count=1)
    return result[0].uid_count

  def countMessageWithTag(self, activity_tool, value):
    """Return the number of messages which match the given tag.
    """
    return self.countMessage(activity_tool, tag=value)

  def dumpMessageList(self, activity_tool):
    # Dump all messages in the table.
    message_list = []
    dumpMessageList = getattr(activity_tool, 'SQLQueue_dumpMessageList', None)
    if dumpMessageList is not None:
      result = dumpMessageList()
      for line in result:
        m = self.loadMessage(line.message, uid = line.uid)
        message_list.append(m)
    return message_list

  def distribute(self, activity_tool, node_count):
    offset = 0
    readMessageList = getattr(activity_tool, 'SQLQueue_readMessageList', None)
    if readMessageList is not None:
      now_date = self.getNow(activity_tool)
      result = readMessageList(path=None, method_id=None, processing_node=-1,
                               to_date=now_date, include_processing=0, 
                               offset=offset, count=READ_MESSAGE_LIMIT)
      validated_count = 0
      #TIME_begin = time()
      while len(result) and validated_count < MAX_VALIDATED_LIMIT:
        get_transaction().commit()

        validation_text_dict = {'none': 1}
        message_dict = {}
        for line in result:
          message = self.loadMessage(line.message, uid = line.uid)
          message.order_validation_text = self.getOrderValidationText(message)
          self.getExecutableMessageList(activity_tool, message, message_dict,
                                        validation_text_dict, now_date=now_date)
        distributable_count = len(message_dict)
        if distributable_count:
          activity_tool.SQLQueue_assignMessage(processing_node=0, uid=[message.uid for message in message_dict.itervalues()])
          validated_count += distributable_count
        if validated_count < MAX_VALIDATED_LIMIT:
          offset += READ_MESSAGE_LIMIT
          result = readMessageList(path=None, method_id=None, processing_node=-1,
                                   to_date=now_date, include_processing=0, 
                                   offset=offset, count=READ_MESSAGE_LIMIT)
      #TIME_end = time()
      #LOG('SQLQueue.distribute', INFO, '%0.4fs : %i messages => %i distributables' % (TIME_end - TIME_begin, offset + len(result), validated_count))

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
      validateMessageList = activity_tool.SQLQueue_validateMessageList
      result = validateMessageList(method_id=method_id,
                                   message_uid=message_uid,
                                   path=path,
                                   tag=tag,
                                   serialization_tag=serialization_tag)
      message_list = []
      for line in result:
        m = self.loadMessage(line.message,
                             uid=line.uid,
                             date=line.date,
                             processing_node=line.processing_node)
        m.order_validation_text = self.getOrderValidationText(m)
        message_list.append(m)
      return message_list
    else:
      return []

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
    if not isinstance(value, (tuple, list)) or len(value) < 2:
      LOG('CMFActivity', WARNING,
          'unable to recognize value for after_tag_and_method_id: %r' % (value,))
      return []
    return self._validate(activity_tool, tag=value[0], method_id=value[1])

  def _validate_serialization_tag(self, activity_tool, message, value):
    return self._validate(activity_tool, serialization_tag=value)

  # Required for tests (time shift)
  def timeShift(self, activity_tool, delay, processing_node = None):
    """
      To simulate timeShift, we simply substract delay from
      all dates in SQLQueue message table
    """
    activity_tool.SQLQueue_timeShift(delay=delay, processing_node=processing_node)

  def getPriority(self, activity_tool):
    method = activity_tool.SQLQueue_getPriority
    default =  RAMQueue.getPriority(self, activity_tool)
    return self._getPriority(activity_tool, method, default)

registerActivity(SQLQueue)
