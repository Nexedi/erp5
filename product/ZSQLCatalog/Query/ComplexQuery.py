from __future__ import absolute_import
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

from .Query import Query
from Products.ZSQLCatalog.SQLExpression import SQLExpression
from Products.ZSQLCatalog.interfaces.query import IQuery
from zope.interface.verify import verifyClass
from Products.ZSQLCatalog.Query.AutoQuery import AutoQuery
from Products.ZSQLCatalog.Query.RelatedQuery import RelatedQuery

logical_operator_search_text_dict = {
  'and': 'AND',
  'or': 'OR',
}

class ComplexQuery(Query):
  """
    A ComplexQuery represents logical operations between Query instances.
  """
  def __init__(self, *args, **kw):
    """
      *args (tuple of Query or of list of Query)
        list-type entry will extend subquery list, other entries will be
        appended.
      logical_operator ('and', 'or', 'not')
        Logical operator.
        Default: 'and'
    """
    self.logical_operator = kw.pop('logical_operator', 'and').lower()
    assert self.logical_operator in ('and', 'or', 'not'), self.logical_operator
    if kw:
      raise TypeError('Unknown named arguments: %r' % (list(kw.keys()), ))
    query_list = []
    append = query_list.append
    extend = query_list.extend
    # Flaten the first level of list-type arguments
    for arg in args:
      if isinstance(arg, (list, tuple)):
        extend(arg)
      else:
        append(arg)
    for query in query_list:
      if not isinstance(query, Query):
        raise TypeError('Got a non-query argument: %r' % (query, ))
    self.query_list = query_list
    self.checkQueryTree()

  def _findRelatedQuery(self, query):
    """
      XXX This method is used for checkQueryTree checking.
      Find RelatedQuery or a query which have RelatedQuery
      from container queries recursively
    """
    result = None
    if isinstance(query, AutoQuery):
      result = self._findRelatedQuery(query.wrapped_query)
    elif isinstance(query, ComplexQuery):
      if getattr(query, '_has_related_query', False):
        result = query
      else:
        for sub_query in query.query_list:
          result = self._findRelatedQuery(sub_query)
          if result:
            break
    elif isinstance(query, RelatedQuery):
      result = query
    return result

  def checkQueryTree(self):
    """
      XXX
      The root of this query tree will not return semantic valid SQLExpression
      when the self has 'or' operator and a RelatedQuery in the query tree of self.
      The semantic valid means that, for example, there is a query tree which has
      three queries:
        - one is intended for searching document with the title 'bra%'
        - one is intended for searching document which is related to a category
        - a ComplexQuery with 'or' operator which has above queries as children
      in this case, the root of the query tree should return an expression
      "(document.tile like 'bra%') or (document related to the category and
      the category entry must be in catalog)". This is semantic valid.
      However at current implementation, return the expression
      "(document.title like 'bra%' or document related to the category) and (the
      category entry must be in catalog)". The outside relation between category
      and catalog also affects the document.title condition. It is a limitation for
      performance. We don't hope to return affected result. So raise the Exception.
    """
    for query in self.query_list:
      result = self._findRelatedQuery(query)
      if result:
        self._has_related_query = True
        break
    else:
      self._has_related_query = False
    if (self._has_related_query and
        self.logical_operator == 'or'):
      raise NotImplementedError

  def _asSearchTextExpression(self, sql_catalog, column=None):
    if column in (None, ''):
      query_column = column
    else:
      query_column = ''
    search_text_list = []
    composition_list = []
    for query in self.query_list:
      is_composed, search_text = query._asSearchTextExpression(sql_catalog, column=query_column)
      if search_text is not None:
        search_text_list.append(search_text)
        composition_list.append(is_composed)
    self_is_composed = False
    if len(search_text_list) == 0:
      result = ''
    else:
      if self.logical_operator in logical_operator_search_text_dict:
        if len(search_text_list) == 1:
          result = search_text_list[0]
          self_is_composed = composition_list[0]
        else:
          self_is_composed = True
          logical_operator = ' %s ' % (logical_operator_search_text_dict[self.logical_operator], )
          parenthesed_search_text_list = []
          append = parenthesed_search_text_list.append
          for is_composed, search_text in zip(composition_list, search_text_list):
            if is_composed:
              append('(%s)' % (search_text, ))
            else:
              append(search_text)
          result = logical_operator.join(parenthesed_search_text_list)
      elif self.logical_operator == 'not':
        assert len(search_text_list) == 1
        result = 'NOT %s' % (search_text_list[0], )
      else:
        raise ValueError('Unknown operator %r' % (self.logical_operator, ))
      if column not in (None, ''):
        if self_is_composed:
          result = '(%s)' % (result, )
          self_is_composed = False
        result = '%s:%s' % (column, result)
    return self_is_composed, result

  def asSQLExpression(self, sql_catalog, column_map, only_group_columns):
    sql_expression_list = [x.asSQLExpression(sql_catalog, column_map, only_group_columns)
                           for x in self.query_list]
    if len(sql_expression_list) == 0:
      sql_expression_list = [SQLExpression(self, where_expression='1')]
    return SQLExpression(self,
      sql_expression_list=sql_expression_list,
      where_expression_operator=self.logical_operator,
    )

  def registerColumnMap(self, sql_catalog, column_map):
    for query in self.query_list:
      query.registerColumnMap(sql_catalog, column_map)

  def __repr__(self):
    return '<%s of %r.join(%r)>' % (self.__class__.__name__, self.logical_operator, self.query_list)

  def setTableAliasList(self, table_alias_list):
    """
      This function is here for backward compatibility.
      This can only be used when there is one and only one subquery which
      defines a setTableAliasList method.

      See RelatedQuery.
    """
    assert len(self.query_list) == 1
    self.query_list[0].setTableAliasList(table_alias_list)

  def setGroup(self, group):
    for query in self.query_list:
      query.setGroup(group)

verifyClass(IQuery, ComplexQuery)

