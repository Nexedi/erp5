from __future__ import absolute_import
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
from six import string_types as basestring
from Products.ERP5Type.Utils import ensure_list, str2unicode

import copy
import socket
from six.moves import urllib
import threading
import sys
import six
from collections import defaultdict
from six.moves.cPickle import dumps, loads
from Products.CMFCore import permissions as CMFCorePermissions
from Products.CMFActivity.ActiveResult import ActiveResult
from Products.CMFActivity.ActiveObject import DEFAULT_ACTIVITY
from Products.CMFActivity.ActivityConnection import ActivityConnection
from Products.PythonScripts.Utility import allow_class
from AccessControl import ClassSecurityInfo, Permissions
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import noSecurityManager
from AccessControl.SecurityManagement import setSecurityManager
from AccessControl.SecurityManagement import getSecurityManager
from AccessControl.users import system as system_user
from Products.CMFCore.utils import UniqueObject
from Products.ERP5Type.Globals import InitializeClass, DTMLFile
from Acquisition import aq_base, aq_inner, aq_parent
from .ActivityBuffer import ActivityBuffer
from .ActivityRuntimeEnvironment import BaseMessage
from zExceptions import ExceptionFormatter, Redirect
from BTrees.OIBTree import OIBTree
from BTrees.OOBTree import OOBTree
from Zope2 import app
from Products.ERP5Type.UnrestrictedMethod import PrivilegedUser
from zope.component.hooks import setSite
import transaction
from App.config import getConfiguration
from Shared.DC.ZRDB.Results import Results

from zope.globalrequest import getRequest, setRequest
from Products.MailHost.MailHost import MailHostError

from zLOG import LOG, INFO, WARNING, ERROR
import warnings
from time import sleep, time
from pprint import pformat

try:
  from Products.TimerService import getTimerService
except ImportError:
  def getTimerService(self):
    pass

from traceback import format_list, extract_stack

# Using a RAM property (not a property of an instance) allows
# to prevent from storing a state in the ZODB (and allows to restart...)
active_threads = 0
max_active_threads = 1 # 2 will cause more bug to appear (he he)
tic_lock = threading.Lock() # A RAM based lock to prevent too many concurrent tic() calls
timerservice_lock = threading.Lock() # A RAM based lock to prevent TimerService spamming when busy
is_running_lock = threading.Lock()
currentNode = None
_server_address = None
ROLE_IDLE = 0
ROLE_PROCESSING = 1

# Logging channel definitions
import logging
activity_tracking_logger = logging.getLogger('Tracking')
activity_timing_logger = logging.getLogger('CMFActivity.TimingLog')


def activity_timing_method(method, args, kw):
  begin = time()
  try:
    return method(*args, **kw)
  finally:
    end = time()
    activity_timing_logger.info('%.02fs: %r(*%r, **%r)' % (end - begin, method, args, kw))

def getServerAddress():
    """
    Return current server address
    """
    global _server_address
    if _server_address is None:
        ip = port = ''
        try:
            zopewsgi = sys.modules['Products.ERP5.bin.zopewsgi']
        except KeyError:
            pass
        else:
            ip, port = zopewsgi.server.addr
        if ip == '0.0.0.0':
            ip = socket.gethostbyname(socket.gethostname())
        _server_address = '%s:%s' %(ip, port)
    return _server_address

def getCurrentNode():
    """ Return current node identifier """
    global currentNode
    if currentNode is None:
      currentNode = getattr(
        getConfiguration(),
        'product_config',
        {},
      ).get('cmfactivity', {}).get('node-id')
    if currentNode is None:
      warnings.warn('Node name auto-generation is deprecated, please add a'
        '\n'
        '<product-config CMFActivity>\n'
        '  node-id = ...\n'
        '</product-config>\n'
        'section in your zope.conf, replacing "..." with a cluster-unique '
        'node identifier.', DeprecationWarning)
      currentNode = getServerAddress()
    return currentNode

# Here go ActivityBuffer instances
# Structure:
#  global_activity_buffer[activity_tool_path][thread_id] = ActivityBuffer
global_activity_buffer = defaultdict(dict)
from _thread import get_ident

MESSAGE_NOT_EXECUTED = 0
MESSAGE_EXECUTED = 1
MESSAGE_NOT_EXECUTABLE = 2


class SkippedMessage(Exception):
  pass


