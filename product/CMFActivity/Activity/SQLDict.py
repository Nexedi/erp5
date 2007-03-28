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

import random
from DateTime import DateTime
from Products.CMFActivity.ActivityTool import registerActivity
from Queue import VALID, INVALID_ORDER, INVALID_PATH, EXCEPTION, MAX_PROCESSING_TIME, VALIDATION_ERROR_DELAY
from RAMDict import RAMDict
from Products.CMFActivity.ActiveObject import DISTRIBUTABLE_STATE, INVOKE_ERROR_STATE, VALIDATE_ERROR_STATE
from Products.CMFActivity.Errors import ActivityFlushError
from ZODB.POSException import ConflictError
import sys
import sha
from types import ClassType, StringType, ListType, TupleType

try:
  from transaction import get as get_transaction
except ImportError:
  pass

from zLOG import LOG, TRACE, WARNING, ERROR

MAX_PRIORITY = 5
MAX_GROUPED_OBJECTS = 500

priority_weight = \
  [1] * 64 + \
  [2] * 20 + \
  [3] * 10 + \
  [4] * 5 + \
  [5] * 1


class SQLDict(RAMDict):
  """
    A simple OOBTree based queue. It should be compatible with transactions
    and provide sequentiality. Should not create conflict
    because use of OOBTree.
  """
  # Transaction commit methods
  def prepareQueueMessage(self, activity_tool, m):
    if m.is_registered:
      activity_tool.SQLDict_writeMessage( path = '/'.join(m.object_path) ,
                                          method_id = m.method_id,
                                          priority = m.activity_kw.get('priority', 1),
                                          broadcast = m.activity_kw.get('broadcast', 0),
                                          message = self.dumpMessage(m),
                                          date = m.activity_kw.get('at_date', DateTime()),
                                          group_method_id = m.activity_kw.get('group_method_id', ''),
                                          tag = m.activity_kw.get('tag', ''),
                                          order_validation_text = self.getOrderValidationText(m))
                                          # Also store uid of activity

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
      broadcast_list = [message.activity_kw.get('broadcast', 0) for message in registered_message_list]
      dumped_message_list = [self.dumpMessage(message) for message in registered_message_list]
      datetime = DateTime()
      date_list = [message.activity_kw.get('at_date', datetime) for message in registered_message_list]
      group_method_id_list = [message.activity_kw.get('group_method_id', '') for message in registered_message_list]
      tag_list = [message.activity_kw.get('tag', '') for message in registered_message_list]
      order_validation_text_list = [self.getOrderValidationText(message) for message in registered_message_list]
      uid_list = activity_tool.getPortalObject().portal_ids.generateNewLengthIdList(id_group='portal_activity', id_count=len(registered_message_list))
      activity_tool.SQLDict_writeMessageList( uid_list = uid_list,
                                              path_list = path_list,
                                              method_id_list = method_id_list,
                                              priority_list = priority_list,
                                              broadcast_list = broadcast_list,
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
    return (tuple(m.object_path), m.method_id, m.activity_kw.get('tag')) in uid_set

  def registerMessage(self, activity_buffer, activity_tool, m):
    m.is_registered = 1
    uid_set = activity_buffer.getUidSet(self)
    uid_set.add((tuple(m.object_path), m.method_id, m.activity_kw.get('tag')))
    message_list = activity_buffer.getMessageList(self)
    message_list.append(m)

  def unregisterMessage(self, activity_buffer, activity_tool, m):
    m.is_registered = 0 # This prevents from inserting deleted messages into the queue
    class_name = self.__class__.__name__
    uid_set = activity_buffer.getUidSet(self)
    uid_set.discard((tuple(m.object_path), m.method_id, m.activity_kw.get('tag')))

  def getRegisteredMessageList(self, activity_buffer, activity_tool):
    message_list = activity_buffer.getMessageList(self)
    return [m for m in message_list if m.is_registered]

  def getOrderValidationText(self, message):
    # Return an identifier of validators related to ordering.
    order_validation_item_list = []
    key_list = message.activity_kw.keys()
    key_list.sort()
    for key in key_list:
      method_id = "_validate_%s" % key
      if hasattr(self, method_id):
        order_validation_item_list.append((key, message.activity_kw[key]))
    if len(order_validation_item_list) == 0:
      # When no order validation argument is specified, skip the computation
      # of the checksum for speed. Here, 'none' is used, because this never be
      # identical to SHA1 hexdigest (which is always 40 characters), and 'none'
      # is true in Python. This is important, because dtml-if assumes that an empty
      # string is false, so we must use a non-empty string for this.
      return 'none'
    return sha.new(repr(order_validation_item_list)).hexdigest()

  def validateMessage(self, activity_tool, message, uid_list, priority, processing_node):
    validation_state = message.validate(self, activity_tool)
    if validation_state is not VALID:
      if validation_state in (EXCEPTION, INVALID_PATH):
        # There is a serious validation error - we must lower priority
        if priority > MAX_PRIORITY:
          # This is an error
          if len(uid_list) > 0:
            activity_tool.SQLDict_assignMessage(uid = uid_list, processing_node = VALIDATE_ERROR_STATE)
                                                                            # Assign message back to 'error' state
          #m.notifyUser(activity_tool)                                      # Notify Error
          get_transaction().commit()                                        # and commit
        else:
          # Lower priority
          if len(uid_list) > 0: # Add some delay before new processing
            activity_tool.SQLDict_setPriority(uid = uid_list, delay = VALIDATION_ERROR_DELAY,
                                              priority = priority + 1, retry = 1)
          get_transaction().commit() # Release locks before starting a potentially long calculation
      else:
        # We do not lower priority for INVALID_ORDER errors but we do postpone execution
        order_validation_text = self.getOrderValidationText(message)
        activity_tool.SQLDict_setPriority(order_validation_text = order_validation_text, 
                                          processing_node = processing_node,
                                          delay = VALIDATION_ERROR_DELAY,
                                          retry = 1,
                                          uid = None)
        get_transaction().commit() # Release locks before starting a potentially long calculation
      return 0
    return 1

  # Queue semantic
  def dequeueMessage(self, activity_tool, processing_node):
    readMessage = getattr(activity_tool, 'SQLDict_readMessage', None)
    if readMessage is None:
      return 1

    now_date = DateTime()
    priority = random.choice(priority_weight)
    # Try to find a message at given priority level which is scheduled for now
    result = readMessage(processing_node=processing_node, priority=priority,
                         to_date=now_date)
    if len(result) == 0:
      # If empty, take any message which is scheduled for now
      priority = None
      result = readMessage(processing_node=processing_node, priority=priority, to_date=now_date)
    if len(result) == 0:
      # If the result is still empty, shift the dates so that SQLDict can dispatch pending active
      # objects quickly.
      self.timeShift(activity_tool, VALIDATION_ERROR_DELAY, processing_node,retry=1)
    else:
      #LOG('SQLDict dequeueMessage', 100, 'result = %r' % (list(result)))
      line = result[0]
      path = line.path
      method_id = line.method_id
      order_validation_text = line.order_validation_text
      uid_list = activity_tool.SQLDict_readUidList(path = path, method_id = method_id,
                                                   processing_node = None, to_date = now_date,
                                                   order_validation_text = order_validation_text)
      uid_list = [x.uid for x in uid_list]
      uid_list_list = [uid_list]
      priority_list = [line.priority]
      # Make sure message can not be processed anylonger
      if len(uid_list) > 0:
        # Set selected messages to processing
        activity_tool.SQLDict_processMessage(uid = uid_list)
      get_transaction().commit() # Release locks before starting a potentially long calculation
      # This may lead (1 for 1,000,000 in case of reindexing) to messages left in processing state

      # At this point, messages are marked as processed. So catch any kind of exception to make sure
      # that they are unmarked on error.
      try:
        m = self.loadMessage(line.message, uid = line.uid)
        message_list = [m]
        # Validate message (make sure object exists, priority OK, etc.)
        if not self.validateMessage(activity_tool, m, uid_list, line.priority, processing_node):
          return 0

        group_method_id = m.activity_kw.get('group_method_id')
        if group_method_id is not None:
          # Count the number of objects to prevent too many objects.
          if m.hasExpandMethod():
            count = len(m.getObjectList(activity_tool))
          else:
            count = 1

          group_method = activity_tool.restrictedTraverse(group_method_id)

          if count < MAX_GROUPED_OBJECTS:
            # Retrieve objects which have the same group method.
            result = readMessage(processing_node = processing_node, priority = priority,
                                to_date = now_date, group_method_id = group_method_id,
                                order_validation_text = order_validation_text)
            #LOG('SQLDict dequeueMessage', 0, 'result = %d' % (len(result)))
            path_and_method_id_dict = {}
            for line in result:
              path = line.path
              method_id = line.method_id

              # Prevent using the same pair of a path and a method id.
              key = (path, method_id)
              if key in path_and_method_id_dict:
                continue
              path_and_method_id_dict[key] = 1

              uid_list = activity_tool.SQLDict_readUidList(path = path, method_id = method_id,
                                                            processing_node = None, to_date = now_date,
                                                            order_validation_text = order_validation_text)
              uid_list = [x.uid for x in uid_list]
              if len(uid_list) > 0:
                # Set selected messages to processing
                activity_tool.SQLDict_processMessage(uid = uid_list)
              get_transaction().commit() # Release locks before starting a potentially long calculation

              # Save this newly marked uids as soon as possible.
              uid_list_list.append(uid_list)

              m = self.loadMessage(line.message, uid = line.uid)
              if self.validateMessage(activity_tool, m, uid_list, line.priority, processing_node):
                if m.hasExpandMethod():
                  count += len(m.getObjectList(activity_tool))
                else:
                  count += 1
                message_list.append(m)
                priority_list.append(line.priority)
                if count >= MAX_GROUPED_OBJECTS:
                  break
              else:
                # If the uids were not valid, remove them from the list, as validateMessage
                # unmarked them.
                uid_list_list.pop()

          # Release locks before starting a potentially long calculation
          get_transaction().commit()

        # Try to invoke
        if group_method_id is not None:
          LOG('SQLDict', TRACE,
              'invoking a group method %s with %d objects '\
              ' (%d objects in expanded form)' % (
              group_method_id, len(message_list), count))
          activity_tool.invokeGroup(group_method_id, message_list)
        else:
          activity_tool.invoke(message_list[0])

        # Check if messages are executed successfully.
        # When some of them are executed successfully, it may not be acceptable to
        # abort the transaction, because these remain pending, only due to other
        # invalid messages. This means that a group method should not be used if
        # it has a side effect. For now, only indexing uses a group method, and this
        # has no side effect.
        for m in message_list:
          if m.is_executed:
            get_transaction().commit()
            break
        else:
          get_transaction().abort()
      except:
        # If an exception occurs, abort the transaction to minimize the impact,
        try:
          get_transaction().abort()
        except:
          # Unfortunately, database adapters may raise an exception against abort.
          LOG('SQLDict', WARNING, 'abort failed, thus some objects may be modified accidentally')
          pass

        # An exception happens at somewhere else but invoke or invokeGroup, so messages
        # themselves should not be delayed.
        try:
          for uid_list in uid_list_list:
            if len(uid_list):
              # This only sets processing to zero.
              activity_tool.SQLDict_setPriority(uid = uid_list)
              get_transaction().commit()
        except:
          LOG('SQLDict', ERROR, 'SQLDict.dequeueMessage raised, and cannot even set processing to zero due to an exception',
              error=sys.exc_info())
          raise
        return 0

      try:
        for i in xrange(len(message_list)):
          m = message_list[i]
          uid_list = uid_list_list[i]
          priority = priority_list[i]
          if m.is_executed:
            if len(uid_list) > 0:
              activity_tool.SQLDict_delMessage(uid = uid_list)                # Delete it
            get_transaction().commit()                                        # If successful, commit
            if m.active_process:
              active_process = activity_tool.unrestrictedTraverse(m.active_process)
              if not active_process.hasActivity():
                # No more activity
                m.notifyUser(activity_tool, message="Process Finished") # XXX commit bas ???
          else:
            if type(m.exc_type) is ClassType and issubclass(m.exc_type, ConflictError):
              # If this is a conflict error, do not lower the priority but only delay.
              activity_tool.SQLDict_setPriority(uid = uid_list, delay = VALIDATION_ERROR_DELAY,
                                                retry = 1)
              get_transaction().commit() # Release locks before starting a potentially long calculation
            elif priority > MAX_PRIORITY:
              # This is an error
              if len(uid_list) > 0:
                activity_tool.SQLDict_assignMessage(uid = uid_list, processing_node = INVOKE_ERROR_STATE)
                                                                                # Assign message back to 'error' state
              m.notifyUser(activity_tool)                                       # Notify Error
              get_transaction().commit()                                        # and commit
            else:
              # Lower priority
              if len(uid_list) > 0:
                activity_tool.SQLDict_setPriority(uid = uid_list, delay = VALIDATION_ERROR_DELAY,
                                                  priority = priority + 1, retry = 1)
                get_transaction().commit() # Release locks before starting a potentially long calculation
      except:
        LOG('SQLDict', ERROR, 'SQLDict.dequeueMessage raised an exception during checking for the results of processed messages',
            error=sys.exc_info())
        raise

      return 0
    get_transaction().commit() # Release locks before starting a potentially long calculation
    return 1

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
        if list(m.object_path) == list(object_path) and (method_id is None or method_id == m.method_id):
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

  def getMessageList(self, activity_tool, processing_node=None,include_processing=0,**kw):
    # YO: reading all lines might cause a deadlock
    message_list = []
    readMessageList = getattr(activity_tool, 'SQLDict_readMessageList', None)
    if readMessageList is not None:
      result = readMessageList(path=None, method_id=None, processing_node=None,
                               to_processing_date=None,include_processing=include_processing)
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
    processing_node = 1
    readMessageList = getattr(activity_tool, 'SQLDict_readMessageList', None)
    if readMessageList is not None:
      now_date = DateTime()
      if (now_date - self.max_processing_date) > MAX_PROCESSING_TIME:
        # Sticky processing messages should be set back to non processing
        max_processing_date = now_date - MAX_PROCESSING_TIME
        self.max_processing_date = now_date
      else:
        max_processing_date = None
      result = readMessageList(path=None, method_id=None, processing_node = -1,
                               to_processing_date = max_processing_date,
                               include_processing=0) # Only assign non assigned messages
      get_transaction().commit() # Release locks before starting a potentially long calculation
      path_dict = {}
      for line in result:
        path = line.path
        broadcast = line.broadcast
        if broadcast:
          # Broadcast messages must be distributed into all nodes.
          uid = line.uid
          activity_tool.SQLDict_assignMessage(processing_node=1, uid=[uid])
          if node_count > 1:
            uid_list = activity_tool.getPortalObject().portal_ids.generateNewLengthIdList(id_group='portal_activity', id_count=node_count - 1)
            for node in range(2, node_count+1):
              activity_tool.SQLDict_writeMessage( uid = uid_list.pop(),
                                                  path = path,
                                                  method_id = line.method_id,
                                                  priority = line.priority,
                                                  broadcast = 1,
                                                  processing_node = node,
                                                  message = line.message,
                                                  date = line.date)
        elif not path_dict.has_key(path):
          # Only assign once (it would be different for a queue)
          path_dict[path] = 1
          activity_tool.SQLDict_assignMessage(path=path, processing_node=processing_node, uid=None, broadcast=0)
          get_transaction().commit() # Release locks immediately to allow processing of messages
          processing_node = processing_node + 1
          if processing_node > node_count:
            processing_node = 1 # Round robin

  # Validation private methods
  def _validate_after_method_id(self, activity_tool, message, value):
    # Count number of occurances of method_id
    if type(value) is StringType:
      value = [value]
    if len(value)>0: # if empty list provided, the message is valid
      result = activity_tool.SQLDict_validateMessageList(method_id=value, message_uid=None, path=None)
      if result[0].uid_count > 0:
        return INVALID_ORDER
    return VALID

  def _validate_after_path(self, activity_tool, message, value):
    # Count number of occurances of path
    if type(value) is StringType:
      value = [value]
    if len(value)>0: # if empty list provided, the message is valid
      result = activity_tool.SQLDict_validateMessageList(method_id=None, message_uid=None, path=value)
      if result[0].uid_count > 0:
        return INVALID_ORDER
    return VALID

  def _validate_after_message_uid(self, activity_tool, message, value):
    # Count number of occurances of message_uid
    result = activity_tool.SQLDict_validateMessageList(method_id=None, message_uid=value, path=None)
    if result[0].uid_count > 0:
      return INVALID_ORDER
    return VALID

  def _validate_after_path_and_method_id(self, activity_tool, message, value):
    # Count number of occurances of path and method_id
    if (type(value) != TupleType and type(value) != ListType) or len(value)<2:
      LOG('CMFActivity WARNING :', 0, 'unable to recognize value for after_path_and_method_id : %s' % repr(value))
      return VALID
    path = value[0]
    method = value[1]
    if type(path) is StringType:
      path = [path]
    if type(method) is StringType:
      method = [method]
    result = activity_tool.SQLDict_validateMessageList(method_id=method, message_uid=None, path=path)
    if result[0].uid_count > 0:
      return INVALID_ORDER
    return VALID

  def _validate_after_tag(self, activity_tool, message, value):
    # Count number of occurances of tag
    if self.countMessageWithTag(activity_tool, value) > 0:
      return INVALID_ORDER
    return VALID

  def countMessage(self, activity_tool, tag=None,path=None,
                   method_id=None,message_uid=None,**kw):
    """
      Return the number of message which match the given parameter.
    """
    if isinstance(tag, StringType):
      tag = [tag]
    if isinstance(path, StringType):
      path = [path]
    if isinstance(message_uid, (int,long)):
      message_uid = [message_uid]
    if isinstance(method_id, StringType):
      method_id = [method_id]
    result = activity_tool.SQLDict_validateMessageList(method_id=method_id, 
                                                       path=path,
                                                       message_uid=message_uid, 
                                                       tag=tag)
    return result[0].uid_count

  def countMessageWithTag(self, activity_tool, value):
    """
      Return the number of message which match the given tag.
    """
    return self.countMessage(activity_tool,tag=value)

  def _validate_after_tag_and_method_id(self, activity_tool, message, value):
    # Count number of occurances of tag and method_id
    if (type(value) != TupleType and type(value) != ListType) or len(value)<2:
      LOG('CMFActivity WARNING :', 0, 'unable to recognize value for after_tag_and_method_id : %s' % repr(value))
      return VALID
    tag = value[0]
    method = value[1]
    if type(tag) is StringType:
      tag = [tag]
    if type(method) is StringType:
      method = [method]
    result = activity_tool.SQLDict_validateMessageList(method_id=method, message_uid=None, tag=tag)
    if result[0].uid_count > 0:
      return INVALID_ORDER
    return VALID

  # Required for tests (time shift)
  def timeShift(self, activity_tool, delay, processing_node=None,retry=None):
    """
      To simulate timeShift, we simply substract delay from
      all dates in SQLDict message table
    """
    activity_tool.SQLDict_timeShift(delay = delay, processing_node = processing_node,retry=retry)

registerActivity(SQLDict)
