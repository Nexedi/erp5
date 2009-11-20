##############################################################################
#
# Copyright (c) 2002-2006 Nexedi SARL and Contributors. All Rights Reserved.
# Copyright (c) 2007-2009 Nexedi SA and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
#                    MURAOKA Yusuke <yusuke@nexedi.com>
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

from Query import Query
from Products.ZSQLCatalog.SQLExpression import SQLExpression
from SQLQuery import SQLQuery
from Products.ZSQLCatalog.interfaces.query import IQuery
from zope.interface.verify import verifyClass
from Products.ZSQLCatalog.SQLCatalog import profiler_decorator

class SubCatalogQuery(Query):
  """
    A Query do out child query of the Query to sub query and
    relate to that in SQL.
  """

  method_id = 'z_SubCatalogQuery'

  @profiler_decorator
  def __init__(self, query):
    self.query = query

  @profiler_decorator
  def _asSearchTextExpression(self, sql_catalog, column=None):
    if self.query:
      return self.query._asSearchTextExpression(sql_catalog, column=column)
    else:
      return (False, '')

  @profiler_decorator
  def asSQLExpression(self, sql_catalog, column_map, only_group_columns):
    sql_expression = self.query.asSQLExpression(sql_catalog,
                                                column_map,
                                                only_group_columns)
    method = getattr(sql_catalog, self.method_id, None)
    # XXX: this if clause is exist for backward compatibility of testSQLCatalog.
    if method:
      where_expression = method(src__=1, **sql_expression.asSQLExpressionDict())
    else:
      where_expression = None
    return SQLExpression(self,
                         where_expression=where_expression,
                         sql_expression_list=(sql_expression,))

  @profiler_decorator
  def registerColumnMap(self, sql_catalog, column_map):
    if self.query:
      self.query.registerColumnMap(sql_catalog, column_map)

  @profiler_decorator
  def setTableAliasList(self, table_alias_list):
    if self.query:
      self.query.setTableAliasList(table_alias_list)

  def __repr__(self):
    return '<%s with %r>' % (self.__class__.__name__, self.query)
