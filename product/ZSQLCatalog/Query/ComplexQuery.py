##############################################################################
#
# Copyright (c) 2005 Nexedi SARL and Contributors. All Rights Reserved.
#                     Ivan Tyagov <ivan@nexedi.com>
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

from Products.PythonScripts.Utility import allow_class
from Query import QueryMixin

class ComplexQuery(QueryMixin):
  """
  Used in order to concatenate many queries
  """
  
  def __init__(self, *args, **kw):
    self.query_list = args
    self.operator = kw.pop('operator', 'AND')
    # XXX: What is that used for ?! It's utterly dangerous.
    #self.__dict__.update(kw)

  def getQueryList(self):
    return self.query_list

  def getRelatedTableMapDict(self):
    result = {}
    for query in self.getQueryList():
      if not(isinstance(query, basestring)):
        result.update(query.getRelatedTableMapDict())
    return result

  def asSQLExpression(self, key_alias_dict=None,
                            ignore_empty_string=1,
                            keyword_search_keys=None,
                            datetime_search_keys=None,
                            full_text_search_keys=None,
                            stat__=0):
    """
    Build the sql string
    """
    sql_expression_list = []
    select_expression_list = []
    for query in self.getQueryList():
      if isinstance(query, basestring):
        sql_expression_list.append(query)
      else:
        query_result = query.asSQLExpression(key_alias_dict=key_alias_dict,
                               ignore_empty_string=ignore_empty_string,
                               keyword_search_keys=keyword_search_keys,
                               datetime_search_keys=datetime_search_keys,
                               full_text_search_keys=full_text_search_keys,
                               stat__=stat__)
        sql_expression_list.append(query_result['where_expression'])
        select_expression_list.extend(query_result['select_expression_list'])
    operator = self.getOperator()
    result = {'where_expression':('(%s)' %  \
                         (' %s ' % operator).join(['(%s)' % x for x in sql_expression_list])),
              'select_expression_list':select_expression_list}
    return result

  def getSQLKeyList(self):
    """
    Returns the list of keys used by this
    instance
    """
    key_list=[]
    for query in self.getQueryList():
      if not(isinstance(query, basestring)):
        key_list.extend(query.getSQLKeyList())
    return key_list

allow_class(ComplexQuery)
