##############################################################################
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solane <jp@nexedi.com>
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
from AccessControl import ClassSecurityInfo
from Products.CMFCore.utils import UniqueObject, _checkPermission, _getAuthenticatedUser
from Globals import InitializeClass, DTMLFile, get_request
from Acquisition import aq_base
from DateTime.DateTime import DateTime
import threading

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
    self.activity_kw = activity_kw
    self.method_id = method_id
    self.args = args
    self.kw = kw
    self.is_executed = 0
    # User Info ? REQUEST Info ?

  def __call__(self, activity_tool):
    try:
      LOG('WARNING ActivityTool', 0,
           'Trying to call method %s on object %s' % (self.method_id, self.object_path))
      object = activity_tool.unrestrictedTraverse(self.object_path)
      REQUEST = get_request()
      REQUEST.active_process = self.active_process
      result = getattr(object, self.method_id)(*self.args, **self.kw)
      if REQUEST.active_process is not None:
        active_process = activity_tool.getActiveProcess()
        active_process.activateResult(result) # XXX Allow other method_id in future
      self.is_executed = 1
    except:
      self.is_executed = 0
      LOG('WARNING ActivityTool', 0,
           'Could not call method %s on object %s' % (self.method_id, self.object_path))

  def validate(self, activity, activity_tool):
    return activity.validate(activity_tool, self, **self.activity_kw)

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
    This is a ZSQLCatalog that filters catalog queries.
    It is based on ZSQLCatalog
    """
    id = 'portal_activities'
    meta_type = 'CMF Activity Tool'
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
      from Activity import RAMQueue, RAMDict, SQLDict
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
        #if 1:
          activity.distribute(self, node_count)
        except:
        #else:
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
          #if 1:
            activity.tic(self, processing_node) # Transaction processing is the responsability of the activity
            has_awake_activity = has_awake_activity or activity.isAwake(self, processing_node)
          except:
          #else:
            LOG('CMFActivity:', 100, 'Core call to tic or isAwake failed for activity %s' % activity)

      # decrease the number of active_threads
      tic_lock.acquire()
      active_threads -= 1
      tic_lock.release()

    def hasActivity(self, object, **kw):
      # Check in each queue if the object has deferred tasks
      for activity in activity_list:
        if activity.hasActivity(self, object, **kw):
          return 1
      return 0

    def activate(self, object, activity, active_process, **kw):
      global is_initialized
      if not is_initialized: self.initialize()
      return ActiveWrapper(object, activity, active_process, **kw)

    def flush(self, object, invoke=0, **kw):
      global is_initialized
      if not is_initialized: self.initialize()
      object_path = object.getPhysicalPath()
      for activity in activity_list:
        LOG('CMFActivity: ', 0, 'flushing activity %s' % activity.__class__.__name__)
        activity.flush(self, object_path, invoke=invoke, **kw)

    def invoke(self, message):
      message(self)

    def newMessage(self, activity, path, active_process, activity_kw, method_id, *args, **kw):
      # Some Security Cheking should be made here XXX
      global is_initialized
      if not is_initialized: self.initialize()
      activity_dict[activity].queueMessage(self, Message(path, active_process, activity_kw, method_id, args, kw))

    def manageInvoke(self, object_path, method_id, REQUEST=None):
      """
        Invokes all methods for object "object_path"
      """
      if type(object_path) is type(''):
        object_path = tuple(object_path.split('/'))
      for activity in activity_list:
        activity.flush(self, object_path, method_id=method_id, invoke=1)
      if REQUEST is not None:
        return REQUEST.RESPONSE.redirect('%s/%s' % (self.absolute_url(), 'manageActivities'))

    def manageCancel(self, object_path, method_id, REQUEST=None):
      """
        Cancel all methods for object "object_path"
      """
      if type(object_path) is type(''):
        object_path = tuple(object_path.split('/'))
      for activity in activity_list:
        activity.flush(self, object_path, method_id=method_id, invoke=0)
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
        message_list += activity.getMessageList(self)
      return message_list

    security.declareProtected( CMFCorePermissions.ManagePortal , 'newActiveProcess' )
    def newActiveProcess(self):
      from ActiveProcess import addActiveProcess
      new_id = str(self.generateNewId())
      addActiveProcess(self, new_id)
      return self._getOb(new_id)

    def reindexObject(self):
      self.immediateReindexObject()

    def getActiveProcess(self):
      REQUEST = get_request()
      if REQUEST.active_process:
        return self.unrestrictedTraverse(REQUEST.active_process)
      return None


InitializeClass(ActivityTool)
