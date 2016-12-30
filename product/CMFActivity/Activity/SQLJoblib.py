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

# XXX: Note from Rafael
# only reimplment the minimal, and only custom the SQL that update this table.
# Always check if things are there (ie.: If the connection, or the script are present).

import copy
import hashlib
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

# this is improvisation of 
# http://stackoverflow.com/questions/5884066/hashing-a-python-dictionary/8714242#8714242
def make_hash(o):
  """
  Makes a hash from a dictionary, list, tuple or set to any level, that contains
  only other hashable types (including any lists, tuples, sets, and
  dictionaries).
  """

  if isinstance(o, (set, tuple, list)):
    return hash(tuple([make_hash(e) for e in o]))

  elif not isinstance(o, dict):
    try:
      return hash(o)
    except TypeError:
      return hash(int(hashlib.md5(o).hexdigest(), 16))
  new_o = copy.deepcopy(o)
  for k, v in new_o.items():
    new_o[k] = make_hash(v)

  return hash(tuple(frozenset(sorted(new_o.items()))))

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
        processing_node=processing_node,
        serialization_tag=m.activity_kw.get('serialization_tag', ''))

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
      tv = getTransactionalVariable()
      tv['activity_runtime_environment'] = activity_runtime_environment
      # Try to invoke
      try:
        method(*args)
        # Abort if at least 1 message failed. On next tic, only those that
        # succeeded will be selected because their at_date won't have been
        # increased.
        for m in message_list:
          if m.getExecutionState() == MESSAGE_NOT_EXECUTED:
            raise _DequeueMessageException
        transaction.commit()
        
        for m in message_list:
          if m.getExecutionState() == MESSAGE_EXECUTED:
            transaction.begin()
            # Create a signature and then store result into the dict
            signature = MyBatchedSignature(m.args[0].batch)
            # get active process
            active_process = activity_tool.unrestrictedTraverse(m.active_process)
            active_process.process_result_map.update({signature: m.result})
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
            tv['activity_runtime_environment'] = activity_runtime_environment
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