class Message(BaseMessage):
  """Activity Message Class.

  Message instances are stored in an activity queue, inside the Activity Tool.
  """

  active_process = None
  active_process_uid = None
  call_traceback = None
  exc_info = None
  exc_type = None
  is_executed = MESSAGE_NOT_EXECUTED
  traceback = None
  user_name = None
  user_object = None
  user_folder_path = None
  document_uid = None
  is_registered = False
  line = None

  def __init__(
      self,
      url,
      document_uid,
      active_process,
      active_process_uid,
      activity_kw,
      method_id,
      args, kw,
      request=None,
      portal_activities=None,
    ):
    self.object_path = url
    self.document_uid = document_uid
    self.active_process = active_process
    self.active_process_uid = active_process_uid
    self.activity_kw = activity_kw
    self.method_id = method_id
    self.args = args
    self.kw = kw
    if getattr(portal_activities, 'activity_creation_trace', False):
      # Save current traceback, to make it possible to tell where a message
      # was generated.
      # Strip last stack entry, since it will always be the same.
      self.call_traceback = ''.join(format_list(extract_stack()[:-1]))
    user = getSecurityManager().getUser()
    self.user_object = copy.deepcopy(aq_base(user))
    # Note: userfolders are not ERP5 objects, so use OFS API.
    self.user_folder_path = getattr(
      aq_parent(user),
      'getPhysicalPath',
      lambda: None,
    )()
    # Store REQUEST Info
    self.request_info = {}
    if request is not None:
      if 'SERVER_URL' in request.other:
        self.request_info['SERVER_URL'] = request.other['SERVER_URL']
      if 'VirtualRootPhysicalPath' in request.other:
        self.request_info['VirtualRootPhysicalPath'] = \
          request.other['VirtualRootPhysicalPath']
      if 'HTTP_ACCEPT_LANGUAGE' in request.environ:
        self.request_info['HTTP_ACCEPT_LANGUAGE'] = \
          request.environ['HTTP_ACCEPT_LANGUAGE']
      self.request_info['_script'] = list(request._script)

  @staticmethod
  def load(s, **kw):
    self = loads(s)
    self.__dict__.update(kw)
    return self

  dump = dumps

  def getGroupId(self):
    get = self.activity_kw.get
    group_method_id = get('group_method_id', '')
    if group_method_id is None:
      group_method_id = 'portal_activities/dummyGroupMethod/' + self.method_id
    return group_method_id + '\0' + get('group_id', '')

  def getGroupMethodCost(self):
    # Meaningless if called on a non-grouped message
    return self.activity_kw.get('group_method_cost', .01)

  def _getObject(self, activity_tool):
    obj = activity_tool.getPhysicalRoot()
    for id in self.object_path[1:]:
      obj = obj[id]
    return obj

  def getObject(self, activity_tool):
    """return the object referenced in this message."""
    try:
      obj = self._getObject(activity_tool)
    except KeyError:
      LOG('CMFActivity', WARNING, "Message dropped (no object found at path %r)"
          % (self.object_path,), error=True)
      self.setExecutionState(MESSAGE_NOT_EXECUTABLE)
    else:
      if self.document_uid and self.document_uid != getattr(aq_base(obj), 'uid', None):
        raise ValueError("UID mismatch for %r" % obj)
      return obj

  def getObjectList(self, activity_tool):
    """return the list of object that can be expanded from this message
    An expand method is used to expand the list of objects and to turn a
    big recursive transaction affecting many objects into multiple
    transactions affecting only one object at a time (this can prevent
    duplicated method calls)."""
    obj = self.getObject(activity_tool)
    if obj is None:
      return ()
    if 'expand_method_id' in self.activity_kw:
      return getattr(obj, self.activity_kw['expand_method_id'])()
    return obj,

  def getObjectCount(self, activity_tool):
    if 'expand_method_id' in self.activity_kw:
      try:
        obj = self._getObject(activity_tool)
        return len(getattr(obj, self.activity_kw['expand_method_id'])())
      except Exception:
        pass
    return 1

  def changeUser(self, activity_tool, annotate_transaction=True):
    """restore the security context for the calling user."""
    portal = activity_tool.getPortalObject()
    user = self.user_object
    if user is None and self.user_name is not None: # BBB
      user_name = self.user_name
      user_folder = portal_user_folder = portal.acl_users
      user = user_folder.getUserById(user_name)
      # if the user is not found, try to get it from a parent acl_users
      # XXX this is still far from perfect, because we need to store all
      # information about the user (like original user folder, roles) to
      # replay the activity with exactly the same security context as if
      # it had been executed without activity.
      if user is None:
        user_folder = portal.aq_parent.acl_users
        user = user_folder.getUserById(user_name)
      if user is None and user_name == system_user.getUserName():
        # The following logic partly comes from unrestricted_apply()
        # implementation in ERP5Type.UnrestrictedMethod but we get roles
        # from the portal to have more roles.
        user_folder = portal_user_folder
        user = PrivilegedUser(
          user_name,
          None,
          user_folder.valid_roles(),
          (),
        )
    else:
      user_folder = portal.getPhysicalRoot().unrestrictedTraverse(
        self.user_folder_path,
      )
      user_name = user.getIdOrUserName()
    if user is not None:
      user = user.__of__(user_folder)
      newSecurityManager(None, user)
      if annotate_transaction:
        if six.PY2:
          user_name = user_name.decode('utf-8')
        transaction.get().setUser(user_name, u'/'.join(user_folder.getPhysicalPath()))
    else :
      LOG("CMFActivity", WARNING,
          "Unable to find user %r in the portal" % user_name)
      noSecurityManager()
    return user

  def activateResult(self, active_process, result, object):
    if not isinstance(result, ActiveResult):
      result = ActiveResult(result=result)
    signature = self.activity_kw.get('signature')
    if signature:
      result.edit(id=signature)
    # XXX Allow other method_id in future
    result.edit(object_path=object, method_id=self.method_id)
    active_process.postResult(result)

  def __call__(self, activity_tool):
    try:
      obj = self.getObject(activity_tool)
      if obj is not None:
        old_security_manager = getSecurityManager()
        try:
          # Change user if required (TO BE DONE)
          # We will change the user only in order to execute this method
          self.changeUser(activity_tool)
          # XXX: There is no check to see if user is allowed to access
          #      that method !
          method = getattr(obj, self.method_id)
          transaction.get().note(
            u'CMFActivity {}/{}'.format(
              '/'.join([str2unicode(x) for x in self.object_path]),
              str2unicode(self.method_id),
            )
          )
          # Store site info
          setSite(activity_tool.getParentValue())
          if activity_tool.activity_timing_log:
            result = activity_timing_method(method, self.args, self.kw)
          else:
            result = method(*self.args, **self.kw)
        finally:
          setSecurityManager(old_security_manager)

        if method is not None:
          if self.active_process and result is not None:
            self.activateResult(
              activity_tool.unrestrictedTraverse(self.active_process),
              result, obj)
          self.setExecutionState(MESSAGE_EXECUTED)
    except:
      self.setExecutionState(MESSAGE_NOT_EXECUTED, context=activity_tool)

  def notifyUser(self, activity_tool, retry=False):
    """Notify the user that the activity failed."""
    if not activity_tool.activity_failure_mail_notification:
      return

    portal = activity_tool.getPortalObject()
    user_email = portal.getProperty('email_to_address',
                       portal.getProperty('email_from_address'))
    email_from_name = portal.getProperty('email_from_name',
                       portal.getProperty('email_from_address'))
    fail_count = self.line.retry + 1
    if retry:
      message = "Pending activity already failed %s times" % fail_count
    else:
      message = "Activity failed"
    path = '/'.join(self.object_path)
    mail_text = """From: %s <%s>
To: %s
Subject: %s: %s/%s

Node: %s
Failures: %s
User name: %r
Uid: %u
Document: %s
Method: %s
Arguments: %r
Named Parameters: %r
""" % (
      email_from_name, activity_tool.email_from_address, user_email, message,
      path, self.method_id, getCurrentNode(), fail_count,
      self.getUserId(),
      self.line.uid, path, self.method_id, self.args, self.kw,
    )
    if self.traceback:
      mail_text += '\nException:\n' + self.traceback
    if self.call_traceback:
      mail_text += '\nCreated at:\n' + self.call_traceback
    try:
      portal.MailHost.send(mail_text)
    except (socket.error, MailHostError) as message:
      LOG('ActivityTool.notifyUser', WARNING,
          'Mail containing failure information failed to be sent: %s' % message)

  def getUserId(self):
    user = self.user_object
    return (
      self.user_name
      if user is None else
      user.getIdOrUserName()
    )

  def reactivate(self, activity_tool, activity=DEFAULT_ACTIVITY):
    # Reactivate the original object.
    obj = self._getObject(activity_tool)
    old_security_manager = getSecurityManager()
    try:
      # Change user if required (TO BE DONE)
      # We will change the user only in order to execute this method
      user = self.changeUser(activity_tool)
      active_obj = obj.activate(activity=activity, **self.activity_kw)
      getattr(active_obj, self.method_id)(*self.args, **self.kw)
    finally:
      # Use again the previous user
      setSecurityManager(old_security_manager)

  def setExecutionState(self, is_executed, exc_info=None, log=True, context=None):
    """
      Set message execution state.

      is_executed can be one of MESSAGE_NOT_EXECUTED, MESSAGE_EXECUTED and
      MESSAGE_NOT_EXECUTABLE (variables defined above).

      exc_info must be - if given - similar to sys.exc_info() return value.

      log must be - if given - True or False. If True, a log line will be
      emited with failure details. This parameter should only be used when
      invoking this method on a list of messages to avoid log flood. It is
      caller's responsability to output a log line summing up all errors, and
      to store error in Zope's error_log.

      context must be - if given - an object wrapped in acquisition context.
      It is used to access Zope's error_log object. It is not used if log is
      False.

      If given state is not MESSAGE_EXECUTED, it will also store given
      exc_info. If not given, it will extract one using sys.exc_info().
      If final exc_info does not contain any exception, current stack trace
      will be stored instead: it will hopefuly help understand why message
      is in an error state.
    """
    assert is_executed in (MESSAGE_NOT_EXECUTED, MESSAGE_EXECUTED, MESSAGE_NOT_EXECUTABLE)
    self.is_executed = is_executed
    if is_executed == MESSAGE_NOT_EXECUTED:
      if not exc_info:
        exc_info = sys.exc_info()
      if self.on_error_callback is not None:
        self.exc_info = exc_info
      self.exc_type = exc_info[0]
      if exc_info[0] is None:
        # Raise a dummy exception, ignore it, fetch it and use it as if it was the error causing message non-execution. This will help identifyting the cause of this misbehaviour.
        try:
          raise Exception('Message execution failed, but there is no exception to explain it. This is a dummy exception so that one can track down why we end up here outside of an exception handling code path.')
        except Exception:
          exc_info = sys.exc_info()
      elif exc_info[0] is SkippedMessage:
        return
      if log:
        LOG('ActivityTool', WARNING, 'Could not call method %s on object %s. Activity created at:\n%s' % (self.method_id, self.object_path, self.call_traceback), error=exc_info)
        # push the error in ZODB error_log
        error_log = getattr(context, 'error_log', None)
        if error_log is not None:
          error_log.raising(exc_info)
      self.traceback = ''.join(ExceptionFormatter.format_exception(*exc_info)[1:])

  def getExecutionState(self):
    return self.is_executed

class GroupedMessage(object):
  __slots__ = 'object', '_message', 'result', 'exc_info'

  def __init__(self, object, message):
    self.object = object
    self._message = message

  args = property(lambda self: self._message.args)
  kw = property(lambda self: self._message.kw)

  def raised(self, exc_info=None):
    self.exc_info = exc_info or sys.exc_info()
    try:
      del self.result
    except AttributeError:
      pass

# XXX: Allowing restricted code to implement a grouping method is questionable
#      but there already exist some.
  __parent__ = property(lambda self: self.object) # for object
  _guarded_writes = 1 # for result
allow_class(GroupedMessage)

# Activity Registration
def activity_dict():
  from .Activity import SQLDict, SQLQueue, SQLJoblib
  return {k: getattr(v, k)() for k, v in six.iteritems(locals())}
