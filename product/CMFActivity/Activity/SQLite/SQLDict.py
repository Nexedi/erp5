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

from Shared.DC.ZRDB.Results import Results
from ..SQLDict import SQLDict as _SQLDict
from .SQLBase import SQLBase

class SQLDict(_SQLDict, SQLBase):

  def _sqlMethodIdCondition(self, db, method_id, group_method_id):
    return b" AND method_id = ? AND group_method_id = ?", (
      method_id, group_method_id,
    )

  def _selectParentMessage(self, db, processing_node, path_list,
                           method_id, group_method_id):
    sql_method_id, sub_args = self._sqlMethodIdCondition(
      db, method_id, group_method_id)
    placeholders = b",".join([b"?"] * len(path_list))
    sql = (b"SELECT * FROM message"
      b" WHERE processing_node IN (0, ?) AND path IN (" + placeholders + b")"
      + sql_method_id + b" ORDER BY path LIMIT 1")
    args = (processing_node,) + tuple(path_list) + sub_args
    return Results(db.query(sql, 0, args=args))

  def _selectSimilarChildren(self, db, path, method_id, group_method_id):
    sql_method_id, sub_args = self._sqlMethodIdCondition(
      db, method_id, group_method_id)
    sql = (b"SELECT uid FROM message"
      b" WHERE processing_node = 0 AND (path = ? OR path LIKE ?)"
      + sql_method_id)
    args = (path, path + '/%') + sub_args
    return db.query(sql, 0, args=args)[1]

  def _selectDuplicates(self, db, path, method_id, group_method_id):
    sql_method_id, sub_args = self._sqlMethodIdCondition(
      db, method_id, group_method_id)
    sql = (b"SELECT uid FROM message"
      b" WHERE processing_node = 0 AND path = ?" + sql_method_id)
    args = (path,) + sub_args
    return db.query(sql, 0, args=args)[1]
