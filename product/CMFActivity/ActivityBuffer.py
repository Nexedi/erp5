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
from zLOG import LOG, ERROR
from collections import defaultdict

import transaction

class ActivityBuffer(TM):
  activity_tool = None

  def __init__(self):
    self.message_list_dict = defaultdict(list)
    self.uid_set_dict = defaultdict(set)

  def _clear(self):
    self.message_list_dict.clear()
    self.uid_set_dict.clear()
    self.activity_tool = None

  def getMessageList(self, activity):
    return self.message_list_dict[activity]

  def getUidSet(self, activity):
    return self.uid_set_dict[activity]

  def _register(self, activity_tool):
    TM._register(self)
    if self.activity_tool is None:
      self.activity_tool = activity_tool
      transaction.get().addBeforeCommitHook(self._prepare)

  _abort = _finish = _clear

  def _prepare(self):
    try:
      activity_tool = self.activity_tool
      # Try to push all messages
      for activity, message_list in six.iteritems(self.message_list_dict):
        activity.prepareQueueMessageList(activity_tool, message_list)
      self.message_list_dict.clear()
      self.activity_tool = None
    except:
      LOG('ActivityBuffer', ERROR, "exception during _prepare",
          error=True)
      raise

  def deferredQueueMessage(self, activity_tool, activity, message):
    self._register(activity_tool)
    assert not message.is_registered, message
    activity.registerMessage(self, activity_tool, message)

  def sortKey(self, *ignored):
    """Activities must be finished before databases commit transactions."""
    return '-1'