activity_dict = activity_dict()


class Method(object):
  __slots__ = (
    '_portal_activities',
    '_passive_url',
    '_passive_uid',
    '_activity',
    '_active_process',
    '_active_process_uid',
    '_kw',
    '_method_id',
    '_request',
  )

  def __init__(self, portal_activities, passive_url, passive_uid, activity,
      active_process, active_process_uid, kw, method_id, request):
    self._portal_activities = portal_activities
    self._passive_url = passive_url
    self._passive_uid = passive_uid
    self._activity = activity
    self._active_process = active_process
    self._active_process_uid = active_process_uid
    self._kw = kw
    self._method_id = method_id
    self._request = request

  def __call__(self, *args, **kw):
    portal_activities = self._portal_activities
    m = Message(
      url=self._passive_url,
      document_uid=self._passive_uid,
      active_process=self._active_process,
      active_process_uid=self._active_process_uid,
      activity_kw=self._kw,
      method_id=self._method_id,
      args=args,
      kw=kw,
      request=self._request,
      portal_activities=portal_activities,
    )
    portal_activities.getActivityBuffer().deferredQueueMessage(
      portal_activities, activity_dict[self._activity], m)
    if portal_activities.activity_tracking and m.is_registered:
      activity_tracking_logger.info('queuing message: activity=%s, object_path=%s, method_id=%s, args=%s, kw=%s, activity_kw=%s, user_name=%s' % (self._activity, '/'.join(m.object_path), m.method_id, m.args, m.kw, m.activity_kw, m.getUserId()))

allow_class(Method)

class ActiveWrapper(object):
  __slots__ = (
    '__portal_activities',
    '__passive_url',
    '__passive_uid',
    '__activity',
    '__active_process',
    '__active_process_uid',
    '__kw',
    '__request',
  )
  # Shortcut security lookup (avoid calling __getattr__)
  __parent__ = None

  def __init__(self, portal_activities, url, uid, activity, active_process,
      active_process_uid, kw, request):
    # second parameter can be an object or an object's path
    self.__portal_activities = portal_activities
    self.__passive_url = url
    self.__passive_uid = uid
    self.__activity = activity
    self.__active_process = active_process
    self.__active_process_uid = active_process_uid
    self.__kw = kw
    self.__request = request

  def __getattr__(self, name):
    return Method(
      self.__portal_activities,
      self.__passive_url,
      self.__passive_uid,
      self.__activity,
      self.__active_process,
      self.__active_process_uid,
      self.__kw,
      name,
      self.__request,
    )

  def __repr__(self):
    return '<%s at 0x%x to %s>' % (self.__class__.__name__, id(self),
                                   self.__passive_url)

# True when activities cannot be executing any more.
has_processed_shutdown = False

def shutdown(timeout):
  """Signal ActivityTool that the application is shutting down.

  Prevent shutdown from happening while an activity queue is
  processing a batch.

  Returns true if shutdown could be processed before the timeout.
  """
  global has_processed_shutdown
  clean = True
  if not has_processed_shutdown:
    has_processed_shutdown = True
    LOG('CMFActivity', INFO, "Shutdown: Waiting for activities to finish.")
    if six.PY2:
      end = time() + timeout
      while time() < end:
        sleep(0.1)
        clean = is_running_lock.acquire(False)
        if clean:
          break
    else:
      clean = is_running_lock.acquire(timeout=timeout)
    LOG('CMFActivity', INFO, "Shutdown: Activities finished." )
  return clean


def cancelProcessShutdown():
  """This function reverts the effect of calling "shutdown".
  """
  global has_processed_shutdown
  is_running_lock.release()
  has_processed_shutdown = False


# Due to a circular import dependency between this module and
# Products.ERP5Type.Core.Folder, both modules must import after the definitions
# of getCurrentNode and Folder (the later is a base class of BaseTool).
from Products.ERP5Type.Tool.BaseTool import BaseTool
# Activating a path means we tried to avoid loading useless
# data in cache so there would be no gain to expect.
# And all nodes are likely to have tools already loaded.
NO_DEFAULT_NODE_PREFERENCE = str, BaseTool

