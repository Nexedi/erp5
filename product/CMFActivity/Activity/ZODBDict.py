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

from BTrees.OOBTree import OOBTree
from BTrees.OIBTree import OITreeSet
from Products.CMFActivity.ActivityTool import registerActivity
from RAMDict import RAMDict

from zLOG import LOG

class ZODBDict(RAMDict):
  """
    A simple OOBTree based queue. It should be compatible with transactions
    and provide sequentiality. Should not create conflict
    because use of OOBTree.
  """

  def initialize(self, activity_tool):
    # This is the only moment when
    # we can set some global variables related
    # to the ZODB context
    if not self.is_initialized:
      RAMDict.initialize(self, activity_tool)
      if getattr(activity_tool.activity_data, 'message_dict', None) is None:
        activity_tool.activity_data.message_dict = OOBTree()
      if getattr(activity_tool.activity_data, 'activable_set', None) is None:
        activity_tool.activity_data.activable_set = OITreeSet()

  def queueMessage(self, activity_tool, m):
    message_dict = activity_tool.activity_data.message_dict
    activable_set = activity_tool.activity_data.activable_set
    if not message_dict.has_key(m.object_path):
      message_dict[m.object_path] = OOBTree()
    #message_dict[m.object_path][m.method_id] = self.dumpMessage(m)
    message_dict[m.object_path][m.method_id] = m
    activable_set.insert(m.object_path) # Add to set

  def dequeueMessage(self, activity_tool, processing_node):
    message_dict = activity_tool.activity_data.message_dict
    activable_set = activity_tool.activity_data.activable_set
    # We never erase BTree items a this point
    # with the hope it reduces the risk of conflict
    if len(activable_set) > 0:
      object_path = activable_set[0]
      object_dict = message_dict[object_path]
      for key, m in object_dict.items():
        #if m.validate(self, activity_tool):
        if 1:
          #activity_tool.invoke(self.loadMessage(m))
          activity_tool.invoke(m)
          del object_dict[key]
          return 0
      # We only reach this point if there are no more messages
      activable_set.remove(object_path)
    return 1

  def hasActivity(self, activity_tool, object, method_id=None, **kw):
    message_dict = activity_tool.activity_data.message_dict
    activable_set = activity_tool.activity_data.activable_set
    my_object_path = object.getPhysicalPath()
    if my_object_path in activable_set:
      object_dict = message_dict[object_path]
      if len(object_dict) > 0:
        return 1
    return 0

  def flush(self, activity_tool, object_path, invoke=0, method_id=None, **kw):
    """
      object_path is a tuple
    """
    message_dict = activity_tool.activity_data.message_dict
    activable_set = activity_tool.activity_data.activable_set
    #LOG('CMFActivity ZODBDict: ', 0, str(object_path))
    if object_path in activable_set:
      object_dict = message_dict[object_path]
      activable_set.remove(object_path)
      for key, m in object_dict.items():
        #LOG('CMFActivity ZODBDict: ', 0, 'flushing object %s' % '/'.join(m.object_path))
        #if invoke: activity_tool.invoke(self.loadMessage(m))
        if invoke: activity_tool.invoke(m)
        del object_dict[key]

  def getMessageList(self, activity_tool, processing_node=None):
    message_dict = activity_tool.activity_data.message_dict
    activable_set = activity_tool.activity_data.activable_set
    result = []
    for object_path in activable_set:
      object_dict = message_dict[object_path]
      #result = result + list(map(lambda m: self.loadMessage(m),object_dict.values()))
      result = result + list(object_dict.values())
    return result

registerActivity(ZODBDict)
