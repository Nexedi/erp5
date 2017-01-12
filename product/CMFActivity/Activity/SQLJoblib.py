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

import sys
import transaction
from functools import total_ordering
from zLOG import LOG, TRACE, INFO, WARNING, ERROR, PANIC
from zExceptions import ExceptionFormatter
from ZODB.POSException import ConflictError
from SQLBase import SQLBase, sort_message_key
from Products.CMFActivity.ActivityTool import Message
from Products.CMFActivity.ActivityTool import (
  Message, MESSAGE_NOT_EXECUTED, MESSAGE_EXECUTED, SkippedMessage)
from Products.CMFActivity.ActivityRuntimeEnvironment import (
  DEFAULT_MAX_RETRY, ActivityRuntimeEnvironment, getTransactionalVariable)
from Queue import Queue, VALIDATION_ERROR_DELAY, VALID, INVALID_PATH

# Stop validating more messages when this limit is reached
MAX_VALIDATED_LIMIT = 1000
# Read this many messages to validate.
READ_MESSAGE_LIMIT = 1000

_DequeueMessageException = Exception()

from SQLDict import SQLDict

@total_ordering
class MyBatchedSignature(object):
  """Create hashable signature"""
  def __init__(self, batch):
    #LOG('CMFActivity', INFO, batch.items)
    items = batch.items[0]
    self.func = items[0].__name__
    self.args = items[1]
    self.kwargs = items[2]

  def __eq__(self, other):
    return (self.func, self.args) == (other.func, other.args)

  def __lt__(self, other):
    return (self.func, self.args) < (other.func, other.args)


class SQLJoblib(SQLDict):
  """
    XXX SQLJoblib
  """
  sql_table = 'message_job'
  uid_group = 'portal_activity_job'

  def initialize(self, activity_tool, clear):
    """
      Initialize the message table using MYISAM Engine 
    """
    folder = activity_tool.getPortalObject().portal_skins.activity
    try:
      createMessageTable = folder.SQLJoblib_createMessageTable
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

  def register(self, activity_buffer, activity_tool, message):
    """
      Send message to mysql directly
    """
    assert not message.is_registered, message
    message.is_registered = True
    if activity_buffer.activity_tool is None:
      self.activity_tool = activity_tool
    self.prepareMessage(activity_tool, message)
      
  def prepareMessage(self, activity_tool, m):
    portal = activity_tool.getPortalObject()
    if m.is_registered:
      uid = portal.portal_ids.generateNewIdList(self.uid_group,
        id_count=1, id_generator='uid')[0]
      #import pdb; pdb.set_trace()
      LOG("CMFActivityBackendEntered", INFO, m.activity_kw.get('signature', 0))
      m.order_validation_text = x = self.getOrderValidationText(m)
      processing_node = (0 if x == 'none' else -1)
      portal.SQLJoblib_writeMessage(
        table=self.sql_table,
        uid=uid,
        path='/'.join(m.object_path),
        active_process_uid=m.active_process_uid,
        method_id=m.method_id,
        priority=m.activity_kw.get('priority', 1),
        message=Message.dump(m),
        group_method_id=m.getGroupId(),
        date=m.activity_kw.get('at_date'),
        tag=m.activity_kw.get('tag', ''),
        signature=m.activity_kw.get('signature', 0),
        processing_node=processing_node,
        serialization_tag=m.activity_kw.get('serialization_tag', ''))

  def getProcessableMessageLoader(self, activity_tool, processing_node):
    path_and_method_id_dict = {}
    def load(line):
      # getProcessableMessageList already fetch messages with the same
      # group_method_id, so what remains to be filtered on are path, method_id
      # and signature
      # XXX: What about tag ?
      path = line.path
      method_id = line.method_id
      key = path, method_id
      uid = line.uid
      signature = line.signature
      original_uid = path_and_method_id_dict.get(key)
      if original_uid is None:
        m = Message.load(line.message, uid=uid, line=line, signature=signature)
        try:
          result = activity_tool.SQLJoblib_selectDuplicatedLineList(
            path=path,
            method_id=method_id,
            group_method_id=line.group_method_id,
            signature=signature)
          reserve_uid_list = uid_list = [x.uid for x in result]
          if reserve_uid_list:
            LOG("CMFActivityBackendMarked", INFO, signature, uid_list)
            activity_tool.SQLJoblib_reserveDuplicatedLineList(
              processing_node=processing_node, uid=reserve_uid_list)
        except:
          self._log(WARNING, 'getDuplicateMessageUidList got an exception')
          raise
        if uid_list:
          self._log(TRACE, 'Reserved duplicate messages: %r' % uid_list)
        path_and_method_id_dict[key] = uid
        return m, uid, uid_list
      # We know that original_uid != uid because caller skips lines we returned
      # earlier.
      return None, original_uid, [uid]
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
        LOG("CMFActivityBackendExecuting", INFO, m.signature)
        # This handles cases wehre the result has been already calculated
        # but the duplicate message(s) somehow landed in the queue, 
        # we should not execute these messages and its duplicates again
        # hence just delete them.
        active_process = activity_tool.unrestrictedTraverse(m.active_process)
        if active_process.getResult(m.signature):
          uid_list.append(uid)
          LOG("CMFActivityBackendDeleting", INFO, m.signature)
          self.finalizeMessageExecution(activity_tool, [], None, uid_list)
          return [], None, []

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

  def generateMessageUID(self, m):
    return (tuple(m.object_path), m.method_id, m.activity_kw.get('signature'),
                  m.activity_kw.get('tag'), m.activity_kw.get('group_id'))

  def distribute(self, activity_tool, node_count):
    offset = 0
    assignMessage = getattr(activity_tool, 'SQLBase_assignMessage', None)
    if assignMessage is not None:
      now_date = self.getNow(activity_tool)
      validated_count = 0
      while 1:
        result = self._getMessageList(activity_tool, processing_node=-1,
                                      to_date=now_date,
                                      offset=offset, count=READ_MESSAGE_LIMIT)
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
          message_unique_dict = {}
          serialization_tag_dict = {}
          distributable_uid_set = set()
          deletable_uid_list = []

          # remove duplicates
          # SQLDict considers object_path, method_id, tag to unify activities,
          # but ignores method arguments. They are outside of semantics.
          for message in message_dict.itervalues():
            message_unique_dict.setdefault(self.generateMessageUID(message),
                                           []).append(message)

          for message_list in message_unique_dict.itervalues():
            if len(message_list) > 1:
              # Sort list of duplicates to keep the message with highest score
              message_list.sort(key=sort_message_key)
              deletable_uid_list += [m.uid for m in message_list[1:]]
            message = message_list[0]
            serialization_tag = message.activity_kw.get('serialization_tag')
            if serialization_tag is None:
              distributable_uid_set.add(message.uid)
            else:
              serialization_tag_dict.setdefault(serialization_tag,
                                                []).append(message)
          # Don't let through if there is the same serialization tag in the
          # message dict. If there is the same serialization tag, only one can
          # be validated and others must wait.
          # But messages with group_method_id are exceptions. serialization_tag
          # does not stop validating together. Because those messages should
          # be processed together at once.
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
          if deletable_uid_list:
            activity_tool.SQLBase_delMessage(table=self.sql_table,
                                             uid=deletable_uid_list)
          distributable_count = len(distributable_uid_set)
          if distributable_count:
            assignMessage(table=self.sql_table,
              processing_node=0, uid=tuple(distributable_uid_set))
            validated_count += distributable_count
            if validated_count >= MAX_VALIDATED_LIMIT:
              return
        offset += READ_MESSAGE_LIMIT
