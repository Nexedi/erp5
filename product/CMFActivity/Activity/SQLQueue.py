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
from Queue import VALID, INVALID_PATH
from Products.CMFActivity.Errors import ActivityFlushError
from ZODB.POSException import ConflictError
from SQLBase import SQLBase, sort_message_key
from zExceptions import ExceptionFormatter

import transaction

from zLOG import LOG, WARNING, ERROR, INFO, PANIC, TRACE

# Stop validating more messages when this limit is reached
MAX_VALIDATED_LIMIT = 1000
# Read this many messages to validate.
READ_MESSAGE_LIMIT = 1000

MAX_MESSAGE_LIST_SIZE = 100

class SQLQueue(RAMQueue, SQLBase):
  """
    A simple OOBTree based queue. It should be compatible with transactions
    and provide sequentiality. Should not create conflict
    because use of OOBTree.
  """
  sql_table = 'message_queue'
  merge_duplicate = False

  def prepareQueueMessageList(self, activity_tool, message_list):
    message_list = [m for m in message_list if m.is_registered]
    for i in xrange(0, len(message_list), MAX_MESSAGE_LIST_SIZE):
      registered_message_list = message_list[i:i + MAX_MESSAGE_LIST_SIZE]
      # The uid_list also is store in the ZODB
      uid_list = activity_tool.getPortalObject().portal_ids.generateNewIdList(
                id_generator='uid', id_group='portal_activity_queue',
                id_count=len(registered_message_list))
      path_list = ['/'.join(m.object_path) for m in registered_message_list]
      active_process_uid_list = [m.active_process_uid for m in registered_message_list]
      method_id_list = [m.method_id for m in registered_message_list]
      priority_list = [m.activity_kw.get('priority', 1) for m in registered_message_list]
      date_list = [m.activity_kw.get('at_date', None) for m in registered_message_list]
      group_method_id_list = []
      for m in registered_message_list:
        group_method_id = m.activity_kw.get('group_method_id', '')
        if group_method_id is None:
          group_method_id = 'portal_activities/dummyGroupMethod/' + m.method_id
        group_method_id_list.append(group_method_id + '\0' +
                                    m.activity_kw.get('group_id', ''))
      tag_list = [m.activity_kw.get('tag', '') for m in registered_message_list]
      serialization_tag_list = [m.activity_kw.get('serialization_tag', '') for m in registered_message_list]
      dumped_message_list = [self.dumpMessage(m) for m in registered_message_list]
      activity_tool.SQLQueue_writeMessageList(uid_list=uid_list,
                                              path_list=path_list,
                                              active_process_uid_list=active_process_uid_list,
                                              method_id_list=method_id_list,
                                              priority_list=priority_list,
                                              message_list=dumped_message_list,
                                              group_method_id_list = group_method_id_list,
                                              date_list=date_list,
                                              tag_list=tag_list,
                                              processing_node_list=None,
                                              serialization_tag_list=serialization_tag_list)

  def prepareDeleteMessage(self, activity_tool, m):
    # Erase all messages in a single transaction
    #LOG("prepareDeleteMessage", 0, str(m.__dict__))
    activity_tool.SQLBase_delMessage(table=self.sql_table, uid=[m.uid])

  def finishQueueMessage(self, activity_tool_path, m):
    # Nothing to do in SQLQueue.
    pass

  def finishDeleteMessage(self, activity_tool_path, m):
    # Nothing to do in SQLQueue.
    pass

  def getDuplicateMessageUidList(self, activity_tool, line, processing_node):
    """
      Reserve unreserved messages matching given line.
      Return their uids.
    """
    return ()

  dequeueMessage = SQLBase.dequeueMessage

  def hasActivity(self, activity_tool, object, method_id=None, only_valid=None, active_process_uid=None):
    hasMessage = getattr(activity_tool, 'SQLQueue_hasMessage', None)
    if hasMessage is not None:
      if object is None:
        my_object_path = None
      else:
        my_object_path = '/'.join(object.getPhysicalPath())
      result = hasMessage(path=my_object_path, method_id=method_id, only_valid=only_valid, active_process_uid=active_process_uid)
      if len(result) > 0:
        return result[0].message_count > 0
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
      result = readMessageList(path=path, method_id=method_id, processing_node=None, to_date=None, include_processing=0)
      for line in result:
        path = line.path
        method_id = line.method_id
        m = self.loadMessage(line.message, uid=line.uid, line=line)
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
        activity_tool.SQLBase_delMessage(table=self.sql_table,
                                         uid=[line.uid for line in result])

  getMessageList = SQLBase.getMessageList

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
                                                        serialization_tag=None,
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
        m = self.loadMessage(line.message, uid=line.uid, line=line)
        message_list.append(m)
    return message_list

  def distribute(self, activity_tool, node_count):
    offset = 0
    readMessageList = getattr(activity_tool, 'SQLQueue_readMessageList', None)
    if readMessageList is not None:
      now_date = self.getNow(activity_tool)
      validated_count = 0
      while 1:
        result = readMessageList(path=None, method_id=None, processing_node=-1,
                                 to_date=now_date, include_processing=0,
                                 offset=offset, count=READ_MESSAGE_LIMIT)
        if not result:
          return
        transaction.commit()

        validation_text_dict = {'none': 1}
        message_dict = {}
        for line in result:
          message = self.loadMessage(line.message, uid=line.uid, line=line)
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
            activity_tool.SQLBase_assignMessage(table=self.sql_table,
              processing_node=0, uid=tuple(distributable_uid_set))
            validated_count += distributable_count
            if validated_count >= MAX_VALIDATED_LIMIT:
              return
        offset += READ_MESSAGE_LIMIT

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
                                   count=False,
                                   serialization_tag=serialization_tag)
      message_list = []
      for line in result:
        m = self.loadMessage(line.message,
                             line=line,
                             uid=line.uid,
                             date=line.date,
                             processing_node=line.processing_node)
        m.order_validation_text = self.getOrderValidationText(m)
        message_list.append(m)
      return message_list
    else:
      return []

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
