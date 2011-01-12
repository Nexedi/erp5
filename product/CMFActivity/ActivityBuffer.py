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

import transaction

class ActivityBuffer(TM):

  _p_oid=_p_changed=_registered=None

  def __init__(self):
    self.queued_activity = []
    self.flushed_activity = []
    self.message_list_dict = {}
    self.uid_set_dict = {}

  def _clear(self):
    del self.queued_activity[:]
    del self.flushed_activity[:]
    self.message_list_dict.clear()
    self.uid_set_dict.clear()
    self.activity_tool = None

  def getMessageList(self, activity):
    return self.message_list_dict.setdefault(activity, [])

  def getUidSet(self, activity):
    return self.uid_set_dict.setdefault(activity, set())

  def _register(self, activity_tool):
    if not self._registered:
      self.activity_tool = activity_tool
      self._activity_tool_path = activity_tool.getPhysicalPath()
      TM._register(self)
      self._prepare_args = 0, 0
    if self._prepare_args:
      transaction.get().addBeforeCommitHook(self._prepare, self._prepare_args)
      self._prepare_args = None

  # Keeps a list of messages to add and remove
  # at end of transaction
  def _begin(self):
    # LOG('ActivityBuffer', 0, '_begin %r' % (self,))
    from ActivityTool import activity_dict
    try:
      # Reset registration for each transaction.
      for activity in activity_dict.itervalues():
        activity.registerActivityBuffer(self)
    except:
      LOG('ActivityBuffer', ERROR, "exception during _begin",
          error=sys.exc_info())
      raise

  def _finish(self):
    # LOG('ActivityBuffer', 0, '_finish %r' % (self,))
    try:
      try:
        # Try to push / delete all messages
        for activity, message in self.flushed_activity:
          activity.finishDeleteMessage(self._activity_tool_path, message)
        for activity, message in self.queued_activity:
          activity.finishQueueMessage(self._activity_tool_path, message)
      except:
        LOG('ActivityBuffer', ERROR, "exception during _finish",
            error=sys.exc_info())
        raise
    finally:
      self._clear()

  _abort = _clear

  def _prepare(self, flushed, queued):
    try:
      activity_tool = self.activity_tool
      # Try to push / delete all messages
      for activity, message in self.flushed_activity[flushed:]:
        activity.prepareDeleteMessage(activity_tool, message)
      activity_dict = {}
      for activity, message in self.queued_activity[queued:]:
        activity_dict.setdefault(activity, []).append(message)
      for activity, message_list in activity_dict.iteritems():
        activity.prepareQueueMessageList(activity_tool, message_list)
      self._prepare_args = len(self.flushed_activity), len(self.queued_activity)
    except:
      LOG('ActivityBuffer', ERROR, "exception during _prepare",
          error=sys.exc_info())
      raise

  def deferredQueueMessage(self, activity_tool, activity, message):
    self._register(activity_tool)
    # Activity is called to prevent queuing some messages (useful for example
    # to prevent reindexing objects multiple times)
    if not activity.isMessageRegistered(self, activity_tool, message):
      self.queued_activity.append((activity, message))
      # We register queued messages so that we can
      # unregister them
      activity.registerMessage(self, activity_tool, message)

  def deferredDeleteMessage(self, activity_tool, activity, message):
    self._register(activity_tool)
    self.flushed_activity.append((activity, message))

  def sortKey(self, *ignored):
    """Activities must be finished before databases commit transactions."""
    return -1
