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

from Products.CMFCore import CMFCorePermissions
from Products.ERP5Type.Document.Folder import Folder
from Products.PythonScripts.Utility import allow_class
from AccessControl import ClassSecurityInfo
from Products.CMFCore.utils import UniqueObject, _checkPermission, _getAuthenticatedUser
from Globals import InitializeClass, DTMLFile, get_request
from Acquisition import aq_base
from DateTime.DateTime import DateTime
from Products.CMFActivity.ActiveObject import DISTRIBUTABLE_STATE, INVOKE_ERROR_STATE, VALIDATE_ERROR_STATE
from ActivityBuffer import ActivityBuffer
import threading
import sys

from zLOG import LOG

# Using a RAM property (not a property of an instance) allows
# to prevent from storing a state in the ZODB (and allows to restart...)
active_threads = 0
max_active_threads = 1 # 2 will cause more bug to appear (he he)
is_initialized = 0
tic_lock = threading.Lock() # A RAM based lock

# Activity Registration
activity_dict = {}
activity_list = []

def registerActivity(activity):
  # Must be rewritten to register
  # class and create instance for each activity
  LOG('Init Activity', 0, str(activity.__name__))
  activity_instance = activity()
  activity_list.append(activity_instance)
  activity_dict[activity.__name__] = activity_instance

class Result:

  def __init__(self, object_or_path, method_id, result, log_title=None, log_id=None, log_message=None):
    # Some utility function to do this would be useful since we use it everywhere XXX
    if type(object_or_path) in (type([]), type(())):
      url = '/'.join(object_or_path)
      path = object_or_path
    elif type(object_or_path) is type('a'):
      path = object_or_path.split('/')
      url = object_or_path
    else:
      path = object_or_path.getPhysicalPath()
      url = '/'.join(path)
    self.object_path = path
    self.object_url = url
    self.method_id = method_id
    self.result = result              # Include arbitrary result
    self.log_title = log_title        # Should follow Zope convention for LOG title
    self.log_id = log_id              # Should follow Zope convention for LOG ids
    self.log_message = log_message    # Should follow Zope convention for LOG message

allow_class(Result)

class Message:
  
  def __init__(self, object, active_process, activity_kw, method_id, args, kw):
    if type(object) is type('a'):
      self.object_path = object.split('/')
    else:
      self.object_path = object.getPhysicalPath()
    if type(active_process) is type('a'):
      self.active_process = active_process.split('/')
    elif active_process is None:
      self.active_process = None
    else:
      self.active_process = active_process.getPhysicalPath()
      self.active_process_uid = active_process.getUid()
    self.activity_kw = activity_kw
    self.method_id = method_id
    self.args = args
    self.kw = kw
    self.is_executed = 0
    self.user_name = str(_getAuthenticatedUser(self))
    # Store REQUEST Info ?

  def __call__(self, activity_tool):
    try:
      LOG('WARNING ActivityTool', 0,
           'Trying to call method %s on object %s' % (self.method_id, self.object_path))
      object = activity_tool.unrestrictedTraverse(self.object_path)
      # Change user if required (TO BE DONE)
      # self.activity_kw
      activity_tool._v_active_process = self.active_process # Store the active_process as volatile thread variable
      result = getattr(object, self.method_id)(*self.args, **self.kw)
      if activity_tool._v_active_process is not None:
        active_process = activity_tool.getActiveProcess()
        active_process.activateResult(Result(object,self.method_id,result)) # XXX Allow other method_id in future
      self.is_executed = 1
    except:
      self.is_executed = 0
      LOG('WARNING ActivityTool', 0,
           'Could not call method %s on object %s' % (self.method_id, self.object_path), error=sys.exc_info())

  def validate(self, activity, activity_tool):
    return activity.validate(activity_tool, self, **self.activity_kw)

  def notifyUser(self, activity_tool, message="Failed Processing Activity"):
    #LOG('notifyUser begin', 0, str(self.user_name))
    user_email = activity_tool.portal_membership.getMemberById(self.user_name).getProperty('email')
    if user_email in ('', None):
      user_email = activity_tool.email_from_address
    #LOG('notifyUser user_email', 0, str(user_email))
    mail_text = """From: %s
To: %s
Subject: %s

%s

Document: %s
Method: %s
    """ % (activity_tool.email_from_address, user_email,
           message, message, '/'.join(self.object_path), self.method_id)
    #LOG('notifyUser mail_text', 0, str(mail_text))
    activity_tool.MailHost.send( mail_text )
    #LOG('notifyUser send', 0, '')

