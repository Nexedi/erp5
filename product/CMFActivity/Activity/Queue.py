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

import pickle, sys
from Acquisition import aq_base
from DateTime import DateTime
from Products.CMFActivity.ActivityTool import Message
from zLOG import LOG
from ZODB.POSException import ConflictError

# Error values for message validation
EXCEPTION      = -1
VALID          = 0
INVALID_PATH   = 1
INVALID_ORDER  = 2

# Time global parameters
MAX_PROCESSING_TIME = 900 # in seconds
VALIDATION_ERROR_DELAY = 30 # in seconds

class Queue:
  """
    Step 1: use lists

    Step 2: add some object related dict which prevents calling twice the same method

    Step 3: add some time information for deferred execution

    Step 4: use MySQL as a way to store events (with locks)

    Step 5: use periodic Timer to wakeup Scheduler

    Step 6: add multiple threads on a single Scheduler

    Step 7: add control thread to kill "events which last too long"

    Some data:

    - reindexObject = 50 ms

    - calling a MySQL read = 0.7 ms

    - calling a simple method by HTTP = 30 ms

    - calling a complex method by HTTP = 500 ms

    References:

    http://www.mysql.com/doc/en/InnoDB_locking_reads.html
    http://www.python.org/doc/current/lib/thread-objects.html
    http://www-poleia.lip6.fr/~briot/actalk/actalk.html
  """

  #scriptable_method_id_list = ['appendMessage', 'nextMessage', 'delMessage']

  def __init__(self):
    self.is_alive = {}
    self.is_awake = {}
    self.is_initialized = 0
    self.max_processing_date = DateTime()

  def initialize(self, activity_tool):
    # This is the only moment when
    # we can set some global variables related
    # to the ZODB context
    if not self.is_initialized:
      self.is_initialized = 1

  def queueMessage(self, activity_tool, m):    
    activity_tool.deferredQueueMessage(self, m)  
  
  def deleteMessage(self, activity_tool, m):
    if not getattr(m, 'is_deleted', 0):
      # We try not to delete twice
      # However this can not be garanteed in the case of messages loaded from SQL
      activity_tool.deferredDeleteMessage(self, m)  
    m.is_deleted = 1
    
  def dequeueMessage(self, activity_tool, processing_node):
    pass

  def tic(self, activity_tool, processing_node):
    # Tic should return quickly to prevent locks or commit transactions at some point
    if self.dequeueMessage(activity_tool, processing_node):
      self.sleep(activity_tool, processing_node)

  def distribute(self, activity_tool, node_count):
    pass

  def sleep(self, activity_tool, processing_node):
    self.is_awake[processing_node] = 0

  def wakeup(self, activity_tool, processing_node):
    self.is_awake[processing_node] = 1

  def terminate(self, activity_tool, processing_node):
    self.is_awake[processing_node] = 0
    self.is_alive[processing_node] = 0

  def validate(self, activity_tool, message, **kw):
    """
      This is the place where activity semantics is implemented
      **kw contains all parameters which allow to implement synchronisation,
      constraints, delays, etc.
      
      Standard synchronisation parameters:
      
      after_method_id   --  never validate message if after_method_id
                            is in the list of methods which are
                            going to be executed
    
      after_message_uid --  never validate message if after_message_uid
                            is in the list of messages which are
                            going to be executed
    
      after_path        --  never validate message if after_path
                            is in the list of path which are
                            going to be executed                                                        
    """
    try:
      if activity_tool.unrestrictedTraverse(message.object_path) is None:
        # Do not try to call methods on objects which do not exist
        LOG('WARNING ActivityTool', 0,
           'Object %s does not exist' % '/'.join(message.object_path))
        return INVALID_PATH
      for k, v in kw.items():
        if activity_tool.validateOrder(message, k, v):
          return INVALID_ORDER
    except ConflictError:
      raise
    except:
      LOG('WARNING ActivityTool', 0,
          'Validation of Object %s raised exception' % '/'.join(message.object_path),
          error=sys.exc_info())
      # Do not try to call methods on objects which cause errors
      return EXCEPTION
    return VALID

  def isAwake(self, activity_tool, processing_node):
    return self.is_awake[processing_node]

  def hasActivity(self, activity_tool, object, processing_node=None, active_process=None, **kw):
    return 0

  def flush(self, activity_tool, object, **kw):    
    pass

  def start(self, active_process=None):
    # Start queue / activities in queue for given process
    pass

  def stop(self, active_process=None):
    # Stop queue / activities in queue for given process
    pass

  def loadMessage(self, s, **kw):
    m = pickle.loads(s)
    m.__dict__.update(kw)
    return m

  def dumpMessage(self, m):
    return pickle.dumps(m)

  def getMessageList(self, activity_tool, processing_node=None,**kw):
    return []  

  def countMessage(self, activity_tool,**kw):
    return 0

  def countMessageWithTag(self, activity_tool,value):
    return 0
  
  # Transaction Management
  def prepareQueueMessage(self, activity_tool, m):
    # Called to prepare transaction commit for queued messages
    pass

  def finishQueueMessage(self, activity_tool_path, m):
    # Called to commit queued messages
    pass

  def prepareDeleteMessage(self, activity_tool, m):
    # Called to prepare transaction commit for deleted messages
    pass

  def finishDeleteMessage(self, activity_tool_path, m):
    # Called to commit deleted messages
    pass

  # Registration Management
  def registerActivityBuffer(self, activity_buffer):
    class_name = self.__class__.__name__
    setattr(activity_buffer, '_%s_message_list' % class_name, [])  

  def isMessageRegistered(self, activity_buffer, activity_tool, m):
    class_name = self.__class__.__name__
    return m in getattr(activity_buffer, '_%s_message_list' % class_name)

  def registerMessage(self, activity_buffer, activity_tool, m):
    class_name = self.__class__.__name__
    getattr(activity_buffer, '_%s_message_list' % class_name).append(m)
    m.is_registered = 1

  def unregisterMessage(self, activity_buffer, activity_tool, m):
    m.is_registered = 0

  def getRegisteredMessageList(self, activity_buffer, activity_tool):
    class_name = self.__class__.__name__
    if hasattr(activity_buffer, '_%s_message_list' % class_name):
      return filter(lambda m: m.is_registered, getattr(activity_buffer, '_%s_message_list' % class_name))
    else:
      return ()

  # Required for tests (time shift)
  def timeShift(self, activity_tool, delay):
    """
      delay is provided in fractions of day
    """
    pass
