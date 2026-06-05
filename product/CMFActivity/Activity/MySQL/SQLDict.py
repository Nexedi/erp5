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
from ..Common.SQLDict import SQLDict as _SQLDict
from .SQLBase import SQLBase

class SQLDict(_SQLDict, SQLBase):

  def _sqlMethodIdCondition(self, db, method_id, group_method_id):
    quote = db.string_literal
    return b" AND method_id = %s AND group_method_id = %s" % (
      quote(method_id), quote(group_method_id),
    )

  def _selectParentMessage(self, db, processing_node, path_list,
                           method_id, group_method_id):
    quote = db.string_literal
    sql_method_id = self._sqlMethodIdCondition(db, method_id, group_method_id)
    sql = b"SELECT * FROM message" \
      b" WHERE processing_node IN (0, %d) AND path IN (%s)%s" \
      b" ORDER BY path LIMIT 1 FOR UPDATE%s" % (
        processing_node,
        b','.join(map(quote, path_list)),
        sql_method_id,
        b' SKIP LOCKED' if db.has_skip_locked else b'',
      )
    return Results(db.query(sql, 0))

  def _selectSimilarChildren(self, db, path, method_id, group_method_id):
    quote = db.string_literal
    sql_method_id = self._sqlMethodIdCondition(db, method_id, group_method_id)
    sql = b"SELECT uid FROM message" \
      b" WHERE processing_node = 0 AND (path = %s OR path LIKE %s)%s" \
      b" FOR UPDATE%s" % (
        quote(path), quote(path.replace('_', r'\_') + '/%'),
        sql_method_id,
        b' SKIP LOCKED' if db.has_skip_locked else b'',
      )
    return db.query(sql, 0)[1]

  def _selectDuplicates(self, db, path, method_id, group_method_id):
    quote = db.string_literal
    sql_method_id = self._sqlMethodIdCondition(db, method_id, group_method_id)
    sql = b"SELECT uid FROM message" \
      b" WHERE processing_node = 0 AND path = %s%s FOR UPDATE%s" % (
        quote(path),
        sql_method_id,
        b' SKIP LOCKED' if db.has_skip_locked else b'',
      )
    return db.query(sql, 0)[1]
