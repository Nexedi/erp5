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
from Products.CMFCore.PortalFolder import PortalFolder
from AccessControl import ClassSecurityInfo
from Products.CMFCore.utils import UniqueObject, _checkPermission, _getAuthenticatedUser
from Globals import InitializeClass, DTMLFile
from Acquisition import aq_base
from DateTime.DateTime import DateTime
import threading

from zLOG import LOG

# Using a RAM property (not a property of an instance) allows
# to prevent from storing a state in the ZODB (and allows to restart...)
active_threads = 0
max_active_threads = 1 # 2 will cause more bug to appear (he he)
is_initialized = 0

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
  def __init__(self, object, activity_kw, method_id, args, kw):
    if type(object) is type('a'):
      self.object_path = object.split('/')
    else:
      self.object_path = object.getPhysicalPath()
    self.activity_kw = activity_kw
    self.method_id = method_id
    self.args = args
    self.kw = kw
    self.__is_executed = 0
    # User Info ? REQUEST Info ?

  def __call__(self, activity_tool):
    try:
      LOG('WARNING ActivityTool', 0,
           'Trying to call method %s on object %s' % (self.method_id, self.object_path))
      object = activity_tool.unrestrictedTraverse(self.object_path)
      getattr(object, self.method_id)(*self.args, **self.kw)
      self.__is_executed = 1
    except:
      LOG('WARNING ActivityTool', 0,
           'Could not call method %s on object %s' % (self.method_id, self.object_path))
      self.__is_executed = 1

  def validate(self, activity, activity_tool):
    return activity.validate(activity_tool, self, **self.activity_kw)

class Method:

  def __init__(self, passive_self, activity, kw, method_id):
    self.__passive_self = passive_self
    self.__activity = activity
    self.__kw = kw
    self.__method_id = method_id

  def __call__(self, *args, **kw):
    m = Message(self.__passive_self, self.__kw, self.__method_id, args, kw)
    activity_dict[self.__activity].queueMessage(self.__passive_self.portal_activities, m)

class ActiveWrapper:

  def __init__(self, passive_self, activity, **kw):
    self.__dict__['__passive_self'] = passive_self
    self.__dict__['__activity'] = activity
    self.__dict__['__kw'] = kw

  def __getattr__(self, id):
    return Method(self.__dict__['__passive_self'], self.__dict__['__activity'],
                  self.__dict__['__kw'], id)

class ActivityTool (UniqueObject, PortalFolder):
    """
    This is a ZSQLCatalog that filters catalog queries.
    It is based on ZSQLCatalog
    """
    id = 'portal_activities'
    meta_type = 'CMF Activity Tool'
    security = ClassSecurityInfo()
    tic_lock = threading.Lock()

    manage_options = ( { 'label' : 'Overview', 'action' : 'manage_overview' }
                     , { 'label' : 'Activities', 'action' : 'manageActivities' }
                     ,
                     )


    security.declareProtected( CMFCorePermissions.ManagePortal , 'manageActivities' )
    manageActivities = DTMLFile( 'dtml/manageActivities', globals() )

    def initialize(self):
      global is_initialized
      from Activity import RAMQueue, RAMDict, SQLDict, ZODBDict
      # Initialize each queue
      for activity in activity_list:
        activity.initialize(self)
      is_initialized = 1

    security.declarePublic('tic')
    def tic(self, force=0):
      """
        Starts again an activity
      """
      global active_threads, is_initialized

      # return if the number of threads is too high
      if active_threads > max_active_threads:
        if not force: return 'Too many threads'

      if self.tic_lock is None:
        return

      # Initialize if needed
      if not is_initialized: self.initialize()

      # increase the number of active_threads
      self.tic_lock.acquire()
      active_threads += 1
      self.tic_lock.release()

      # Wakeup each queue
      for activity in activity_list:
        try:
          activity.wakeup(self)
        except:
          LOG('CMFActivity:', 100, 'Core call to wakeup failed for activity %s' % activity)

      # Process messages on each queue in round robin
      has_awake_activity = 1
      while has_awake_activity:
        has_awake_activity = 0
        for activity in activity_list:
          try:
          #if 1:
            activity.tic(self)
            get_transaction().commit()
            has_awake_activity = has_awake_activity or activity.isAwake(self)
          except:
            LOG('CMFActivity:', 100, 'Core call to tic or isAwake failed for activity %s' % activity)

      # decrease the number of active_threads
      self.tic_lock.acquire()
      active_threads -= 1
      self.tic_lock.release()

    def hasActivity(self, object, **kw):
      # Check in each queue if the object has deferred tasks
      for activity in activity_list:
        if activity.hasActivity(self, object, **kw):
          return 1
      return 0

    def activate(self, object, activity, **kw):
      global is_initialized
      if not is_initialized: self.initialize()
      return ActiveWrapper(object, activity, **kw)

    def flush(self, object, invoke=0, **kw):
      global is_initialized
      if not is_initialized: self.initialize()
      object_path = object.getPhysicalPath()
      for activity in activity_list:
        LOG('CMFActivity: ', 0, 'flushing activity %s' % activity.__class__.__name__)
        activity.flush(self, object_path, invoke=invoke, **kw)

    def invoke(self, message):
      message(self)

    def newMessage(self, activity, path, activity_kw, method_id, *args, **kw):
      global is_initialized
      if not is_initialized: self.initialize()
      activity_dict[activity].queueMessage(self, Message(path, activity_kw, method_id, args, kw))

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
      message_list = []
      for activity in activity_list:
        message_list += activity.getMessageList(self)
      return message_list

InitializeClass(ActivityTool)
