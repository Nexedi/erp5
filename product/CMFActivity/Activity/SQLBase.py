##############################################################################
#
# Copyright (c) 2007 Nexedi SA and Contributors. All Rights Reserved.
#                    Vincent Pelletier <vincent@nexedi.com>
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

from zLOG import LOG, INFO, WARNING
from ZODB.POSException import ConflictError

class SQLBase:
  """
    Define a set of common methods for SQL-based storage of activities.
  """
 
  def getNow(self, context):
    """
      Return the current value for SQL server's NOW().
      Note that this value is not cached, and is not transactionnal on MySQL
      side.
    """
    result = context.SQLBase_getNow()
    assert len(result) == 1
    assert len(result[0]) == 1
    return result[0][0]

  def getMessageList(self, activity_tool, processing_node=None,
                     include_processing=0, **kw):
    # YO: reading all lines might cause a deadlock
    readMessageList = getattr(activity_tool,
                              self.__class__.__name__ + '_readMessageList',
                              None)
    if readMessageList is None:
      return []
    return [self.loadMessage(line.message,
                             uid=line.uid,
                             processing_node=line.processing_node,
                             priority=line.priority,
                             processing=line.processing)
            for line in readMessageList(path=None,
                                        method_id=None,
                                        processing_node=processing_node,
                                        to_date=None,
                                        include_processing=include_processing)]

  def _getPriority(self, activity_tool, method, default):
    result = method()
    assert len(result) == 1
    priority = result[0]['priority']
    if priority is None:
      priority = default
    return priority

  def _retryOnLockError(self, method, args=(), kw=None):
    if kw is None:
      kw = {}
    while True:
      try:
        result = method(*args, **kw)
      except ConflictError:
        # Note that this code assumes that a database adapter translates
        # a lock error into a conflict error.
        LOG('SQLBase', INFO, 'Got a lock error, retrying...')
      else:
        break
    return result

  def _validate_after_method_id(self, activity_tool, message, value):
    return self._validate(activity_tool, method_id=value)

  def _validate_after_path(self, activity_tool, message, value):
    return self._validate(activity_tool, path=value)

  def _validate_after_message_uid(self, activity_tool, message, value):
    return self._validate(activity_tool, message_uid=value)

  def _validate_after_path_and_method_id(self, activity_tool, message, value):
    if not (isinstance(value, (tuple, list)) and len(value) == 2):
      LOG('CMFActivity', WARNING,
          'unable to recognize value for after_path_and_method_id: %r' % (value,))
      return []
    return self._validate(activity_tool, path=value[0], method_id=value[1])

  def _validate_after_tag(self, activity_tool, message, value):
    return self._validate(activity_tool, tag=value)

  def _validate_after_tag_and_method_id(self, activity_tool, message, value):
    # Count number of occurances of tag and method_id
    if not (isinstance(value, (tuple, list)) and len(value) == 2):
      LOG('CMFActivity', WARNING,
          'unable to recognize value for after_tag_and_method_id: %r' % (value,))
      return []
    return self._validate(activity_tool, tag=value[0], method_id=value[1])

  def _validate_serialization_tag(self, activity_tool, message, value):
    return self._validate(activity_tool, serialization_tag=value)