class Method:

  def __init__(self, passive_self, activity, active_process, kw, method_id):
    self.__passive_self = passive_self
    self.__activity = activity
    self.__active_process = active_process
    self.__kw = kw
    self.__method_id = method_id

  def __call__(self, *args, **kw):
    m = Message(self.__passive_self, self.__active_process, self.__kw, self.__method_id, args, kw)
    activity_dict[self.__activity].queueMessage(self.__passive_self.portal_activities, m)

allow_class(Method)

class ActiveWrapper:

  def __init__(self, passive_self, activity, active_process, **kw):
    self.__dict__['__passive_self'] = passive_self
    self.__dict__['__activity'] = activity
    self.__dict__['__active_process'] = active_process
    self.__dict__['__kw'] = kw

  def __getattr__(self, id):
    return Method(self.__dict__['__passive_self'], self.__dict__['__activity'],
                  self.__dict__['__active_process'],
                  self.__dict__['__kw'], id)

class ActivityTool (Folder, UniqueObject):
    """
    ActivityTool is the central point for activity management.

    Improvement to consider to reduce locks:

      Idea 1: create an SQL tool which accumulate queries and executes them at the end of a transaction,
              thus allowing all SQL transaction to happen in a very short time
              (this would also be a great way of using MyISAM tables)

      Idea 2: do the same at the level of ActivityTool

      Idea 3: do the same at the level of each activity (ie. queueMessage
              accumulates and fires messages at the end of the transactino)
    """
    id = 'portal_activities'
    meta_type = 'CMF Activity Tool'
    portal_type = 'Activity Tool'
    allowed_types = ( 'CMF Active Process', )
    security = ClassSecurityInfo()

    manage_options = tuple(
                     [ { 'label' : 'Overview', 'action' : 'manage_overview' }
                     , { 'label' : 'Activities', 'action' : 'manageActivities' }
                     ,
                     ] + list(Folder.manage_options))

    security.declareProtected( CMFCorePermissions.ManagePortal , 'manageActivities' )
    manageActivities = DTMLFile( 'dtml/manageActivities', globals() )

    security.declareProtected( CMFCorePermissions.ManagePortal , 'manage_overview' )
    manage_overview = DTMLFile( 'dtml/explainActivityTool', globals() )

    def __init__(self):
        return Folder.__init__(self, ActivityTool.id)
    
    # Filter content (ZMI))
    def filtered_meta_types(self, user=None):
        # Filters the list of available meta types.
        all = ActivityTool.inheritedAttribute('filtered_meta_types')(self)
        meta_types = []
        for meta_type in self.all_meta_types():
            if meta_type['name'] in self.allowed_types:
                meta_types.append(meta_type)
        return meta_types

    def initialize(self):
      global is_initialized
      from Activity import RAMQueue, RAMDict, SQLQueue, SQLDict
      # Initialize each queue
      for activity in activity_list:
        activity.initialize(self)
      is_initialized = 1

    security.declarePublic('distribute')
    def distribute(self, node_count=1):
      """
        Distribute load
      """
      # Initialize if needed
      if not is_initialized: self.initialize()

      # Call distribute on each queue
      for activity in activity_list:
        try:
          activity.distribute(self, node_count)
        except:
          LOG('CMFActivity:', 100, 'Core call to distribute failed for activity %s' % activity)

    security.declarePublic('tic')
    def tic(self, processing_node=1, force=0):
      """
        Starts again an activity
        processing_node starts from 1 (there is not node 0)
      """
      global active_threads, is_initialized

      # return if the number of threads is too high
      if active_threads >= max_active_threads:
        if not force: return 'Too many threads'

      if tic_lock is None:
        return

      # Initialize if needed
      if not is_initialized: self.initialize()

      # increase the number of active_threads
      tic_lock.acquire()
      active_threads += 1
      tic_lock.release()

      # Wakeup each queue
      for activity in activity_list:
        try:
          activity.wakeup(self, processing_node)
        except:
          LOG('CMFActivity:', 100, 'Core call to wakeup failed for activity %s' % activity)

      # Process messages on each queue in round robin
      has_awake_activity = 1
      while has_awake_activity:
        has_awake_activity = 0
        for activity in activity_list:
          try:
            activity.tic(self, processing_node) # Transaction processing is the responsability of the activity
            has_awake_activity = has_awake_activity or activity.isAwake(self, processing_node)
          except:
            LOG('CMFActivity:', 100, 'Core call to tic or isAwake failed for activity %s' % activity)

      # decrease the number of active_threads
      tic_lock.acquire()
      active_threads -= 1
      tic_lock.release()

    def hasActivity(self, *args, **kw):
      # Check in each queue if the object has deferred tasks
      # if not argument is provided, then check on self
      if len(args) > 0:
        object = args[0]
      else:
        object = self
      for activity in activity_list:
        if activity.hasActivity(self, object, **kw):
          return 1
      return 0

    def activate(self, object, activity, active_process, **kw):
      global is_initialized
      if not is_initialized: self.initialize()
      if not hasattr(self, '_v_activity_buffer'): self._v_activity_buffer = ActivityBuffer()
      return ActiveWrapper(object, activity, active_process, **kw)

    def deferredQueueMessage(self, activity, message):
      self._v_activity_buffer.deferredQueueMessage(self, activity, message)
      
    def deferredDeleteMessage(self, activity, message):
      self._v_activity_buffer.deferredDeleteMessage(self, activity, message)
          
    def getRegisteredMessageList(self, activity):
      activity_buffer = getattr(self, '_v_activity_buffer', None)
      #if getattr(self, '_v_activity_buffer', None):
      if activity_buffer is not None:
        activity_buffer._register() # This is required if flush flush is called outside activate
        return activity.getRegisteredMessageList(self._v_activity_buffer, self)
      else:
        return []
          
    def unregisterMessage(self, activity, message):
      self._v_activity_buffer._register() # Required if called by flush, outside activate
      return activity.unregisterMessage(self._v_activity_buffer, self, message)
          
    def flush(self, object, invoke=0, **kw):
      global is_initialized
      if not is_initialized: self.initialize()
      if not hasattr(self, '_v_activity_buffer'): self._v_activity_buffer = ActivityBuffer()
      if type(object) is type(()):
        object_path = object
      else:
        object_path = object.getPhysicalPath()
      for activity in activity_list:
        LOG('CMFActivity: ', 0, 'flushing activity %s' % activity.__class__.__name__)
        activity.flush(self, object_path, invoke=invoke, **kw)

    def start(self, **kw):
      global is_initialized
      if not is_initialized: self.initialize()
      for activity in activity_list:
        LOG('CMFActivity: ', 0, 'starting activity %s' % activity.__class__.__name__)
        activity.start(self, **kw)

    def stop(self, **kw):
      global is_initialized
      if not is_initialized: self.initialize()
      for activity in activity_list:
        LOG('CMFActivity: ', 0, 'starting activity %s' % activity.__class__.__name__)
        activity.stop(self, **kw)

    def invoke(self, message):
      message(self)

    def newMessage(self, activity, path, active_process, activity_kw, method_id, *args, **kw):
      # Some Security Cheking should be made here XXX
      global is_initialized
      if not is_initialized: self.initialize()
      if not hasattr(self, '_v_activity_buffer'): self._v_activity_buffer = ActivityBuffer()
      activity_dict[activity].queueMessage(self, Message(path, active_process, activity_kw, method_id, args, kw))

    def manageInvoke(self, object_path, method_id, REQUEST=None):
      """
        Invokes all methods for object "object_path"
      """
      if type(object_path) is type(''):
        object_path = tuple(object_path.split('/'))
      self.flush(object_path,method_id=method_id,invoke=1)
      if REQUEST is not None:
        return REQUEST.RESPONSE.redirect('%s/%s' % (self.absolute_url(), 'manageActivities'))

    def manageCancel(self, object_path, method_id, REQUEST=None):
      """
        Cancel all methods for object "object_path"
      """
      if type(object_path) is type(''):
        object_path = tuple(object_path.split('/'))
      self.flush(object_path,method_id=method_id,invoke=0)
      if REQUEST is not None:
        return REQUEST.RESPONSE.redirect('%s/%s' % (self.absolute_url(), 'manageActivities'))

    security.declarePublic('getMessageList')
    def getMessageList(self):
      """
        List messages waiting in queues
      """
      # Initialize if needed
      if not is_initialized: self.initialize()

      message_list = []
      for activity in activity_list:
        try:
          message_list += activity.getMessageList(self)
        except AttributeError:
          LOG('getMessageList, could not get message from Activity:',0,activity)
      return message_list

    security.declareProtected( CMFCorePermissions.ManagePortal , 'newActiveProcess' )
    def newActiveProcess(self, **kw):
      from ActiveProcess import addActiveProcess
      new_id = str(self.generateNewId())
      addActiveProcess(self, new_id)
      active_process = self._getOb(new_id)
      active_process.edit(**kw)
      return active_process

    def reindexObject(self):
      self.immediateReindexObject()

    def getActiveProcess(self):
      active_process = getattr(self, '_v_active_process')
      if active_process:
        return self.unrestrictedTraverse(active_process)
      return None

    # Active synchronisation methods
    def validateOrder(self, message, validator_id, validation_value):
      global is_initialized
      if not is_initialized: self.initialize()
      for activity in activity_list:
        method_id = "_validate_%s" % validator_id
        if hasattr(activity, method_id):
          if getattr(activity,method_id)(self, message, validation_value):
            return 1
      return 0
              
InitializeClass(ActivityTool)
