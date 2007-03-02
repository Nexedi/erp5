##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
#          Jean-Paul Smets-Solanes <jp@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
#
# Based on: db.py in ZMySQLDA
#
##############################################################################

from Shared.DC.ZRDB.TM import TM
from zLOG import LOG, ERROR, INFO
import sys
import threading

try:
  from transaction import get as get_transaction
except ImportError:
  pass

# This variable is used to store thread-local buffered information.
# This must be RAM-based, because the use of a volatile attribute does
# not guarantee that the information persists until the end of a
# transaction, but we need to assure that the information is accessible
# for flushing activities. So the approach here is that information is
# stored in RAM, and removed at _finish and _abort, so that the information
# would not span over transactions.
buffer_dict_lock = threading.Lock()
buffer_dict = {}

class ActivityBuffer(TM):

  _p_oid=_p_changed=_registered=None

  def __init__(self, activity_tool=None):
    self.requires_prepare = 0

    # Directly store the activity tool as an attribute. At the beginning
    # the activity tool was stored as a part of the key in queued_activity and
    # in flushed_activity, but this is not nice because in that case we must
    # use hash on it, and when there is no uid on activity tool, it is
    # impossible to generate a new uid because acquisition is not available
    # in the dictionary.
    assert activity_tool is not None
    self._activity_tool = activity_tool

    # Referring to a persistent object is dangerous when finishing a transaction,
    # so store only the required information.
    self._activity_tool_path = activity_tool.getPhysicalPath()

    try:
      buffer_dict_lock.acquire()
      if self._activity_tool_path not in buffer_dict:
        buffer_dict[self._activity_tool_path] = threading.local()
    finally:
      buffer_dict_lock.release()

    # Create attributes only if they are not present.
    buffer = self._getBuffer()
    if not hasattr(buffer, 'queued_activity'):
      buffer.queued_activity = []
      buffer.flushed_activity = []
      buffer.message_list_dict = {}
      buffer.uid_set_dict = {}

  def _getBuffer(self):
    return buffer_dict[self._activity_tool_path]

  def _clearBuffer(self):
    buffer = self._getBuffer()
    del buffer.queued_activity[:]
    del buffer.flushed_activity[:]
    buffer.message_list_dict.clear()
    buffer.uid_set_dict.clear()

  def getMessageList(self, activity):
    buffer = self._getBuffer()
    return buffer.message_list_dict.setdefault(activity, []) 

  def getUidSet(self, activity):
    buffer = self._getBuffer()
    return buffer.uid_set_dict.setdefault(activity, set())

  # Keeps a list of messages to add and remove
  # at end of transaction
  def _begin(self, *ignored):
    LOG('ActivityBuffer', 0, '_begin %r' % (self,))
    from ActivityTool import activity_list
    self.requires_prepare = 1
    try:

      # Reset registration for each transaction.
      for activity in activity_list:
        activity.registerActivityBuffer(self)

      # In Zope 2.8 (ZODB 3.4), use beforeCommitHook instead of
      # patching Trasaction.
      transaction = get_transaction()
      try:
        transaction.beforeCommitHook(self.tpc_prepare, transaction)
      except AttributeError:
        pass
    except:
      LOG('ActivityBuffer', ERROR, "exception during _begin",
          error=sys.exc_info())
      raise

  def _finish(self, *ignored):
    LOG('ActivityBuffer', 0, '_finish %r' % (self,))
    try:
      try:
        # Try to push / delete all messages
        buffer = self._getBuffer()
        for (activity, message) in buffer.flushed_activity:
          activity.finishDeleteMessage(self._activity_tool_path, message)
        for (activity, message) in buffer.queued_activity:
          activity.finishQueueMessage(self._activity_tool_path, message)
      except:
        LOG('ActivityBuffer', ERROR, "exception during _finish",
            error=sys.exc_info())
        raise
    finally:
      self._clearBuffer()

  def _abort(self, *ignored):
    self._clearBuffer()

  def tpc_prepare(self, transaction, sub=None):
    # Do nothing if it is a subtransaction
    if sub is not None:
      return

    if not self.requires_prepare:
      return

    self.requires_prepare = 0
    try:
      # Try to push / delete all messages
      buffer = self._getBuffer()
      for (activity, message) in buffer.flushed_activity:
        activity.prepareDeleteMessage(self._activity_tool, message)
      activity_dict = {}
      for (activity, message) in buffer.queued_activity:
        activity_dict.setdefault(activity, []).append(message)
      for activity, message_list in activity_dict.iteritems():
        if hasattr(activity, 'prepareQueueMessageList'):
          activity.prepareQueueMessageList(self._activity_tool, message_list)
        else:
          for message in message_list:
            activity.prepareQueueMessage(self._activity_tool, message)
    except:
      LOG('ActivityBuffer', ERROR, "exception during tpc_prepare",
          error=sys.exc_info())
      raise

  def deferredQueueMessage(self, activity_tool, activity, message):
    self._register()
    # Activity is called to prevent queuing some messages (useful for example
    # to prevent reindexing objects multiple times)
    if not activity.isMessageRegistered(self, activity_tool, message):
      buffer = self._getBuffer()
      buffer.queued_activity.append((activity, message))
      # We register queued messages so that we can
      # unregister them
      activity.registerMessage(self, activity_tool, message)

  def deferredDeleteMessage(self, activity_tool, activity, message):
    self._register()
    buffer = self._getBuffer()
    buffer.flushed_activity.append((activity, message))