class ActivityTool (BaseTool):
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
    title = 'Activities'
    allowed_types = ( 'CMF Active Process', )
    security = ClassSecurityInfo()

    manage_options = tuple(
                     [ { 'label' : 'Overview', 'action' : 'manage_overview' }
                     , { 'label' : 'Activities', 'action' : 'manageActivities' }
                     , { 'label' : 'LoadBalancing', 'action' : 'manageLoadBalancing'}
                     , { 'label' : 'Advanced', 'action' : 'manageActivitiesAdvanced' }
                     ,
                     ] + list(BaseTool.manage_options))

    security.declareProtected( CMFCorePermissions.ManagePortal , 'manageActivities' )
    manageActivities = DTMLFile( 'dtml/manageActivities', globals(), pformat=pformat )

    security.declareProtected( CMFCorePermissions.ManagePortal , 'manageActivitiesAdvanced' )
    manageActivitiesAdvanced = DTMLFile( 'dtml/manageActivitiesAdvanced', globals() )

    security.declareProtected( CMFCorePermissions.ManagePortal , 'manage_overview' )
    manage_overview = DTMLFile( 'dtml/explainActivityTool', globals() )

    security.declareProtected( CMFCorePermissions.ManagePortal , 'manageLoadBalancing' )
    manageLoadBalancing = DTMLFile( 'dtml/manageLoadBalancing', globals(), _getCurrentNode=getCurrentNode)

    distributingNode = ''
    _nodes = ()
    _family_list = ()
    _node_family_dict = None
    activity_creation_trace = False
    activity_tracking = False
    activity_timing_log = False
    activity_failure_mail_notification = False
    cancel_and_invoke_links_hidden = False

    # Filter content (ZMI))
    def filtered_meta_types(self, user=None):
        # Filters the list of available meta types.
        all = BaseTool.filtered_meta_types(self)
        meta_types = []
        for meta_type in self.all_meta_types():
            if meta_type['name'] in self.allowed_types:
                meta_types.append(meta_type)
        return meta_types

    def getSQLConnection(self):
      return self.aq_inner.aq_parent.cmf_activity_sql_connection()

    def maybeMigrateConnectionClass(self):
      connection_id = 'cmf_activity_sql_connection'
      sql_connection = getattr(self, connection_id, None)
      if (sql_connection is not None and
          not isinstance(sql_connection, ActivityConnection)):
        # SQL Connection migration is needed
        LOG('ActivityTool', WARNING, "Migrating MySQL Connection class")
        parent = aq_parent(aq_inner(sql_connection))
        parent._delObject(sql_connection.getId())
        new_sql_connection = ActivityConnection(connection_id,
                                                sql_connection.title,
                                                sql_connection.connection_string)
        parent._setObject(connection_id, new_sql_connection)

    security.declarePrivate('initialize')
    def initialize(self):
      self.maybeMigrateConnectionClass()
      for activity in six.itervalues(activity_dict):
        activity.initialize(self, clear=False)
      # Remove old skin if any.
      skins_tool = self.getPortalObject().portal_skins
      name = 'activity'
      if (getattr(skins_tool.get(name), '_dirpath', None)
          == 'Products.CMFActivity:skins/activity'):
        for selection, skins in skins_tool.getSkinPaths():
          skins = skins.split(',')
          try:
            skins.remove(name)
          except ValueError:
            continue
          skins_tool.manage_skinLayers(
            add_skin=1, skinname=selection, skinpath=skins)
        skins_tool._delObject(name)

    def _callSafeFunction(self, batch_function):
      return batch_function()

    security.declareProtected(Permissions.manage_properties, 'isSubscribed')
    def isSubscribed(self):
      """
      return True, if we are subscribed to TimerService.
      Otherwise return False.
      """
      service = getTimerService(self)
      if service:
        path = '/'.join(self.getPhysicalPath())
        return path in service.lisSubscriptions()
      LOG('ActivityTool', INFO, 'TimerService not available')
      return False

    security.declareProtected(Permissions.manage_properties, 'subscribe')
    def subscribe(self, REQUEST=None, RESPONSE=None):
        """ subscribe to the global Timer Service """
        service = getTimerService(self)
        url = '%s/manageLoadBalancing?manage_tabs_message=' %self.absolute_url()
        if not service:
            LOG('ActivityTool', INFO, 'TimerService not available')
            url += urllib.parse.quote('TimerService not available')
        else:
            service.subscribe(self)
            url += urllib.parse.quote("Subscribed to Timer Service")
        if RESPONSE is not None:
            RESPONSE.redirect(url)

    security.declareProtected(Permissions.manage_properties, 'unsubscribe')
    def unsubscribe(self, REQUEST=None, RESPONSE=None):
        """ unsubscribe from the global Timer Service """
        service = getTimerService(self)
        url = '%s/manageLoadBalancing?manage_tabs_message=' %self.absolute_url()
        if not service:
            LOG('ActivityTool', INFO, 'TimerService not available')
            url += urllib.parse.quote('TimerService not available')
        else:
            service.unsubscribe(self)
            url += urllib.parse.quote("Unsubscribed from Timer Service")
        if RESPONSE is not None:
            RESPONSE.redirect(url)

    security.declareProtected(Permissions.manage_properties, 'isActivityTrackingEnabled')
    def isActivityTrackingEnabled(self):
      return self.activity_tracking

    security.declareProtected(Permissions.manage_properties, 'manage_enableActivityTracking')
    def manage_enableActivityTracking(self, REQUEST=None, RESPONSE=None):
        """
          Enable activity tracing.
        """
        self.activity_tracking = True
        if RESPONSE is not None:
          url = '%s/manageActivitiesAdvanced?manage_tabs_message=' % self.absolute_url()
          url += urllib.parse.quote('Tracking log enabled')
          RESPONSE.redirect(url)

    security.declareProtected(Permissions.manage_properties, 'manage_disableActivityTracking')
    def manage_disableActivityTracking(self, REQUEST=None, RESPONSE=None):
        """
          Disable activity tracing.
        """
        self.activity_tracking = False
        if RESPONSE is not None:
          url = '%s/manageActivitiesAdvanced?manage_tabs_message=' % self.absolute_url()
          url += urllib.parse.quote('Tracking log disabled')
          RESPONSE.redirect(url)

    security.declareProtected(Permissions.manage_properties, 'isActivityMailNotificationEnabled')
    def isActivityMailNotificationEnabled(self):
      return self.activity_failure_mail_notification

    security.declareProtected(Permissions.manage_properties, 'manage_enableMailNotification')
    def manage_enableMailNotification(self, REQUEST=None, RESPONSE=None):
        """
          Enable mail notification when activity fails.
        """
        self.activity_failure_mail_notification = True
        if RESPONSE is not None:
          url = '%s/manageActivitiesAdvanced?manage_tabs_message=' % self.absolute_url()
          url += urllib.parse.quote('Mail notification enabled')
          RESPONSE.redirect(url)

    security.declareProtected(Permissions.manage_properties, 'manage_disableMailNotification')
    def manage_disableMailNotification(self, REQUEST=None, RESPONSE=None):
        """
          Disable mail notification when activity fails.
        """
        self.activity_failure_mail_notification = False
        if RESPONSE is not None:
          url = '%s/manageActivitiesAdvanced?manage_tabs_message=' % self.absolute_url()
          url += urllib.parse.quote('Mail notification disabled')
          RESPONSE.redirect(url)

    security.declareProtected(Permissions.manage_properties, 'isActivityTimingLoggingEnabled')
    def isActivityTimingLoggingEnabled(self):
      return self.activity_timing_log

    security.declareProtected(Permissions.manage_properties, 'manage_enableActivityTimingLogging')
    def manage_enableActivityTimingLogging(self, REQUEST=None, RESPONSE=None):
        """
          Enable activity timing logging.
        """
        self.activity_timing_log = True
        if RESPONSE is not None:
          url = '%s/manageActivitiesAdvanced?manage_tabs_message=' % self.absolute_url()
          url += urllib.parse.quote('Timing log enabled')
          RESPONSE.redirect(url)

    security.declareProtected(Permissions.manage_properties, 'manage_disableActivityTimingLogging')
    def manage_disableActivityTimingLogging(self, REQUEST=None, RESPONSE=None):
        """
          Disable activity timing logging.
        """
        self.activity_timing_log = False
        if RESPONSE is not None:
          url = '%s/manageActivitiesAdvanced?manage_tabs_message=' % self.absolute_url()
          url += urllib.parse.quote('Timing log disabled')
          RESPONSE.redirect(url)

    security.declareProtected(Permissions.manage_properties, 'isActivityCreationTraceEnabled')
    def isActivityCreationTraceEnabled(self):
      return self.activity_creation_trace

    security.declareProtected(Permissions.manage_properties, 'manage_enableActivityCreationTrace')
    def manage_enableActivityCreationTrace(self, REQUEST=None, RESPONSE=None):
        """
          Enable activity creation trace.
        """
        self.activity_creation_trace = True
        if RESPONSE is not None:
          url = '%s/manageActivitiesAdvanced?manage_tabs_message=' % self.absolute_url()
          url += urllib.parse.quote('Activity creation trace enabled')
          RESPONSE.redirect(url)

    security.declareProtected(Permissions.manage_properties, 'manage_disableActivityCreationTrace')
    def manage_disableActivityCreationTrace(self, REQUEST=None, RESPONSE=None):
        """
          Disable activity creation trace.
        """
        self.activity_creation_trace = False
        if RESPONSE is not None:
          url = '%s/manageActivitiesAdvanced?manage_tabs_message=' % self.absolute_url()
          url += urllib.parse.quote('Activity creation trace disabled')
          RESPONSE.redirect(url)

    security.declareProtected(Permissions.manage_properties, 'isCancelAndInvokeLinksHidden')
    def isCancelAndInvokeLinksHidden(self):
      return self.cancel_and_invoke_links_hidden

    security.declareProtected(Permissions.manage_properties, 'manage_hideCancelAndInvokeLinks')
    def manage_hideCancelAndInvokeLinks(self, REQUEST=None, RESPONSE=None):
        """
        """
        self.cancel_and_invoke_links_hidden = True
        if RESPONSE is not None:
          url = '%s/manageActivitiesAdvanced?manage_tabs_message=' % self.absolute_url()
          url += urllib.parse.quote('Cancel and invoke links hidden')
          RESPONSE.redirect(url)

    security.declareProtected(Permissions.manage_properties, 'manage_showCancelAndInvokeLinks')
    def manage_showCancelAndInvokeLinks(self, REQUEST=None, RESPONSE=None):
        """
        """
        self.cancel_and_invoke_links_hidden = False
        if RESPONSE is not None:
          url = '%s/manageActivitiesAdvanced?manage_tabs_message=' % self.absolute_url()
          url += urllib.parse.quote('Cancel and invoke links visible')
          RESPONSE.redirect(url)

    security.declarePrivate('manage_beforeDelete')
    def manage_beforeDelete(self, item, container):
        self.unsubscribe()
        BaseTool.inheritedAttribute('manage_beforeDelete')(self, item, container)

    security.declarePrivate('manage_afterAdd')
    def manage_afterAdd(self, item, container):
        self.subscribe()
        BaseTool.inheritedAttribute('manage_afterAdd')(self, item, container)

    security.declareProtected(CMFCorePermissions.ManagePortal, 'getServerAddress')
    def getServerAddress(self):
        """
        Backward-compatibility code only.
        """
        warnings.warn(
          '"getServerAddress" class method is deprecated, use "getServerAddress" module-level function instead.',
          DeprecationWarning,
          stacklevel=2,
        )
        return getServerAddress()

    security.declareProtected(CMFCorePermissions.ManagePortal, 'getCurrentNode')
    def getCurrentNode(self):
        """
        Backward-compatibility code only.
        """
        warnings.warn(
          '"getCurrentNode" class method is deprecated, use "getCurrentNode" module-level function instead.',
          DeprecationWarning,
          stacklevel=2,
        )
        return getCurrentNode()

    security.declareProtected(CMFCorePermissions.ManagePortal, 'getDistributingNode')
    def getDistributingNode(self):
        """ Return the distributingNode """
        return self.distributingNode

    def getNodeList(self, role=None):
      node_dict = self.getNodeDict()
      if role is None:
        result = [x for x in node_dict.keys()]
      else:
        result = [node_id for node_id, node_role in node_dict.items() if node_role == role]
      result.sort()
      return result

    def getNodeDict(self):
      nodes = self._nodes
      if isinstance(nodes, tuple):
        new_nodes = OIBTree()
        new_nodes.update([(x, ROLE_PROCESSING) for x in nodes])
        self._nodes = nodes = new_nodes
      return nodes

    def _getNodeFamilyIdDict(self):
      result = self._node_family_dict
      if result is None:
        result = self._node_family_dict = OOBTree()
      return result

    security.declareProtected(CMFCorePermissions.ManagePortal, 'getCurrentNodeFamilyIdSet')
    def getCurrentNodeFamilyIdSet(self):
      """
      Returns the tuple of family ids current node is member of.
      """
      return self._getNodeFamilyIdDict().get(getCurrentNode(), ())

    security.declareProtected(CMFCorePermissions.ManagePortal, 'getCurrentNodeFamilyNameSet')
    def getCurrentNodeFamilyNameSet(self):
      """
      Returns the tuple of family names current node is member of.
      """
      return [
        self._family_list[-x - 1]
        for x in self._getNodeFamilyIdDict().get(getCurrentNode(), ())
      ]

    security.declareProtected(CMFCorePermissions.ManagePortal, 'getFamilyId')
    def getFamilyId(self, name):
      """
      Raises ValueError for unknown family names.
      """
      # First family is -1, second is -2, etc.
      return -self._family_list.index(name) - 1

    security.declareProtected(CMFCorePermissions.ManagePortal, 'addNodeToFamily')
    def addNodeToFamily(self, node_id, family_name):
      """
      Silently does nothing if node is already a member of family_name.
      """
      family_id = self.getFamilyId(family_name)
      node_family_id_dict = self._getNodeFamilyIdDict()
      family_id_list = node_family_id_dict.get(node_id, ())
      if family_id not in family_id_list:
        node_family_id_dict[node_id] = family_id_list + (family_id, )

    security.declareProtected(CMFCorePermissions.ManagePortal, 'manage_addNodeSetToFamily')
    def manage_addNodeSetToFamily(self, family_new_node_list, REQUEST):
      """
      Add selected nodes to family.
      """
      family_name = REQUEST['manage_addNodeSetToFamily']
      if isinstance(family_new_node_list, basestring):
        family_new_node_list = [family_new_node_list]
      for node_id in family_new_node_list:
        self.addNodeToFamily(node_id, family_name)
      REQUEST.RESPONSE.redirect(
        REQUEST.URL1 + '/manageLoadBalancing?manage_tabs_message=' +
        urllib.parse.quote('Nodes added to family.'),
      )

    security.declareProtected(CMFCorePermissions.ManagePortal, 'removeNodeFromFamily')
    def removeNodeFromFamily(self, node_id, family_name):
      """
      Silently does nothing if node is not member of family_name.
      """
      family_id = self.getFamilyId(family_name)
      node_family_id_dict = self._getNodeFamilyIdDict()
      family_id_list = node_family_id_dict.get(node_id, ())
      if family_id in family_id_list:
        node_family_id_dict[node_id] = tuple(
          x
          for x in family_id_list
          if x != family_id
        )

    security.declareProtected(CMFCorePermissions.ManagePortal, 'manage_removeNodeSetFromFamily')
    def manage_removeNodeSetFromFamily(self, REQUEST):
      """
      Remove selected nodes from family.
      """
      family_name = REQUEST['manage_removeNodeSetFromFamily']
      node_to_remove_list = REQUEST['family_member_set_' + family_name]
      if isinstance(node_to_remove_list, basestring):
        node_to_remove_list = [node_to_remove_list]
      for node_id in node_to_remove_list:
        self.removeNodeFromFamily(node_id, family_name)
      REQUEST.RESPONSE.redirect(
        REQUEST.URL1 + '/manageLoadBalancing?manage_tabs_message=' +
        urllib.parse.quote('Nodes removed from family.'),
      )

    def _checkFamilyName(self, name):
      if not isinstance(name, basestring):
        raise TypeError('Name must be a string')
      if name in self._family_list:
        raise ValueError('Already in use')
      if name in ('', 'same'):
        raise ValueError('Reserved family name')

    security.declareProtected(CMFCorePermissions.ManagePortal, 'createFamily')
    def createFamily(self, name):
      """
      Raises ValueError if family already exists.
      """
      self._checkFamilyName(name)
      new_family_list = []
      for existing_name in self._family_list:
        if existing_name is None and name is not None:
          new_family_list.append(name)
          name = None
        else:
          new_family_list.append(existing_name)
      if name is None:
        # A free spot has been recycled.
        self._family_list = tuple(new_family_list)
      else:
        # No free spot, append.
        self._family_list += (name, )

    security.declareProtected(CMFCorePermissions.ManagePortal, 'manage_createFamily')
    def manage_createFamily(self, new_family_name, REQUEST, family_new_node_list=None):
      """Create a family"""
      redirect_url = REQUEST.URL1 + '/manageLoadBalancing?manage_tabs_message='
      if family_new_node_list is None:
        family_new_node_list = []
      elif isinstance(family_new_node_list, basestring):
        family_new_node_list = [family_new_node_list]
      try:
        self.createFamily(new_family_name)
        for node_id in family_new_node_list:
          self.addNodeToFamily(node_id, new_family_name)
      except ValueError as exc:
        raise Redirect(redirect_url + urllib.parse.quote(str(exc)))
      REQUEST.RESPONSE.redirect(redirect_url + urllib.parse.quote('Family created.'))

    security.declareProtected(CMFCorePermissions.ManagePortal, 'renameFamily')
    def renameFamily(self, old_name, new_name):
      """
      Raises ValueError if old_name does not exist.
      """
      self._checkFamilyName(new_name)
      family_list = self._family_list
      if old_name not in family_list:
        raise ValueError('Unknown family')
      self._family_list = tuple(
        new_name if x == old_name else x
        for x in family_list
      )

    security.declareProtected(CMFCorePermissions.ManagePortal, 'manage_renameFamily')
    def manage_renameFamily(self, REQUEST):
      """Rename a family"""
      redirect_url = REQUEST.URL1 + '/manageLoadBalancing?manage_tabs_message='
      old_family_name = REQUEST['manage_renameFamily']
      new_family_name = REQUEST['family_new_name_' + old_family_name]
      try:
        self.renameFamily(old_family_name, new_family_name)
      except ValueError as exc:
        raise Redirect(redirect_url + urllib.parse.quote(str(exc)))
      REQUEST.RESPONSE.redirect(redirect_url + urllib.parse.quote('Family renamed.'))

    security.declareProtected(CMFCorePermissions.ManagePortal, 'deleteFamily')
    def deleteFamily(self, name):
      """
      Raises ValueError if name does not exist.
      """
      for node_id in self._getNodeFamilyIdDict():
        self.removeNodeFromFamily(node_id, name)
      self._family_list = tuple(
        None if x == name else x
        for x in self._family_list
      )

    security.declareProtected(CMFCorePermissions.ManagePortal, 'manage_deleteFamily')
    def manage_deleteFamily(self, REQUEST):
      """Delete families"""
      redirect_url = REQUEST.URL1 + '/manageLoadBalancing?manage_tabs_message='
      family_name = REQUEST['manage_deleteFamily']
      try:
        self.deleteFamily(family_name)
      except ValueError as exc:
        raise Redirect(redirect_url + urllib.parse.quote(str(exc)))
      REQUEST.RESPONSE.redirect(redirect_url + urllib.parse.quote('Family deleted'))

    security.declareProtected(CMFCorePermissions.ManagePortal, 'getFamilyNameList')
    def getFamilyNameList(self):
      """
      Return the list of existing family names.
      """
      return [x for x in self._family_list if x is not None]

    security.declareProtected(CMFCorePermissions.ManagePortal, 'getFamilyNodeList')
    def getFamilyNodeList(self, family_name):
      """
      Return the list of node names in given family.
      """
      family_id = self.getFamilyId(family_name)
      return [
        x
        for x, y in self._getNodeFamilyIdDict().items()
        if family_id in y
      ]

    def registerNode(self, node):
      node_dict = self.getNodeDict()
      if node not in node_dict:
        if node_dict:
          # BBB: check if our node was known by address (processing and/or
          # distribution), and migrate it.
          server_address = getServerAddress()
          role = node_dict.pop(server_address, ROLE_IDLE)
          if self.distributingNode == server_address:
            self.distributingNode = node
        else:
          # We are registering the first node, make
          # it both the distributing node and a processing node.
          role = ROLE_PROCESSING
          self.distributingNode = node
        self.updateNode(node, role)

    def updateNode(self, node, role):
      node_dict = self.getNodeDict()
      node_dict[node] = role

    security.declareProtected(CMFCorePermissions.ManagePortal, 'getProcessingNodeList')
    def getProcessingNodeList(self):
      return self.getNodeList(role=ROLE_PROCESSING)

    security.declareProtected(CMFCorePermissions.ManagePortal, 'getIdleNodeList')
    def getIdleNodeList(self):
      return self.getNodeList(role=ROLE_IDLE)

    def _isValidNodeName(self, node_name) :
      """Check we have been provided a good node name"""
      return isinstance(node_name, str)

    security.declareProtected(CMFCorePermissions.ManagePortal, 'manage_setDistributingNode')
    def manage_setDistributingNode(self, distributingNode, REQUEST=None):
        """ set the distributing node """
        if not distributingNode or self._isValidNodeName(distributingNode):
          self.distributingNode = distributingNode
          if REQUEST is not None:
              REQUEST.RESPONSE.redirect(
                  REQUEST.URL1 +
                  '/manageLoadBalancing?manage_tabs_message=' +
                  urllib.parse.quote("Distributing Node successfully changed."))
        else :
          if REQUEST is not None:
              REQUEST.RESPONSE.redirect(
                  REQUEST.URL1 +
                  '/manageLoadBalancing?manage_tabs_message=' +
                  urllib.parse.quote("Malformed Distributing Node."))

    security.declareProtected(CMFCorePermissions.ManagePortal, 'manage_delNode')
    def manage_delNode(self, unused_node_list=None, REQUEST=None):
      """ delete selected unused nodes """
      processing_node = self.getDistributingNode()
      updated_processing_node = False
      if unused_node_list is not None:
        node_dict = self.getNodeDict()
        for node in unused_node_list:
          if node in node_dict:
            del node_dict[node]
          if node == processing_node:
            self.processing_node = ''
            updated_processing_node = True
      if REQUEST is not None:
        if unused_node_list is None:
          message = "No unused node selected, nothing deleted."
        else:
          message = "Deleted nodes %r." % (unused_node_list, )
        if updated_processing_node:
          message += "Disabled distributing node because it was deleted."
        REQUEST.RESPONSE.redirect(
          REQUEST.URL1 +
          '/manageLoadBalancing?manage_tabs_message=' +
          urllib.parse.quote(message))

    security.declareProtected(CMFCorePermissions.ManagePortal, 'manage_addToProcessingList')
    def manage_addToProcessingList(self, unused_node_list=None, REQUEST=None):
      """ Change one or more idle nodes into processing nodes """
      if unused_node_list is not None:
        for node in unused_node_list:
          self.updateNode(node, ROLE_PROCESSING)
      if REQUEST is not None:
        if unused_node_list is None:
          message = "No unused node selected, nothing done."
        else:
          message = "Nodes now procesing: %r." % (unused_node_list, )
        REQUEST.RESPONSE.redirect(
          REQUEST.URL1 +
          '/manageLoadBalancing?manage_tabs_message=' +
          urllib.parse.quote(message))

    security.declareProtected(CMFCorePermissions.ManagePortal, 'manage_removeFromProcessingList')
    def manage_removeFromProcessingList(self, processing_node_list=None, REQUEST=None):
      """ Change one or more procesing nodes into idle nodes """
      if processing_node_list is not None:
        for node in processing_node_list:
          self.updateNode(node, ROLE_IDLE)
      if REQUEST is not None:
        if processing_node_list is None:
          message = "No used node selected, nothing done."
        else:
          message = "Nodes now unused %r." % (processing_node_list, )
        REQUEST.RESPONSE.redirect(
          REQUEST.URL1 +
          '/manageLoadBalancing?manage_tabs_message=' +
          urllib.parse.quote(message))

    security.declareProtected(CMFCorePermissions.ManagePortal, 'process_timer')
    def process_timer(self, tick, interval, prev="", next=""):
      """
      Call distribute() if we are the Distributing Node and call tic()
      with our node number.
      This method is called by TimerService in the interval given
      in zope.conf. The Default is every 5 seconds.
      """
      # Prevent TimerService from starting multiple threads in parallel
      if timerservice_lock.acquire(0):
        try:
          # make sure our skin is set-up. On CMF 1.5 it's setup by acquisition,
          # but on 2.2 it's by traversal, and our site probably wasn't traversed
          # by the timerserver request, which goes into the Zope Control_Panel
          # calling it a second time is a harmless and cheap no-op.
          # both setupCurrentSkin and REQUEST are acquired from containers.
          self.setupCurrentSkin(self.REQUEST)
          old_sm = getSecurityManager()
          try:
            # get owner of portal_catalog, so normally we should be able to
            # have the permission to invoke all activities
            user = self.portal_catalog.getWrappedOwner()
            newSecurityManager(self.REQUEST, user)

            currentNode = getCurrentNode()
            self.registerNode(currentNode)
            processing_node_list = self.getNodeList(role=ROLE_PROCESSING)

            # only distribute when we are the distributingNode
            if self.getDistributingNode() == currentNode:
              self.distribute(len(processing_node_list))

            # SkinsTool uses a REQUEST cache to store skin objects, as
            # with TimerService we have the same REQUEST over multiple
            # portals, we clear this cache to make sure the cache doesn't
            # contains skins from another portal.
            try:
              self.getPortalObject().portal_skins.changeSkin(None)
            except AttributeError:
              pass

            # call tic for the current processing_node
            # the processing_node numbers are the indices of the elements
            # in the node tuple +1 because processing_node starts form 1
            if currentNode in processing_node_list:
              self.tic(processing_node_list.index(currentNode) + 1)
          except:
            # Catch ALL exception to avoid killing timerserver.
            LOG('ActivityTool', ERROR, 'process_timer received an exception',
                error=True)
          finally:
            setSecurityManager(old_sm)
        finally:
          timerservice_lock.release()

    security.declarePublic('distribute')
    def distribute(self, node_count=1):
      """
        Distribute load
      """
      inner_self = aq_inner(self)
      while is_running_lock.acquire(0):
        try:
          # Note: "has_more_to_distribute" is to be taken in a lose sense, we
          # do not positively know there is more, just that distribute returned
          # before it could confirm there is nothing left to do.
          has_more_to_distribute = False
          # Call distribute on each queue
          for activity in six.itervalues(activity_dict):
            has_more_to_distribute |= activity.distribute(inner_self, node_count)
          if not has_more_to_distribute:
            break
        finally:
          is_running_lock.release()
          if has_processed_shutdown:
            break

    security.declarePublic('tic')
    def tic(self, processing_node=1, force=0):
      """
        Starts again an activity
        processing_node starts from 1 (there is not node 0)
      """
      global active_threads

      # return if the number of threads is too high
      # else, increase the number of active_threads and continue
      with tic_lock:
        too_many_threads = (active_threads >= max_active_threads)
        if not too_many_threads or force:
          active_threads += 1
        else:
          raise RuntimeError('Too many threads')

      inner_self = aq_inner(self)

      try:
        # Loop as long as there are activities. Always process the queue with
        # "highest" priority. If several queues have same highest priority,
        # use a round-robin algorithm.
        # XXX: We always finish by iterating over all queues, in case that
        #      getPriority does not see messages dequeueMessage would process.
        activity_list = ensure_list(activity_dict.values())
        def sort_key(activity):
          return activity.getPriority(self, processing_node,
            node_family_id_set)
        while is_running_lock.acquire(0):
          try:
            # May have changed since previous iteration.
            node_family_id_set = self.getCurrentNodeFamilyIdSet()
            activity_list.sort(key=sort_key) # stable sort
            for i, activity in enumerate(activity_list):
              # Transaction processing is the responsability of the activity
              if activity.dequeueMessage(inner_self, processing_node,
                node_family_id_set):
                activity_list.append(activity_list.pop(i))
                break
            else:
              break
          finally:
            is_running_lock.release()
            if has_processed_shutdown:
              break

      finally:
        # decrease the number of active_threads
        with tic_lock:
          active_threads -= 1

    def hasActivity(self, *args, **kw):
      # Check in each queue if the object has deferred tasks
      # if not argument is provided, then check on self
      if args:
        obj, = args
      else:
        obj = self
      path = None if obj is None else '/'.join(obj.getPhysicalPath())
      db = self.getSQLConnection()
      quote = db.string_literal
      return bool(db.query(b"(%s)" % b") UNION ALL (".join(
        activity.hasActivitySQL(quote, path=path, **kw)
        for activity in six.itervalues(activity_dict)))[1])

    security.declarePrivate('getActivityBuffer')
    def getActivityBuffer(self, create_if_not_found=True):
      """
        Get activtity buffer for this thread for this activity tool.
        If no activity buffer is found at lowest level and create_if_not_found
        is True, create one.
        Intermediate level is unconditionaly created if non existant because
        chances are it will be used in the instance life.
      """
      # XXX: using a volatile attribute to cache getPhysicalPath result.
      # This cache may need invalidation if all the following is
      # simultaneously true:
      # - ActivityTool instances can be moved in object tree
      # - moved instance is used to get access to its activity buffer
      # - another instance is put in the place of the original, and used to
      #   access its activity buffer
      # ...which seems currently unlikely, and as such is left out.
      try:
        my_instance_key = self._v_physical_path
      except AttributeError:
        # Safeguard: make sure we are wrapped in acquisition context before
        # using our path as an activity tool instance-wide identifier.
        assert getattr(self, 'aq_self', None) is not None
        self._v_physical_path = my_instance_key = self.getPhysicalPath()
      thread_activity_buffer = global_activity_buffer[my_instance_key]
      my_thread_key = get_ident()
      try:
        return thread_activity_buffer[my_thread_key]
      except KeyError:
        if create_if_not_found:
          buffer = ActivityBuffer()
        else:
          buffer = None
        thread_activity_buffer[my_thread_key] = buffer
        return buffer

    def activateObject(self, object, activity=DEFAULT_ACTIVITY,
                       active_process=None, serialization_tag=None,
                       node=None, uid=None, **kw):
      if active_process is None:
        active_process_uid = None
      elif isinstance(active_process, str):
        # TODO: deprecate
        active_process_uid = self.unrestrictedTraverse(active_process).getUid()
      else:
        active_process_uid = active_process.getUid()
        active_process = active_process.getPhysicalPath()
      if isinstance(object, str):
        url = tuple(object.split('/'))
      else:
        if uid is not None:
          raise ValueError
        uid = getattr(aq_base(object), 'uid', None)
        url = object.getPhysicalPath()
      if serialization_tag is not None:
        kw['serialization_tag'] = serialization_tag
      while 1: # not a loop
        if node is None:
          # The caller lets us decide whether we prefer to execute on same node
          # (to increase the efficiency of the ZODB Storage cache).
          if (isinstance(object, NO_DEFAULT_NODE_PREFERENCE)
              # A grouped activity is the sign we may have many of them so make
              # sure that this node won't overprioritize too many activities.
              or kw.get('group_method_id', '') != ''):
            break
        elif node == '':
          break
        elif node != 'same':
          kw['node'] = self.getFamilyId(node)
          break
        try:
          kw['node'] = 1 + self.getNodeList(
            role=ROLE_PROCESSING).index(getCurrentNode())
        except ValueError:
          pass
        break
      return ActiveWrapper(self, url, uid, activity,
                           active_process, active_process_uid, kw,
                           getattr(self, 'REQUEST', None))

    def getRegisteredMessageList(self, activity):
      activity_buffer = self.getActivityBuffer(create_if_not_found=False)
      if activity_buffer is not None:
        #activity_buffer._register() # This is required if flush flush is called outside activate
        return activity.getRegisteredMessageList(activity_buffer,
                                                 aq_inner(self))
      else:
        return []

    def unregisterMessage(self, activity, message):
      activity_buffer = self.getActivityBuffer()
      #activity_buffer._register()
      return activity.unregisterMessage(activity_buffer, aq_inner(self), message)

    def flush(self, obj, invoke=0, **kw):
      self.getActivityBuffer()
      if isinstance(obj, tuple):
        object_path = obj
      else:
        object_path = obj.getPhysicalPath()
      for activity in six.itervalues(activity_dict):
        activity.flush(aq_inner(self), object_path, invoke=invoke, **kw)

    def invoke(self, message):
      if self.activity_tracking:
        activity_tracking_logger.info('invoking message: object_path=%s, method_id=%s, args=%r, kw=%r, activity_kw=%r, user_name=%s' % ('/'.join(message.object_path), message.method_id, message.args, message.kw, message.activity_kw, message.getUserId()))
      if getattr(self, 'aq_chain', None) is not None:
        # Grab existing acquisition chain and extrach base objects.
        base_chain = [aq_base(x) for x in self.aq_chain]
        # Grab existig request (last chain item) and create a copy.
        request_container = base_chain.pop()
        request = request_container.REQUEST
        # Generate PARENTS value. Sadly, we cannot reuse base_chain since
        # PARENTS items must be wrapped in acquisition
        parents = []
        application = self.getPhysicalRoot().aq_base
        for parent in self.aq_chain:
          if parent.aq_base is application:
            break
          parents.append(parent)
        # XXX: REQUEST.clone() requires PARENTS to be set, and it's not when
        # runing unit tests. Recreate it if it does not exist.
        if getattr(request.other, 'PARENTS', None) is None:
          request.other['PARENTS'] = parents
        # XXX: PATH_INFO might not be set when runing unit tests.
        if request.environ.get('PATH_INFO') is None:
          request.environ['PATH_INFO'] = '/Control_Panel/timer_service/process_timer'

        # restore request information
        old_request = getRequest()
        new_request = request.clone()
        setRequest(new_request)
        request_info = message.request_info
        # PARENTS is truncated by clone
        new_request.other['PARENTS'] = parents
        if '_script' in request_info:
          new_request._script = request_info['_script']
        if 'SERVER_URL' in request_info:
          new_request.other['SERVER_URL'] = request_info['SERVER_URL']
        if 'VirtualRootPhysicalPath' in request_info:
          new_request.other['VirtualRootPhysicalPath'] = request_info['VirtualRootPhysicalPath']
        if 'HTTP_ACCEPT_LANGUAGE' in request_info:
          new_request.environ['HTTP_ACCEPT_LANGUAGE'] = request_info['HTTP_ACCEPT_LANGUAGE']
          new_request.processInputs()

        new_request_container = request_container.__class__(REQUEST=new_request)
        # Recreate acquisition chain.
        my_self = new_request_container
        base_chain.reverse()
        for item in base_chain:
          my_self = item.__of__(my_self)
      else:
        my_self = self
        LOG('CMFActivity.ActivityTool.invoke', INFO, 'Strange: invoke is called outside of acquisition context.')
      try:
        message(my_self)
      finally:
        if my_self is not self: # We rewrapped self
          # Restore default skin selection
          skinnable = self.getPortalObject()
          skinnable.changeSkin(skinnable.getSkinNameFromRequest(request))
        setRequest(old_request)
      if self.activity_tracking:
        activity_tracking_logger.info('invoked message')
      if my_self is not self: # We rewrapped self
        for held in my_self.REQUEST._held:
          self.REQUEST._hold(held)

    def invokeGroup(self, method_id, message_list, activity, merge_duplicate):
      if self.activity_tracking:
        activity_tracking_logger.info(
          'invoking group messages: method_id=%s, paths=%s'
          % (method_id, ['/'.join(m.object_path) for m in message_list]))
      # Invoke a group method.
      message_dict = {}
      path_set = set()
      # Filter the list of messages. If an object is not available, mark its
      # message as non-executable. In addition, expand an object if necessary,
      # and make sure that no duplication happens.
      for m in message_list:
        # alternate method is used to segregate objects which cannot be grouped.
        alternate_method_id = m.activity_kw.get('alternate_method_id')
        try:
          object_list = m.getObjectList(self)
          if object_list is None:
            continue
          message_dict[m] = expanded_object_list = []
          for subobj in object_list:
            if merge_duplicate:
              path = subobj.getPath()
              if path in path_set:
                continue
              path_set.add(path)
            if alternate_method_id is not None \
               and hasattr(aq_base(subobj), alternate_method_id):
              # if this object is alternated,
              # generate a new single active object
              activity_kw = m.activity_kw.copy()
              activity_kw.pop('group_method_id', None)
              activity_kw.pop('group_id', None)
              active_obj = subobj.activate(activity=activity, **activity_kw)
              getattr(active_obj, alternate_method_id)(*m.args, **m.kw)
            else:
              expanded_object_list.append(GroupedMessage(subobj, m))
        except:
          m.setExecutionState(MESSAGE_NOT_EXECUTED, context=self)

      expanded_object_list = sum(six.itervalues(message_dict), [])
      try:
        if expanded_object_list:
          # Store site info
          setSite(self.getParentValue())
          traverse = self.getPortalObject().unrestrictedTraverse
          # FIXME: how to apply security here?
          # NOTE: The callee must update each processed item of
          #       expanded_object_list, by setting:
          #       - 'exc_info' in case of error
          #       - 'result' otherwise, with None or the result to post
          #          on the active process
          #       Skipped item must not be touched.
          traverse(method_id)(expanded_object_list)
      except:
        # In this case, the group method completely failed.
        exc_info = sys.exc_info()
        for m in message_dict:
          m.setExecutionState(MESSAGE_NOT_EXECUTED, exc_info, log=False)
        LOG('WARNING ActivityTool', 0,
            'Could not call method %s on objects %s' %
            (method_id, [x.object for x in expanded_object_list]),
            error=exc_info)
        error_log = getattr(self, 'error_log', None)
        if error_log is not None:
          error_log.raising(exc_info)
      else:
        # Note there can be partial failures.
        for m, expanded_object_list in six.iteritems(message_dict):
          result_list = []
          for result in expanded_object_list:
            try:
              if result.result is not None:
                result_list.append(result)
            except AttributeError:
              exc_info = getattr(result, "exc_info", (SkippedMessage,))
              break # failed or skipped message
          else:
            try:
              if result_list and m.active_process:
                active_process = traverse(m.active_process)
                for result in result_list:
                  m.activateResult(active_process, result.result, result.object)
            except:
              exc_info = None
            else:
              m.setExecutionState(MESSAGE_EXECUTED, context=self)
              continue
          m.setExecutionState(MESSAGE_NOT_EXECUTED, exc_info, context=self)
      exc_info = None
      if self.activity_tracking:
        activity_tracking_logger.info('invoked group messages')

    security.declarePrivate('dummyGroupMethod')
    class dummyGroupMethod(object):
      def __bobo_traverse__(self, REQUEST, method_id):
        def group_method(message_list):
          sm = getSecurityManager()
          try:
            for m in message_list:
              m._message.changeUser(m.object, annotate_transaction=False)
              m.result = getattr(m.object, method_id)(*m.args, **m.kw)
          except Exception:
            m.raised()
          finally:
            setSecurityManager(sm)
        return group_method
    dummyGroupMethod = dummyGroupMethod()

    def newMessage(self, activity, path, active_process,
                   activity_kw, method_id, *args, **kw):
      # Some Security Cheking should be made here XXX
      self.getActivityBuffer()
      activity_dict[activity].queueMessage(aq_inner(self),
        Message(path, active_process, activity_kw, method_id, args, kw,
          portal_activities=self))

    security.declareProtected( CMFCorePermissions.ManagePortal, 'manageInvoke' )
    def manageInvoke(self, object_path, method_id, REQUEST=None):
      """
        Invokes all methods for object "object_path"
      """
      if type(object_path) is type(''):
        object_path = tuple(object_path.split('/'))
      self.flush(object_path,method_id=method_id,invoke=1)
      if REQUEST is not None:
        return REQUEST.RESPONSE.redirect('%s/%s' %
                (self.absolute_url(), 'manageActivities'))

    security.declareProtected( CMFCorePermissions.ManagePortal, 'manageRestart')
    def manageRestart(self, message_uid_list, activity, REQUEST=None):
      """
        Restart one or several messages
      """
      if not(isinstance(message_uid_list, list)):
        message_uid_list = [message_uid_list]
      if message_uid_list:
        activity_dict[activity].assignMessageList(self.getSQLConnection(),
                                                     0, message_uid_list)
      if REQUEST is not None:
        return REQUEST.RESPONSE.redirect('%s/%s' % (
          self.absolute_url(), 'view'))

    security.declareProtected( CMFCorePermissions.ManagePortal, 'manageCancel' )
    def manageCancel(self, object_path, method_id, REQUEST=None):
      """
        Cancel all methods for object "object_path"
      """
      LOG('ActivityTool', WARNING,
          '"manageCancel" method is deprecated, use "manageDelete" instead.')
      if type(object_path) is type(''):
        object_path = tuple(object_path.split('/'))
      self.flush(object_path,method_id=method_id,invoke=0)
      if REQUEST is not None:
        return REQUEST.RESPONSE.redirect('%s/%s' % (
          self.absolute_url(), 'manageActivities'))

    security.declareProtected( CMFCorePermissions.ManagePortal, 'manageDelete' )
    def manageDelete(self, message_uid_list, activity, REQUEST=None):
      """
        Delete one or several messages
      """
      if not(isinstance(message_uid_list, list)):
        message_uid_list = [message_uid_list]
      activity_dict[activity].deleteMessageList(
        self.getSQLConnection(), message_uid_list)
      if REQUEST is not None:
        return REQUEST.RESPONSE.redirect('%s/%s' % (
          self.absolute_url(), 'view'))

    security.declareProtected( CMFCorePermissions.ManagePortal,
                               'manageClearActivities' )
    def manageClearActivities(self, keep=1, RESPONSE=None):
      """
        Recreate tables, clearing all activities
      """
      for activity in six.itervalues(activity_dict):
        activity.initialize(self, clear=True)

      if RESPONSE is not None:
        return RESPONSE.redirect(self.absolute_url_path() +
          '/manageActivitiesAdvanced?manage_tabs_message=Activities%20Cleared')


    security.declareProtected( CMFCorePermissions.ManagePortal,
                               'getMessageTempObjectList')
    def getMessageTempObjectList(self, **kw):
      """
        Get object list of messages waiting in queues
      """
      message_list = self.getMessageList(**kw)
      object_list = []
      for sql_message in message_list:
        message = self.newContent(
          portal_type="Active Process",
          temp_object=1,
        )
        message.__dict__.update(**sql_message.__dict__)
        object_list.append(message)
      return object_list

    security.declarePublic('getMessageList')
    def getMessageList(self, activity=None, **kw):
      """
        List messages waiting in queues
      """
      if activity:
        return activity_dict[activity].getMessageList(aq_inner(self), **kw)

      message_list = []
      for activity in six.itervalues(activity_dict):
        try:
          message_list += activity.getMessageList(aq_inner(self), **kw)
        except AttributeError:
          LOG('getMessageList, could not get message from Activity:',0,activity)
      return message_list

    security.declarePublic('countMessageWithTag')
    def countMessageWithTag(self, value):
      """
        Return the number of messages which match the given tag.
      """
      return self.countMessage(tag=value)

    security.declarePublic('countMessage')
    def countMessage(self, **kw):
      """
        Return the number of messages which match the given parameter.

        Parameters allowed:

        method_id : the id of the method
        path : for activities on a particular object
        tag : activities with a particular tag
        message_uid : activities with a particular uid
      """
      db = self.getSQLConnection()
      quote = db.string_literal
      return sum(x for x, in db.query(b"(%s)" % b") UNION ALL (".join(
        activity.countMessageSQL(quote, **kw)
        for activity in six.itervalues(activity_dict)))[1])

    security.declareProtected( CMFCorePermissions.ManagePortal , 'newActiveProcess' )
    def newActiveProcess(self, REQUEST=None, **kw):
      # note: if one wants to create an Actice Process without ERP5 products,
      # she can call ActiveProcess.addActiveProcess
      obj = self.newContent(portal_type="Active Process", **kw)
      if REQUEST is not None:
        REQUEST['RESPONSE'].redirect( 'manage_main' )
      return obj

    security.declarePrivate('getSQLTableNameSet')
    def getSQLTableNameSet(self):
      return [x.sql_table for x in six.itervalues(activity_dict)]

    # Required for tests (time shift)
    def timeShift(self, delay):
      for activity in six.itervalues(activity_dict):
        activity.timeShift(aq_inner(self), delay)

InitializeClass(ActivityTool)
