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

from Products.CMFActivity.ActivityTool import registerActivity
from Queue import Queue
import pickle

from zLOG import LOG

class SQLQueue(Queue):
  """
    A simple RAM based queue
  """

  def initialize(self, activity_tool):
    # This is the only moment when
    # we can set some global variables related
    # to the ZODB context
    if not self.is_initialized:
      try:
        self.activity_tool = activity_tool
        self.sqlWriteMessage = activity_tool.SQLQueue_writeMessage
        self.sqlReadMessage = activity_tool.SQLQueue_readMessage
        self.sqlDelMessage = activity_tool.SQLQueue_delMessage
        self.sqlHasMessage = activity_tool.SQLQueue_hasMessage
        self.is_initialized = 1
      except:
        LOG('ERROR SQLQueue', 100, 'could not initialize SQL methods')

  def queueMessage(self, m):
    self.sqlWriteMessage(uid = m.object.uid , method_id = m.method_id, message = self.dumpMessage(m))

  def dequeueMessage(self, activity_tool):
    return 1 # sleep
    m = self.loadMessage(message)
    activity_tool.invoke(m)
    self.sqlDelMessage(uid = m.object.uid , method_id = m.method_id)

  def hasActivity(self, object):
    return self.sqlHasMessage(uid = object.uid).has_activity

registerActivity(SQLQueue)