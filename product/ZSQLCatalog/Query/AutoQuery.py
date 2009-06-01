##############################################################################
#
# Copyright (c) 2002-2006 Nexedi SARL and Contributors. All Rights Reserved.
# Copyright (c) 2007-2009 Nexedi SA and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
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

from Query import Query
from zLOG import LOG
from Products.ZSQLCatalog.interfaces.query import IQuery
from Interface.Verify import verifyClass
from Products.ZSQLCatalog.SQLCatalog import profiler_decorator

class AutoQuery(Query):
  """
    An AutoQuery is a compatibility layer for former Query class.
    It passes parameters given at instantiation time to SQLCatalog's
    buildQuery or buildSingleQuery, and wraps resulting Query instance (proxy
    behaviour).

    This is only here for backward compatibility, and use is strongly
    discouraged. Use SQLCatalog API instead.
  """
  wrapped_query = None

  @profiler_decorator
  def __init__(self, *args, **kw):
    """
      Note: "operator" might contain a logical or a comparison operator.
    """
    if len(args):
      LOG('AutoQuery', 100, 'Got extra positional parameters (will be ignored): %r' % (args, ))
    self.table_alias_list = kw.pop('table_alias_list', None)
    self.kw = kw
    operator = kw.pop('operator', None)
    if isinstance(operator, basestring):
      operator = operator.lower()
    self.operator = operator
    self.ignore_empty_string = kw.pop('ignore_empty_string', True)
    if 'key' in kw and len(kw) > 2:
      raise ValueError, '"key" parameter cannot be used when more than one column is given. key=%r' % (self.search_key, )
    self.search_key = kw.pop('key', None)

  @profiler_decorator
  def _createWrappedQuery(self, sql_catalog):
    """
      Create wrapped query. This requires being able to reach catalog, since
      we use it as a query producer.
    """
    kw = self.kw
    operator = self.operator
    if 'range' in kw:
      # If we received a range parameter we are building a single query.
      # Recreate value as a dict and pass it to buildSingleQuery.
      range = kw.pop('range')
      assert len(kw) == 1, repr(kw)
      key, value = kw.items()[0]
      query = sql_catalog.buildSingleQuery(key, {'query': value,
                                                 'range': range})
    elif operator == 'in':
      # 'in' is a *comparison* operator, not a logical operator.
      # Transform kw into the proper form.
      assert len(kw) == 1, repr(kw)
      key, value = kw.items()[0]
      query = sql_catalog.buildSingleQuery(key, {'query': value,
                                                 'operator': operator})
    elif len(kw) == 1 and isinstance(kw.values()[0], (tuple, list)) and \
       operator in ('and', 'or'):
      # If there is only one parameter, and operator was given and is a
      # known logical operator, then operator will apply to it.
      # For example (from testDomainTool):
      #  kw = {'portal_type': ['!=a', '!=b'], 'operator': 'AND'}
      #  In such case, expected result is
      #  "portal_type!='a' AND portal_type!='b'"
      key, value = kw.items()[0]
      query = sql_catalog.buildSingleQuery(key, value, logical_operator=operator)
    else:
      # Otherwise, the operator will apply to the relationship between
      # parameters.
      if operator is None:
        operator = 'and'
      if self.search_key is not None:
        key, value = kw.items()[0]
        kw = {key: {'query': value, 'key': self.search_key}}
      query = sql_catalog.buildQuery(kw, operator=operator, ignore_empty_string=self.ignore_empty_string)
    if self.table_alias_list is not None:
      query.setTableAliasList(self.table_alias_list)
    self.wrapped_query = query

  @profiler_decorator
  def asSearchTextExpression(self, sql_catalog, column=None):
    if self.wrapped_query is None:
      self._createWrappedQuery(sql_catalog)
    return self.wrapped_query.asSearchTextExpression(sql_catalog, column=column)

  @profiler_decorator
  def asSQLExpression(self, sql_catalog, column_map, only_group_columns):
    if self.wrapped_query is None:
      self._createWrappedQuery(sql_catalog)
    return self.wrapped_query.asSQLExpression(sql_catalog, column_map, only_group_columns=only_group_columns)

  @profiler_decorator
  def registerColumnMap(self, sql_catalog, column_map):
    if self.wrapped_query is None:
      self._createWrappedQuery(sql_catalog)
    return self.wrapped_query.registerColumnMap(sql_catalog, column_map)

  def __repr__(self):
    if self.wrapped_query is None:
      result = '<%s(**%r) at %s>' % (self.__class__.__name__, self.kw, id(self))
    else:
      result = '<%s %r>' % (self.__class__.__name__, self.wrapped_query)
    return result

verifyClass(IQuery, AutoQuery)

