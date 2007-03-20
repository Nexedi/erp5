##############################################################################
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
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
from Products.CMFActivity.ActivityTool import registerActivity
from RAMQueue import RAMQueue
from DateTime import DateTime
from Queue import VALID, INVALID_ORDER, INVALID_PATH, EXCEPTION, MAX_PROCESSING_TIME, VALIDATION_ERROR_DELAY
from Products.CMFActivity.ActiveObject import DISTRIBUTABLE_STATE, INVOKE_ERROR_STATE, VALIDATE_ERROR_STATE
from Products.CMFActivity.Errors import ActivityFlushError
from ZODB.POSException import ConflictError
from types import StringType, ClassType
import sys

try:
  from transaction import get as get_transaction
except ImportError:
  pass

from zLOG import LOG, WARNING

MAX_PRIORITY = 5

priority_weight = \
  [1] * 64 + \
  [2] * 20 + \
  [3] * 10 + \
  [4] * 5 + \
  [5] * 1

class SQLQueue(RAMQueue):
  """
    A simple OOBTree based queue. It should be compatible with transactions
    and provide sequentiality. Should not create conflict
    because use of OOBTree.
  """
  def prepareQueueMessage(self, activity_tool, m):
    if m.is_registered:
      activity_tool.SQLQueue_writeMessage(path = '/'.join(m.object_path) ,
                                          method_id = m.method_id,
                                          priority = m.activity_kw.get('priority', 1),
                                          broadcast = m.activity_kw.get('broadcast', 0),
                                          message = self.dumpMessage(m),
                                          date = m.activity_kw.get('at_date', DateTime()),
                                          tag = m.activity_kw.get('tag', ''))

  def prepareDeleteMessage(self, activity_tool, m):
    # Erase all messages in a single transaction
    #LOG("prepareDeleteMessage", 0, str(m.__dict__))
    activity_tool.SQLQueue_delMessage(uid = [m.uid])

  def dequeueMessage(self, activity_tool, processing_node):
    readMessage = getattr(activity_tool, 'SQLQueue_readMessage', None)
    if readMessage is None:
      return 1

    now_date = DateTime()
    # Next processing date in case of error
    next_processing_date = now_date + float(VALIDATION_ERROR_DELAY)/86400
    priority = random.choice(priority_weight)
    # Try to find a message at given priority level
    result = readMessage(processing_node=processing_node, priority=priority,
                         to_date=now_date)
    if len(result) == 0:
      # If empty, take any message
      result = readMessage(processing_node=processing_node, priority=None,to_date=now_date)
    if len(result) > 0:
      line = result[0]
      path = line.path
      method_id = line.method_id
      # Make sure message can not be processed anylonger
      activity_tool.SQLQueue_processMessage(uid=line.uid)
      get_transaction().commit() # Release locks before starting a potentially long calculation

      # At this point, the message is marked as processed.
      try:
        m = self.loadMessage(line.message)
        # Make sure object exists
        validation_state = m.validate(self, activity_tool)
        if validation_state is not VALID:
          if validation_state in (EXCEPTION, INVALID_PATH):
            if line.priority > MAX_PRIORITY:
              # This is an error.
              # Assign message back to 'error' state.
              activity_tool.SQLQueue_assignMessage(uid=line.uid,
                                                   processing_node = VALIDATE_ERROR_STATE)
              get_transaction().commit()                                        # and commit
            else:
              # Lower priority
              activity_tool.SQLQueue_setPriority(uid=line.uid, priority = line.priority + 1)
              get_transaction().commit() # Release locks before starting a potentially long calculation
          else:
            # We do not lower priority for INVALID_ORDER errors but we do postpone execution
            activity_tool.SQLQueue_setPriority(uid = line.uid, date = next_processing_date,
                                                priority = line.priority)
            get_transaction().commit() # Release locks before starting a potentially long calculation
          return 0

        # Try to invoke
        activity_tool.invoke(m) # Try to invoke the message
        if m.is_executed:                                          # Make sure message could be invoked
          get_transaction().commit()                                        # If successful, commit
      except:
        # If an exception occurs, abort the transaction to minimize the impact,
        try:
          get_transaction().abort()
        except:
          # Unfortunately, database adapters may raise an exception against abort.
          LOG('SQLQueue', WARNING, 'abort failed, thus some objects may be modified accidentally')
          pass

        if issubclass(sys.exc_info()[0], ConflictError):
          # If a conflict occurs, delay the operation.
          activity_tool.SQLQueue_setPriority(uid = line.uid, date = next_processing_date,
                                             priority = line.priority)
        else:
          # For the other exceptions, put it into an error state.
          activity_tool.SQLQueue_assignMessage(uid = line.uid, 
                                               processing_node = INVOKE_ERROR_STATE)
          LOG('SQLQueue', WARNING,
              'Error in ActivityTool.invoke', error=sys.exc_info())

        get_transaction().commit()
        return 0


      if m.is_executed:
        activity_tool.SQLQueue_delMessage(uid=[line.uid])  # Delete it
      else:
        try:
          # If not, abort transaction and start a new one
          get_transaction().abort()
        except:
          # Unfortunately, database adapters may raise an exception against abort.
          LOG('SQLQueue', WARNING, 'abort failed, thus some objects may be modified accidentally')
          pass

        if type(m.exc_type) is ClassType \
                and issubclass(m.exc_type, ConflictError):
          activity_tool.SQLQueue_setPriority(uid = line.uid, 
                                             date = next_processing_date,
                                             priority = line.priority)
        elif line.priority > MAX_PRIORITY:
          # This is an error
          activity_tool.SQLQueue_assignMessage(uid = line.uid, 
                                               processing_node = INVOKE_ERROR_STATE)
                                                                            # Assign message back to 'error' state
          m.notifyUser(activity_tool)                                       # Notify Error
        else:
          # Lower priority
          activity_tool.SQLQueue_setPriority(uid=line.uid, date = next_processing_date,
                                              priority = line.priority + 1)
      get_transaction().commit()
      return 0
    get_transaction().commit() # Release locks before starting a potentially long calculation
    return 1

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
          if invoke: activity_tool.invoke(m)
          activity_tool.unregisterMessage(self, m)
      # Parse each message in SQL queue
      #LOG('Flush', 0, str((path, invoke, method_id)))
      result = readMessageList(path=path, method_id=method_id,processing_node=None)
      #LOG('Flush', 0, str(len(result)))
      method_dict = {}
      for line in result:
        path = line.path
        method_id = line.method_id
        if not method_dict.has_key(method_id):
          # Only invoke once (it would be different for a queue)
          method_dict[method_id] = 1
          m = self.loadMessage(line.message, uid = line.uid)
          if invoke:
            # First Validate
            if m.validate(self, activity_tool) is VALID:
              activity_tool.invoke(m) # Try to invoke the message - what happens if invoke calls flushActivity ??
              if not m.is_executed:                                                 # Make sure message could be invoked
                # The message no longer exists
                raise ActivityFlushError, (
                    'Could not evaluate %s on %s' % (method_id , path))
            else:
              # The message no longer exists
              raise ActivityFlushError, (
                  'The document %s does not exist' % path)

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
    result = activity_tool.SQLQueue_validateMessageList(method_id=method_id, 
                                                       path=path,
                                                       message_uid=message_uid, 
                                                       tag=tag)
    return result[0].uid_count

  def countMessageWithTag(self, activity_tool, value):
    """
      Return the number of message which match the given tag.
    """
    return self.countMessage(activity_tool,tag=value)


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
    processing_node = 1
    readMessageList = getattr(activity_tool, 'SQLQueue_readMessageList', None)
    if readMessageList is not None:
      result = readMessageList(path=None, method_id=None, processing_node = -1) # Only assign non assigned messages
      #LOG('distribute count',0,str(len(result)) )
      #LOG('distribute count',0,str(map(lambda x:x.uid, result)))
      #get_transaction().commit() # Release locks before starting a potentially long calculation
      result = list(result)[0:100]
      for line in result:
        broadcast = line.broadcast
        uid = line.uid
        if broadcast:
          # Broadcast messages must be distributed into all nodes.
          activity_tool.SQLQueue_assignMessage(processing_node=1, uid=uid)
          if node_count > 1:
            for node in range(2, node_count+1):
              activity_tool.SQLQueue_writeMessage( path = line.path,
                                                  method_id = line.method_id,
                                                  priority = line.priority,
                                                  broadcast = 1,
                                                  processing_node = node,
                                                  message = line.message,
                                                  date = line.date)
        else:
          #LOG("distribute", 0, "assign %s" % uid)
          activity_tool.SQLQueue_assignMessage(uid=uid, processing_node=processing_node)
          #get_transaction().commit() # Release locks immediately to allow processing of messages
          processing_node = processing_node + 1
          if processing_node > node_count:
            processing_node = 1 # Round robin

  # Validation private methods
  def _validate_after_method_id(self, activity_tool, message, value):
    # Count number of occurances of method_id
    #get_transaction().commit()
    if type(value) == type(''):
      value = [value]
    result = activity_tool.SQLQueue_validateMessageList(method_id=value, message_uid=None, path=None)
    #LOG('SQLQueue._validate_after_method_id, method_id',0,value)
    #LOG('SQLQueue._validate_after_method_id, result[0].uid_count',0,result[0].uid_count)
    if result[0].uid_count > 0:
      return INVALID_ORDER
    return VALID

  def _validate_after_path(self, activity_tool, message, value):
    # Count number of occurances of path
    if type(value) == type(''):
      value = [value]
    result = activity_tool.SQLQueue_validateMessageList(method_id=None, message_uid=None, path=value)
    if result[0].uid_count > 0:
      return INVALID_ORDER
    return VALID

  def _validate_after_message_uid(self, activity_tool, message, value):
    # Count number of occurances of message_uid
    result = activity_tool.SQLQueue_validateMessageList(method_id=None, message_uid=value, path=None)
    if result[0].uid_count > 0:
      return INVALID_ORDER
    return VALID

  def _validate_after_path_and_method_id(self, activity_tool, message, value):
    # Count number of occurances of method_id and path
    if (type(value) != type( (0,) ) and type(value) != type ([])) or len(value)<2:
      LOG('CMFActivity WARNING :', 0, 'unable to recognize value for after_path_and_method : %s' % repr(value))
      return VALID
    path = value[0]
    method = value[1]
    if type(path) == type(''):
      path = [path]
    if type(method) == type(''):
      method = [method]
    result = activity_tool.SQLQueue_validateMessageList(method_id=method, message_uid=None, path=path)
    if result[0].uid_count > 0:
      return INVALID_ORDER
    return VALID

  def _validate_after_tag(self, activity_tool, message, value):
    # Count number of occurances of tag
    if type(value) == type(''):
      value = [value]
    result = activity_tool.SQLQueue_validateMessageList(method_id=None, message_uid=None, tag=value)
    if result[0].uid_count > 0:
      return INVALID_ORDER
    return VALID

  def _validate_after_tag_and_method_id(self, activity_tool, message, value):
    # Count number of occurances of tag and method_id
    if (type(value) != type ( (0,) ) and type(value) != type([])) or len(value)<2:
      LOG('CMFActivity WARNING :', 0, 'unable to recognize value for after_tag_and_method_id : %s' % repr(value))
      return VALID
    tag = value[0]
    method = value[1]
    if type(tag) == type(''):
      tag = [tag]
    if type(method) == type(''):
      method = [method]
    result = activity_tool.SQLQueue_validateMessageList(method_id=method, message_uid=None, tag=tag)
    if result[0].uid_count > 0:
      return INVALID_ORDER
    return VALID

  # Required for tests (time shift)
  def timeShift(self, activity_tool, delay, processing_node = None):
    """
      To simulate timeShift, we simply substract delay from
      all dates in SQLDict message table
    """
    activity_tool.SQLQueue_timeShift(delay = delay, processing_node = processing_node)

registerActivity(SQLQueue)
