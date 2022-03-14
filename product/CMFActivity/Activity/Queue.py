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

import sys
from hashlib import sha1
from DateTime import DateTime
from zLOG import LOG, WARNING, ERROR
from ZODB.POSException import ConflictError
from io import BytesIO as StringIO

# Time global parameters
MAX_PROCESSING_TIME = 900 # in seconds
VALIDATION_ERROR_DELAY = 15 # in seconds

class Queue(object):
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

  def initialize(self, activity_tool, clear):
    pass

  def deleteMessage(self, activity_tool, m):
    if not getattr(m, 'is_deleted', 0):
      # We try not to delete twice
      # However this can not be garanteed in the case of messages loaded from SQL
      activity_tool.deferredDeleteMessage(self, m)
    m.is_deleted = 1

  def dequeueMessage(self, activity_tool, processing_node,
                     node_family_id_list):
    raise NotImplementedError

  def distribute(self, activity_tool, node_count):
    raise NotImplementedError

  def flush(self, activity_tool, object, **kw):
    pass

  def getMessageList(self, activity_tool, processing_node=None,**kw):
    return []

  # Transaction Management
  def prepareQueueMessageList(self, activity_tool, message_list):
    # Called to prepare transaction commit for queued messages
    raise NotImplementedError

  # Registration Management
  def isMessageRegistered(self, activity_buffer, activity_tool, m):
    # BBB: deprecated
    message_list = activity_buffer.getMessageList(self)
    return m in message_list

  def registerMessage(self, activity_buffer, activity_tool, m):
    activity_buffer.getMessageList(self).append(m)
    m.is_registered = True

  def unregisterMessage(self, activity_buffer, activity_tool, m):
    m.is_registered = False

  def getRegisteredMessageList(self, activity_buffer, activity_tool):
    message_list = activity_buffer.getMessageList(self)
    return [m for m in message_list if m.is_registered]

  # Required for tests (time shift)
  def timeShift(self, activity_tool, delay):
    """
      delay is provided in fractions of day
    """
    pass

  def getPriority(self, activity_tool, processing_node, node_set):
    """
      Get priority from this queue.
      Lower number means higher priority value.
      Legal value range is [-385, 382].
      Values out of this range might work, but are non-standard.
    """
    return 384,
