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

class SQLQueue(SQLBase):
  """
    A simple OOBTree based queue. It should be compatible with transactions
    and provide sequentiality. Should not create conflict
    because use of OOBTree.
  """
  sql_table = 'message_queue'

  def prepareQueueMessageList(self, activity_tool, message_list):
    registered_message_list = [m for m in message_list if m.is_registered]
    for i in xrange(0, len(registered_message_list), MAX_MESSAGE_LIST_SIZE):
      message_list = registered_message_list[i:i + MAX_MESSAGE_LIST_SIZE]
      # The uid_list also is store in the ZODB
      uid_list = activity_tool.getPortalObject().portal_ids.generateNewIdList(
        id_generator='uid', id_group='portal_activity_queue',
        id_count=len(message_list))
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
      dumped_message_list = map(self.dumpMessage, message_list)
      activity_tool.SQLQueue_writeMessageList(
        uid_list=uid_list,
        path_list=path_list,
        active_process_uid_list=active_process_uid_list,
        method_id_list=method_id_list,
        priority_list=priority_list,
        message_list=dumped_message_list,
        group_method_id_list=group_method_id_list,
        date_list=date_list,
        tag_list=tag_list,
        processing_node_list=processing_node_list,
        serialization_tag_list=serialization_tag_list)

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
    assignMessage = getattr(activity_tool, 'SQLBase_assignMessage', None)
    if assignMessage is not None:
      now_date = self.getNow(activity_tool)
      validated_count = 0
      while 1:
        result = self._getMessageList(activity_tool, processing_node=-1,
                                      to_date=now_date, processing=0,
                                      offset=offset, count=READ_MESSAGE_LIMIT)
        if not result:
          return
        transaction.commit()

        validation_text_dict = {'none': 1}
        message_dict = {}
        for line in result:
          message = self.loadMessage(line.message, uid=line.uid, line=line)
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
        if not hasattr(m, 'order_validation_text'): # BBB
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
    default =  SQLBase.getPriority(self, activity_tool)
    return self._getPriority(activity_tool, method, default)

registerActivity(SQLQueue)
