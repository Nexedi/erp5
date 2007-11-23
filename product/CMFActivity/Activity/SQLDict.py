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

from Products.CMFActivity.ActivityTool import registerActivity
from Queue import VALID, INVALID_PATH, VALIDATION_ERROR_DELAY, \
        abortTransactionSynchronously
from RAMDict import RAMDict
from Products.CMFActivity.ActiveObject import INVOKE_ERROR_STATE, VALIDATE_ERROR_STATE
from Products.CMFActivity.Errors import ActivityFlushError
from ZODB.POSException import ConflictError
import sys
from types import ClassType
#from time import time
from SQLBase import SQLBase

try:
  from transaction import get as get_transaction
except ImportError:
  pass

from zLOG import LOG, TRACE, WARNING, ERROR, INFO, PANIC

MAX_PRIORITY = 5
# Stop validating more messages when this limit is reached
MAX_VALIDATED_LIMIT = 1000 
# Read this many messages to validate.
READ_MESSAGE_LIMIT = 1000
# Stop electing more messages for processing if more than this many objects 
# are impacted by elected messages.
MAX_GROUPED_OBJECTS = 500

class SQLDict(RAMDict, SQLBase):
  """
    A simple OOBTree based queue. It should be compatible with transactions
    and provide sequentiality. Should not create conflict
    because use of OOBTree.
  """
  # Transaction commit methods
  def prepareQueueMessageList(self, activity_tool, message_list):
    registered_message_list = []
    for message in message_list:
      if message.is_registered:
        registered_message_list.append(message)
    if len(registered_message_list) > 0:
      #LOG('SQLDict prepareQueueMessageList', 0, 'registered_message_list = %r' % (registered_message_list,))
      path_list = ['/'.join(message.object_path) for message in registered_message_list]
      method_id_list = [message.method_id for message in registered_message_list]
      priority_list = [message.activity_kw.get('priority', 1) for message in registered_message_list]
      dumped_message_list = [self.dumpMessage(message) for message in registered_message_list]
      date_list = [message.activity_kw.get('at_date', None) for message in registered_message_list]
      group_method_id_list = ['\0'.join([message.activity_kw.get('group_method_id', ''), message.activity_kw.get('group_id', '')])
                              for message in registered_message_list]
      tag_list = [message.activity_kw.get('tag', '') for message in registered_message_list]
      order_validation_text_list = [self.getOrderValidationText(message) for message in registered_message_list]
      uid_list = activity_tool.getPortalObject().portal_ids.generateNewLengthIdList(id_group='portal_activity', 
                   id_count=len(registered_message_list), store=0)
      activity_tool.SQLDict_writeMessageList( uid_list = uid_list,
                                              path_list = path_list,
                                              method_id_list = method_id_list,
                                              priority_list = priority_list,
                                              message_list = dumped_message_list,
                                              date_list = date_list,
                                              group_method_id_list = group_method_id_list,
                                              tag_list = tag_list,
                                              order_validation_text_list = order_validation_text_list)

  def prepareDeleteMessage(self, activity_tool, m):
    # Erase all messages in a single transaction
    path = '/'.join(m.object_path)
    order_validation_text = self.getOrderValidationText(m)
    uid_list = activity_tool.SQLDict_readUidList(path = path, method_id = m.method_id,
                                                 order_validation_text = order_validation_text,
                                                 processing_node = None)
    uid_list = [x.uid for x in uid_list]
    if len(uid_list)>0:
      activity_tool.SQLDict_delMessage(uid = uid_list)

  # Registration management
  def registerActivityBuffer(self, activity_buffer):
    pass

  def isMessageRegistered(self, activity_buffer, activity_tool, m):
    uid_set = activity_buffer.getUidSet(self)
    return (tuple(m.object_path), m.method_id, m.activity_kw.get('tag'), m.activity_kw.get('group_id')) in uid_set

  def registerMessage(self, activity_buffer, activity_tool, m):
    m.is_registered = 1
    uid_set = activity_buffer.getUidSet(self)
    uid_set.add((tuple(m.object_path), m.method_id, m.activity_kw.get('tag'), m.activity_kw.get('group_id')))
    message_list = activity_buffer.getMessageList(self)
    message_list.append(m)

  def unregisterMessage(self, activity_buffer, activity_tool, m):
    m.is_registered = 0 # This prevents from inserting deleted messages into the queue
    class_name = self.__class__.__name__
    uid_set = activity_buffer.getUidSet(self)
    uid_set.discard((tuple(m.object_path), m.method_id, m.activity_kw.get('tag'), m.activity_kw.get('group_id')))

  def getRegisteredMessageList(self, activity_buffer, activity_tool):
    message_list = activity_buffer.getMessageList(self)
    return [m for m in message_list if m.is_registered]
  
  def validateMessage(self, activity_tool, message, uid_list, priority, processing_node):
    validation_state = message.validate(self, activity_tool, check_order_validation=0)
    if validation_state is not VALID:
      # There is a serious validation error - we must lower priority
      if priority > MAX_PRIORITY:
        # This is an error
        if len(uid_list) > 0:
          activity_tool.SQLDict_assignMessage(uid=uid_list, processing_node=VALIDATE_ERROR_STATE)
                                                                          # Assign message back to 'error' state
        #m.notifyUser(activity_tool)                                      # Notify Error
        get_transaction().commit()                                        # and commit
      else:
        # Lower priority
        if len(uid_list) > 0: # Add some delay before new processing
          activity_tool.SQLDict_setPriority(uid=uid_list, delay=VALIDATION_ERROR_DELAY,
                                            priority=priority + 1, retry=1)
        get_transaction().commit() # Release locks before starting a potentially long calculation
      return 0
    return 1

  def getReservedMessageList(self, activity_tool, date, processing_node, limit=None, **kw):
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
    result = activity_tool.SQLDict_selectReservedMessageList(processing_node=processing_node, limit=limit)
    if len(result) == 0:
      activity_tool.SQLDict_reserveMessageList(limit=limit, processing_node=processing_node, to_date=date, **kw)
      result = activity_tool.SQLDict_selectReservedMessageList(processing_node=processing_node, limit=limit)
    return result

  def makeMessageListAvailable(self, activity_tool, uid_list):
    """
      Put messages back in processing_node=0 .
    """
    if len(uid_list):
      activity_tool.SQLDict_makeMessageListAvailable(uid_list=uid_list)

  def deleteDuplicatedLineList(self, activity_tool, date, processing_node, line):
    """
      Delete all messages matching given one except itself.
      Operator  Value
      !=        uid
      <=        date
      =         path, method_id, group_method_id, order_validation_text,
                processing_node, tag
    """
    activity_tool.SQLDict_deleteDuplicatedMessageList(
      processing_node=processing_node, uid=line.uid,
      to_date=line.date, path=line.path, method_id=line.method_id,
      group_method_id=line.group_method_id,
      order_validation_text=line.order_validation_text,
      tag=line.tag)

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
      - return still-reserved message list and a group_method_id

      If any error happens in above described process, try to unreserve all
      messages already reserved in that process.
      If it fails, complain loudly that some messages might still be in an
      unclean state.

      Returned values:
        3-tuple:
          - list of 3-tuple:
            - message uid
            - message
            - priority
          - impacted object count
          - group_method_id
    """
    def getReservedMessageList(**kw):
      line_list = self.getReservedMessageList(activity_tool=activity_tool,
                                              date=now_date,
                                              processing_node=processing_node,
                                              **kw)
      if len(line_list):
        LOG('SQLDict', TRACE, 'Reserved messages: %r' % ([x.uid for x in line_list]))
      return line_list
    def deleteDuplicatedLineList(line):
      self.deleteDuplicatedLineList(activity_tool=activity_tool, date=now_date,
                                 processing_node=processing_node, line=line)
    def makeMessageListAvailable(uid_list):
      self.makeMessageListAvailable(activity_tool=activity_tool, uid_list=uid_list)
    BUNDLE_MESSAGE_COUNT = 100 # Arbitrary number
    now_date = self.getNow(activity_tool)
    message_list = []
    def append(line, message):
      uid = line.uid
      message_list.append((uid, message, line.priority))
    count = 0
    group_method_id = None
    try:
      result = getReservedMessageList(limit=1)
      if len(result) > 0:
        line = result[0]
        m = self.loadMessage(line.message, uid=line.uid)
        append(line, m)
        group_method_id = line.group_method_id
        # Delete all messages matching current one - except current one.
        deleteDuplicatedLineList(line)
        activity_tool.SQLDict_processMessage(uid=[line.uid])
        if group_method_id not in (None, '', '\0'):
          # Count the number of objects to prevent too many objects.
          count += len(m.getObjectList(activity_tool))
          if count < MAX_GROUPED_OBJECTS:
            # Retrieve objects which have the same group method.
            result = getReservedMessageList(limit=BUNDLE_MESSAGE_COUNT, group_method_id=group_method_id)
            path_and_method_id_dict = {}
            unreserve_uid_list = []
            for line in result:
              # All fetched lines have the same group_method_id and
              # processing_node.
              # Their dates are lower-than or equal-to now_date.
              # We read each line once so lines have distinct uids.
              # So what remains to be filtered on are path, method_id,
              # order_validation_text, tag
              key = (line.path, line.method_id, line.order_validation_text, line.tag)
              if key in path_and_method_id_dict:
                LOG('SQLDict', TRACE, 'Duplicate of message %r has been skipped (it should already be deleted anyway): %r' % (path_and_method_id_dict[key], line.uid))
                continue
              path_and_method_id_dict[key] = line.uid
              deleteDuplicatedLineList(line)
              if count < MAX_GROUPED_OBJECTS:
                m = self.loadMessage(line.message, uid=line.uid)
                count += len(m.getObjectList(activity_tool))
                append(line, m)
              else:
                unreserve_uid_list.append(line.uid)
            activity_tool.SQLDict_processMessage(uid=[x[0] for x in message_list])
            # Unreserve extra messages as soon as possible.
            makeMessageListAvailable(unreserve_uid_list)
      return message_list, count, group_method_id
    except:
      LOG('SQLDict', WARNING, 'Exception while reserving messages.', error=sys.exc_info())
      if len(message_list):
        to_free_uid_list = [x[0] for x in message_list]
        try:
          makeMessageListAvailable(to_free_uid_list)
        except:
          LOG('SQLDict', PANIC, 'Failed to free messages: %r' % (to_free_uid_list, ), error=sys.exc_info())
        else:
          if len(to_free_uid_list):
            LOG('SQLDict', TRACE, 'Freed messages %r' % (to_free_uid_list, ))
      else:
        LOG('SQLDict', TRACE, '(no message was reserved)')
      return [], 0, None

  def finalizeMessageExecution(self, activity_tool, message_uid_priority_list):
    def makeMessageListAvailable(uid_list):
      self.makeMessageListAvailable(activity_tool=activity_tool, uid_list=uid_list)
    deletable_uid_list = []
    delay_uid_list = []
    final_error_uid_list = []
    message_with_active_process_list = []
    for uid, m, priority in message_uid_priority_list:
      if m.is_executed:
        deletable_uid_list.append(uid)
        if m.active_process:
          message_with_active_process_list.append(m)
      else:
        if type(m.exc_type) is ClassType and \
           issubclass(m.exc_type, ConflictError):
          delay_uid_list.append(uid)
        elif priority > MAX_PRIORITY:
          final_error_uid_list.append(uid)
        else:
          try:
            # Immediately update, because values different for every message
            activity_tool.SQLDict_setPriority(
              uid=[uid],
              delay=VALIDATION_ERROR_DELAY,
              priority=priority + 1)
          except:
            LOG('SQLDict', WARNING, 'Failed to increase priority of %r' % (uid, ), error=sys.exc_info())
          try:
            makeMessageListAvailable(delay_uid_list)
          except:
            LOG('SQLDict', PANIC, 'Failed to unreserve %r' % (uid, ), error=sys.exc_info())
          else:
            LOG('SQLDict', TRACE, 'Freed message %r' % (uid, ))
    if len(deletable_uid_list):
      try:
        activity_tool.SQLDict_delMessage(uid=deletable_uid_list)
      except:
        LOG('SQLDict', PANIC, 'Failed to delete messages %r' % (deletable_uid_list, ), error=sys.exc_info())
      else:
        LOG('SQLDict', TRACE, 'Deleted messages %r' % (deletable_uid_list, ))
    if len(delay_uid_list):
      try:
        # If this is a conflict error, do not lower the priority but only delay.
        activity_tool.SQLDict_setPriority(uid=delay_uid_list, delay=VALIDATION_ERROR_DELAY)
      except:
        LOG('SQLDict', TRACE, 'Failed to delay %r' % (delay_uid_list, ), error=sys.exc_info())
      try:
        makeMessageListAvailable(delay_uid_list)
      except:
        LOG('SQLDict', PANIC, 'Failed to unreserve %r' % (delay_uid_list, ), error=sys.exc_info())
      else:
        LOG('SQLDict', TRACE, 'Freed messages %r' % (delay_uid_list, ))
    if len(final_error_uid_list):
      try:
        activity_tool.SQLDict_assignMessage(uid=final_error_uid_list,
                                            processing_node=INVOKE_ERROR_STATE)
      except:
        LOG('SQLDict', WARNING, 'Failed to set message to error state for %r' % (final_error_uid_list, ), error=sys.exc_info())
    for m in message_with_active_process_list:
      active_process = activity_tool.unrestrictedTraverse(m.active_process)
      if not active_process.hasActivity():
        # No more activity
        m.notifyUser(activity_tool, message="Process Finished") # XXX commit bas ???

  # Queue semantic
  def dequeueMessage(self, activity_tool, processing_node):
    def makeMessageListAvailable(uid_list):
      self.makeMessageListAvailable(activity_tool=activity_tool, uid_list=uid_list)
    message_uid_priority_list, count, group_method_id = \
      self.getProcessableMessageList(activity_tool, processing_node)
    if len(message_uid_priority_list):
      # Remove group_id parameter from group_method_id
      if group_method_id is not None:
        group_method_id = group_method_id.split('\0')[0]
      message_list = [x[1] for x in message_uid_priority_list]
      if group_method_id not in (None, ""):
        method  = activity_tool.invokeGroup
        args = (group_method_id, message_list)
      else:
        method = activity_tool.invoke
        args = (message_list[0], )
      try:
        # Commit right before executing messages.
        # As MySQL transaction do no start exactly at the same time as ZODB
        # transactions but a bit later, messages available might be called
        # on objects which are not available - or available in an old
        # version - to ZODB connector.
        # So all connectors must be commited now that we have selected
        # everything needed from MySQL to get a fresh view of ZODB objects.
        get_transaction().commit() 
        # Try to invoke
        method(*args)
      except:
        LOG('SQLDict', WARNING, 'Exception raised when invoking messages (uid, path, method_id) %r' % ([(x[0], x[1].object_path, x[1].method_id) for x in message_uid_priority_list], ), error=sys.exc_info())
        to_free_uid_list = [x[0] for x in message_uid_priority_list]
        try:
          makeMessageListAvailable(to_free_uid_list)
        except:
          LOG('SQLDict', PANIC, 'Failed to free messages: %r' % (to_free_uid_list, ), error=sys.exc_info())
        else:
          LOG('SQLDict', TRACE, 'Freed messages %r' % (to_free_uid_list))
        try:
          abortTransactionSynchronously()
        except:
          # Unfortunately, database adapters may raise an exception against abort.
          LOG('SQLDict', PANIC,
              'abort failed, thus some objects may be modified accidentally')
          return True # Stop processing messages for this tic call for this queue.
      # Only abort if nothing succeeded.
      # This means that when processing multiple messages, failed ones must not cause
      # bad things to happen if transaction is commited.
      if len([x for x in message_uid_priority_list if x[1].is_executed]) == 0:
        endTransaction = abortTransactionSynchronously
      else:
        endTransaction = get_transaction().commit
      try:
        endTransaction()
      except:
        LOG('SQLDict', WARNING, 'Failed to end transaction for messages (uid, path, method_id) %r' % ([(x[0], x[1].object_path, x[1].method_id) for x in message_uid_priority_list], ), error=sys.exc_info())
        failed_message_uid_list = [x[0] for x in message_uid_priority_list]
        try:
          makeMessageListAvailable(failed_message_uid_list)
        except:
          LOG('SQQueue', PANIC, 'Failed to free remaining messages: %r' % (failed_message_uid_list, ), error=sys.exc_info())
        else:
          LOG('SQQueue', TRACE, 'Freed messages %r' % (failed_message_uid_list, ))
        if endTransaction == abortTransactionSynchronously:
          LOG('SQLDict', PANIC, 'Failed to abort executed messages. Some objects may be modified accidentally.')
        else:
          try:
            abortTransactionSynchronously()
          except:
            LOG('SQLDict', PANIC, 'Failed to abort executed messages which also failed to commit. Some objects may be modified accidentally.')
        return True # Stop processing messages for this tic call for this queue.
      self.finalizeMessageExecution(activity_tool, message_uid_priority_list)
    get_transaction().commit()
    return not len(message_uid_priority_list)

  def hasActivity(self, activity_tool, object, **kw):
    hasMessage = getattr(activity_tool, 'SQLDict_hasMessage', None)
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
    path = '/'.join(object_path)
    # LOG('Flush', 0, str((path, invoke, method_id)))
    method_dict = {}
    readMessageList = getattr(activity_tool, 'SQLDict_readMessageList', None)
    if readMessageList is not None:
      # Parse each message in registered
      for m in activity_tool.getRegisteredMessageList(self):
        if m.object_path == object_path and (method_id is None or method_id == m.method_id):
          #if not method_dict.has_key(method_id or m.method_id):
          if not method_dict.has_key(m.method_id):
            method_dict[m.method_id] = 1 # Prevents calling invoke twice
            if invoke:
              # First Validate
              validate_value = m.validate(self, activity_tool)
              if validate_value is VALID:
                activity_tool.invoke(m) # Try to invoke the message - what happens if invoke calls flushActivity ??
                if not m.is_executed:                                                 # Make sure message could be invoked
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
      # Parse each message in SQL dict
      result = readMessageList(path=path, method_id=method_id,
                               processing_node=None,include_processing=0)
      for line in result:
        path = line.path
        line_method_id = line.method_id
        if not method_dict.has_key(line_method_id):
          # Only invoke once (it would be different for a queue)
          # This is optimisation with the goal to process objects on the same
          # node and minimize network traffic with ZEO server
          method_dict[line_method_id] = 1
          m = self.loadMessage(line.message, uid = line.uid)
          if invoke:
            # First Validate
            validate_value = m.validate(self, activity_tool)
#             LOG('SQLDict.flush validate_value',0,validate_value)
            if validate_value is VALID:
              activity_tool.invoke(m) # Try to invoke the message - what happens if invoke calls flushActivity ??
#               LOG('SQLDict.flush m.is_executed',0,m.is_executed)
              if not m.is_executed:                                                 # Make sure message could be invoked
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

      if len(result):
        uid_list = activity_tool.SQLDict_readUidList(path = path, method_id = method_id,
                                                     processing_node = None,)
        if len(uid_list)>0:
          activity_tool.SQLDict_delMessage(uid = [x.uid for x in uid_list])

  def getMessageList(self, activity_tool, processing_node=None, include_processing=0, **kw):
    # YO: reading all lines might cause a deadlock
    message_list = []
    readMessageList = getattr(activity_tool, 'SQLDict_readMessageList', None)
    if readMessageList is not None:
      result = readMessageList(path=None, method_id=None, processing_node=None,
                               to_processing_date=None, include_processing=include_processing)
      for line in result:
        m = self.loadMessage(line.message, uid = line.uid)
        m.processing_node = line.processing_node
        m.priority = line.priority
        m.processing = line.processing
        message_list.append(m)
    return message_list

  def dumpMessageList(self, activity_tool):
    # Dump all messages in the table.
    message_list = []
    dumpMessageList = getattr(activity_tool, 'SQLDict_dumpMessageList', None)
    if dumpMessageList is not None:
      result = dumpMessageList()
      for line in result:
        m = self.loadMessage(line.message, uid = line.uid)
        message_list.append(m)
    return message_list

  def distribute(self, activity_tool, node_count):
    offset = 0
    readMessageList = getattr(activity_tool, 'SQLDict_readMessageList', None)
    if readMessageList is not None:
      now_date = self.getNow(activity_tool)
      result = readMessageList(path=None, method_id=None, processing_node=-1,
                               to_date=now_date, include_processing=0, offset=offset, count=READ_MESSAGE_LIMIT)
      validated_count = 0
      #TIME_begin = time()
      while len(result) and validated_count < MAX_VALIDATED_LIMIT:
        get_transaction().commit()

        validation_text_dict = {'none': 1}
        message_dict = {}
        for line in result:
          message = self.loadMessage(line.message, uid = line.uid,
                                     order_validation_text = line.order_validation_text)
          self.getExecutableMessageList(activity_tool, message, message_dict,
                                        validation_text_dict, now_date=now_date)
        distributable_count = len(message_dict)
        if distributable_count:
          activity_tool.SQLDict_assignMessage(processing_node=0, uid=[message.uid for message in message_dict.itervalues()])
          validated_count += distributable_count
        if validated_count < MAX_VALIDATED_LIMIT:
          offset += READ_MESSAGE_LIMIT
          result = readMessageList(path=None, method_id=None, processing_node=-1,
                                   to_date=now_date, include_processing=0, offset=offset, count=READ_MESSAGE_LIMIT)
      #TIME_end = time()
      #LOG('SQLDict.distribute', INFO, '%0.4fs : %i messages => %i distributables' % (TIME_end - TIME_begin, offset - READ_MESSAGE_LIMIT + len(result), validated_count))

  # Validation private methods
  def _validate(self, activity_tool, method_id=None, message_uid=None, path=None, tag=None):
    if isinstance(method_id, str):
      method_id = [method_id]
    if isinstance(path, str):
      path = [path]
    if isinstance(tag, str):
      tag = [tag]

    if method_id or message_uid or path or tag:
      validateMessageList = activity_tool.SQLDict_validateMessageList
      result = validateMessageList(method_id=method_id,
                                   message_uid=message_uid,
                                   path=path,
                                   tag=tag)
      message_list = []
      for line in result:
        m = self.loadMessage(line.message,
                             uid=line.uid,
                             order_validation_text=line.order_validation_text,
                             date=line.date,
                             processing_node=line.processing_node)
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
    if not isinstance(value, (tuple, list)) or len(value) < 2:
      LOG('CMFActivity', WARNING,
          'unable to recognize value for after_path_and_method_id: %r' % (value,))
      return []
    return self._validate(activity_tool, path=value[0], method_id=value[1])

  def _validate_after_tag(self, activity_tool, message, value):
    return self._validate(activity_tool, tag=value)

  def _validate_after_tag_and_method_id(self, activity_tool, message, value):
    # Count number of occurances of tag and method_id
    if not isinstance(value, (tuple, list)) or len(value) < 2:
      LOG('CMFActivity', WARNING,
          'unable to recognize value for after_tag_and_method_id: %r' % (value,))
      return []
    return self._validate(activity_tool, tag=value[0], method_id=value[1])

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
    result = activity_tool.SQLDict_validateMessageList(method_id=method_id, 
                                                       path=path,
                                                       message_uid=message_uid, 
                                                       tag=tag,
                                                       count=1)
    return result[0].uid_count

  def countMessageWithTag(self, activity_tool, value):
    """Return the number of messages which match the given tag.
    """
    return self.countMessage(activity_tool, tag=value)

  # Required for tests (time shift)
  def timeShift(self, activity_tool, delay, processing_node=None, retry=None):
    """
      To simulate timeShift, we simply substract delay from
      all dates in SQLDict message table
    """
    activity_tool.SQLDict_timeShift(delay=delay, processing_node=processing_node,retry=retry)

registerActivity(SQLDict)
