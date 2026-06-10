from __future__ import absolute_import
##############################################################################
#
# Copyright (c) 2002,2007 Nexedi SA and Contributors. All Rights Reserved.
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

from zLOG import TRACE, WARNING
from Products.CMFActivity.ActivityTool import Message
from .SQLDict import SQLDict


class SQLJoblib(SQLDict):
  """
    An extention of SQLDict, It is non transatactional and follow always-excute paradigm.
    It uses a dictionary to store results and with hash of arguments as keys
  """
  sql_table = 'message_job'
  uid_group = 'portal_activity_job'

  def generateMessageUID(self, m):
    return (tuple(m.object_path), m.method_id, m.activity_kw.get('signature'),
                  m.activity_kw.get('tag'), m.activity_kw.get('group_id'))

  def getProcessableMessageLoader(self, db, processing_node):
    path_and_method_id_dict = {}
    def load(line):
      # getProcessableMessageList already fetch messages with the same
      # group_method_id, so what remains to be filtered on are path, method_id
      # and signature
      path = line.path
      method_id = line.method_id
      key = path, method_id
      uid = line.uid
      original_uid = path_and_method_id_dict.get(key)
      if original_uid is None:
        m = Message.load(line.message, uid=uid, line=line)
        try:
          # Select duplicates.
          result = self._selectDuplicates(
            db, path, line.signature, method_id, line.group_method_id)
          uid_list = [x for x, in result]
          if uid_list:
            self.assignMessageList(db, processing_node, uid_list)
          else:
            db.query(b"COMMIT") # XXX: useful ?
        except:
          self._log(WARNING, 'Failed to reserve duplicates')
          db.query(b"ROLLBACK")
          raise
        if uid_list:
          self._log(TRACE, 'Reserved duplicate messages: %r' % uid_list)
        path_and_method_id_dict[key] = uid
        return m, uid, uid_list
      # We know that original_uid != uid because caller skips lines we returned
      # earlier.
      return None, original_uid, [uid]
    return load

  def getPriority(self, activity_tool, processing_node, node_set):
    return SQLDict.getPriority(self, activity_tool, processing_node)

  def getReservedMessageList(self, db, date, processing_node,
                             limit=None, group_method_id=None, node_set=None):
    return SQLDict.getReservedMessageList(self, db,
      date, processing_node, limit, group_method_id)
