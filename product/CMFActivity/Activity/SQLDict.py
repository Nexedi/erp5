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
from RAMDict import RAMDict

from zLOG import LOG

MAX_RETRY = 5

DISTRIBUTABLE_STATE = -1
INVOKE_ERROR_STATE = -2
VALIDATE_ERROR_STATE = -3

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

  def queueMessage(self, activity_tool, m):
    activity_tool.SQLDict_writeMessage(path = '/'.join(m.object_path) ,
                                       method_id = m.method_id,
                                       priority = m.activity_kw.get('priority', 1),
                                       message = self.dumpMessage(m))

  def dequeueMessage(self, activity_tool, processing_node):
    priority = random.choice(priority_weight)
    # Try to find a message at given priority level
    result = activity_tool.SQLDict_readMessage(processing_node=processing_node, priority=priority)
    if len(result) == 0:
      # If empty, take any message
      result = activity_tool.SQLDict_readMessage(processing_node=processing_node, priority=None)
    if len(result) > 0:
      line = result[0]
      path = line.path
      method_id = line.method_id
      # Make sure message can not be processed anylonger
      activity_tool.SQLDict_processMessage(path=path, method_id=method_id, processing_node = processing_node)
      get_transaction().commit() # Release locks before starting a potentially long calculation
      m = self.loadMessage(line.message)
      if m.validate(self, activity_tool): # We should validate each time XXX in case someone is deleting it at the same time
        retry = 0
        while retry < MAX_RETRY:
          activity_tool.invoke(m) # Try to invoke the message
          if m.is_executed:
            retry=MAX_RETRY
          else:
            get_transaction().abort() # Abort and retry
            retry = retry + 1
        if m.is_executed:                                          # Make sure message could be invoked
          activity_tool.SQLDict_delMessage(path=path, method_id=method_id, processing_node=processing_node)  # Delete it
          get_transaction().commit()                                        # If successful, commit
        else:
          get_transaction().abort()                                         # If not, abort transaction and start a new one
          activity_tool.SQLDict_assignMessage(path=path, method_id=method_id, processing_node = INVOKE_ERROR_STATE)
                                                                            # Assign message back to 'error' state
          get_transaction().commit()                                        # and commit
      else:
        activity_tool.SQLDict_assignMessage(path=path, method_id=method_id, processing_node = VALIDATE_ERROR_STATE)
                                                                          # Assign message back to 'error' state
        get_transaction().commit()                                        # and commit
      return 0
    get_transaction().commit() # Release locks before starting a potentially long calculation
    return 1

  def hasActivity(self, activity_tool, object, method_id=None, **kw):
    my_object_path = '/'.join(object.getPhysicalPath())
    result = activity_tool.SQLDict_hasMessage(path=my_object_path, method_id=method_id)
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
    """
    path = '/'.join(object_path)
    # LOG('Flush', 0, str((path, invoke, method_id)))
    result = activity_tool.SQLDict_readMessageList(path=path, method_id=method_id,processing_node=None)
    if commit: get_transaction().commit() # Release locks before starting a potentially long calculation
    method_dict = {}
    if invoke:
      for line in result:
        path = line.path
        method_id = line.method_id
        if not method_dict.has_key(method_id):
          # Only invoke once (it would be different for a queue)
          method_dict[method_id] = 1
          m = self.loadMessage(line.message)
          if m.validate(self, activity_tool):
            retry = 0
            while retry < MAX_RETRY:
              activity_tool.invoke(m) # Try to invoke the message
              if m.is_executed:
                retry=MAX_RETRY
              else:
                get_transaction().abort() # Abort and retry
                retry = retry + 1
            if m.is_executed:                                                 # Make sure message could be invoked
              activity_tool.SQLDict_delMessage(path=path, method_id=method_id, processing_node=None)  # Delete it
              if commit: get_transaction().commit()                           # If successful, commit
            else:
              if commit: get_transaction().abort()    # If not, abort transaction and start a new one
    else:
      activity_tool.SQLDict_delMessage(path=path, method_id=method_id)  # Delete all
      if commit: get_transaction().abort() # Commit flush

  def getMessageList(self, activity_tool, processing_node=None):
    message_list = []
    result = activity_tool.SQLDict_readMessageList(path=None, method_id=None, processing_node=None)
    for line in result:
      m = self.loadMessage(line.message)
      m.processing_node = line.processing_node
      message_list.append(m)
    return message_list

  def distribute(self, activity_tool, node_count):
    processing_node = 1
    result = activity_tool.SQLDict_readMessageList(path=None, method_id=None, processing_node = -1) # Only assign non assigned messages
    get_transaction().commit() # Release locks before starting a potentially long calculation
    path_dict = {}
    for line in result:
      path = line.path
      if not path_dict.has_key(path):
        # Only assign once (it would be different for a queue)
        path_dict[path] = 1
        activity_tool.SQLDict_assignMessage(path=path, processing_node=processing_node)
        get_transaction().commit() # Release locks immediately to allow processing of messages
        processing_node = processing_node + 1
        if processing_node > node_count:
          processing_node = 1 # Round robin

registerActivity(SQLDict)
