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
from Products.CMFActivity.ActiveObject import DISTRIBUTABLE_STATE, INVOKE_ERROR_STATE, VALIDATE_ERROR_STATE

from zLOG import LOG

MAX_PRIORITY = 5

priority_weight = \
  [1] * 64 + \
  [2] * 20 + \
  [3] * 10 + \
  [4] * 5 + \
  [5] * 1

class ActivityFlushError(Exception):
    """Error during active message flush"""

class SQLDict(RAMDict):
  """
    A simple OOBTree based queue. It should be compatible with transactions
    and provide sequentiality. Should not create conflict
    because use of OOBTree.
  """
  # Transaction commit methods
  def prepareQueueMessage(self, activity_tool, m):
    if m.is_registered:
      activity_tool.SQLDict_writeMessage(path = '/'.join(m.object_path) ,
                                          method_id = m.method_id,
                                          priority = m.activity_kw.get('priority', 1),
                                          message = self.dumpMessage(m))
                                          # Also store uid of activity

  def prepareDeleteMessage(self, activity_tool, m):
    # Erase all messages in a single transaction
    path = '/'.join(m.object_path)
    uid_list = activity_tool.SQLDict_readUidList(path=path, method_id=m.method_id,processing_node=None)
    uid_list = map(lambda x:x.uid, uid_list)
    if len(uid_list)>0:
      activity_tool.SQLDict_delMessage(uid = uid_list) 
    
  # Registration management    
  def registerActivityBuffer(self, activity_buffer):
    activity_buffer._sqldict_uid_dict = {}
    activity_buffer._sqldict_message_list = []
            
  def isMessageRegistered(self, activity_buffer, activity_tool, m):
    return activity_buffer._sqldict_uid_dict.has_key((m.object_path, m.method_id))
          
  def registerMessage(self, activity_buffer, activity_tool, m):
    m.is_registered = 1
    activity_buffer._sqldict_uid_dict[(m.object_path, m.method_id)] = 1
    activity_buffer._sqldict_message_list.append(m)
          
  def unregisterMessage(self, activity_buffer, activity_tool, m):
    m.is_registered = 0 # This prevents from inserting deleted messages into the queue
    if activity_buffer._sqldict_uid_dict.has_key((m.object_path, m.method_id)):
      del activity_buffer._sqldict_uid_dict[(m.object_path, m.method_id)]

  def getRegisteredMessageList(self, activity_buffer, activity_tool):
    if hasattr(activity_buffer,'_sqldict_message_list'):
      return filter(lambda m: m.is_registered, activity_buffer._sqldict_message_list)
    else:
      return ()
                
  # Queue semantic
  def dequeueMessage(self, activity_tool, processing_node):
    priority = random.choice(priority_weight)
    # Try to find a message at given priority level
    result = activity_tool.SQLDict_readMessage(processing_node=processing_node, priority=priority)
    if len(result) == 0:
      # If empty, take any message
      priority = None
      result = activity_tool.SQLDict_readMessage(processing_node=processing_node, priority=priority)
    if len(result) > 0:
      line = result[0]
      path = line.path
      method_id = line.method_id
      uid_list = activity_tool.SQLDict_readUidList( path=path, method_id= method_id, processing_node = None )
      uid_list = map(lambda x:x.uid, uid_list)
      # Make sure message can not be processed anylonger
      if len(uid_list) > 0:
        activity_tool.SQLDict_processMessage(uid = uid_list)
      get_transaction().commit() # Release locks before starting a potentially long calculation
      # This may lead (1 for 1,000,000 in case of reindexing) to messages left in processing state
      m = self.loadMessage(line.message, uid = line.uid)
      # Make sure object exists
      if not m.validate(self, activity_tool):
        if line.priority > MAX_PRIORITY:
          # This is an error
          if len(uid_list) > 0:
            activity_tool.SQLDict_assignMessage(uid = uid_list, processing_node = VALIDATE_ERROR_STATE)
                                                                            # Assign message back to 'error' state
          #m.notifyUser(activity_tool)                                       # Notify Error
          get_transaction().commit()                                        # and commit
        else:
          # Lower priority
          if len(uid_list) > 0:
            activity_tool.SQLDict_setPriority(uid = uid_list,
                                            priority = line.priority + 1)
          get_transaction().commit() # Release locks before starting a potentially long calculation
      else:
        # Try to invoke
        activity_tool.invoke(m) # Try to invoke the message - what happens if read conflict error restarts transaction ?
        if m.is_executed:                                          # Make sure message could be invoked
          if len(uid_list) > 0:
            activity_tool.SQLDict_delMessage(uid = uid_list)                # Delete it
          get_transaction().commit()                                        # If successful, commit
          if m.active_process:
            active_process = activity_tool.unrestrictedTraverse(m.active_process)
            if not active_process.hasActivity():
              # Not more activity
              m.notifyUser(activity_tool, message="Process Finished") # XXX commit bas ???
        else:
          get_transaction().abort()                                         # If not, abort transaction and start a new one
          if line.priority > MAX_PRIORITY:
            # This is an error
            if len(uid_list) > 0:
              activity_tool.SQLDict_assignMessage(uid = uid_list, processing_node = INVOKE_ERROR_STATE)
                                                                              # Assign message back to 'error' state
            m.notifyUser(activity_tool)                                       # Notify Error
            get_transaction().commit()                                        # and commit
          else:
            # Lower priority
            if len(uid_list) > 0:
              activity_tool.SQLDict_setPriority(uid = uid_list,
                                                priority = line.priority + 1)
            get_transaction().commit() # Release locks before starting a potentially long calculation
      return 0
    get_transaction().commit() # Release locks before starting a potentially long calculation
    return 1

  def hasActivity(self, activity_tool, object, **kw):
    if object is not None:
      my_object_path = '/'.join(object.getPhysicalPath())
      result = activity_tool.SQLDict_hasMessage(path=my_object_path, **kw)
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
    # Parse each message in registered
    for m in activity_tool.getRegisteredMessageList(self):
      if object_path == m.object_path and (method_id is None or method_id == m.method_id):
        activity_tool.unregisterMessage(self, m)
        if not method_dict.has_key(method_id):
          if invoke:
            # First Validate
            if m.validate(self, activity_tool):
              activity_tool.invoke(m) # Try to invoke the message - what happens if invoke calls flushActivity ??
              if not m.is_executed:                                                 # Make sure message could be invoked
                # The message no longer exists
                raise ActivityFlushError, (
                    'Could not evaluate %s on %s' % (method_id , path))
            else:
              # The message no longer exists
              raise ActivityFlushError, (
                  'The document %s does not exist' % path)               
    # Parse each message in SQL dict
    result = activity_tool.SQLDict_readMessageList(path=path, method_id=method_id,processing_node=None)
    for line in result:
      path = line.path
      method_id = line.method_id
      if not method_dict.has_key(method_id):
        # Only invoke once (it would be different for a queue)
        method_dict[method_id] = 1
        m = self.loadMessage(line.message, uid = line.uid)
        self.deleteMessage(activity_tool, m)
        if invoke:
          # First Validate
          if m.validate(self, activity_tool):
            activity_tool.invoke(m) # Try to invoke the message - what happens if invoke calls flushActivity ??
            if not m.is_executed:                                                 # Make sure message could be invoked
              # The message no longer exists
              raise ActivityFlushError, (
                  'Could not evaluate %s on %s' % (method_id , path))
          else:
            # The message no longer exists
            raise ActivityFlushError, (
                'The document %s does not exist' % path)

  # def start(self, activity_tool, active_process=None):
  #   uid_list = activity_tool.SQLDict_readUidList(path=path, active_process=active_process)
  #   activity_tool.SQLDict_assignMessage(uid = uid_list, processing_node = DISTRIBUTABLE_STATE)

  # def stop(self, activity_tool, active_process=None):
  #   uid_list = activity_tool.SQLDict_readUidList(path=path, active_process=active_process)
  #   activity_tool.SQLDict_assignMessage(uid = uid_list, processing_node = STOP_STATE)

  def getMessageList(self, activity_tool, processing_node=None):
    # YO: reading all lines might cause a deadlock
    message_list = []
    result = activity_tool.SQLDict_readMessageList(path=None, method_id=None, processing_node=None)
    for line in result:
      m = self.loadMessage(line.message, uid = line.uid)
      m.processing_node = line.processing_node
      m.priority = line.priority
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
        activity_tool.SQLDict_assignMessage(path=path, processing_node=processing_node, uid=None)
        get_transaction().commit() # Release locks immediately to allow processing of messages
        processing_node = processing_node + 1
        if processing_node > node_count:
          processing_node = 1 # Round robin

registerActivity(SQLDict)
