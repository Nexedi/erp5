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
from DateTime import DateTime
from Query import QueryMixin
from pprint import pprint

# valid search modes for queries
FULL_TEXT_SEARCH_MODE = 'FullText'
EXACT_MATCH_SEARCH_MODE = 'ExactMatch'
KEYWORD_SEARCH_MODE = 'Keyword'
DATETIME_SEARCH_MODE = 'DateTime'

def isSimpleType(value):
  return isinstance(value, basestring) or \
         isinstance(value, int) or \
         isinstance(value, long) or \
         isinstance(value, float)

# XXX Bad name JPS - NotQuery or NegativeQuery is better NegationQuery
class NegatedQuery(QueryMixin):
  """
    Do a boolean negation of given query.
  """

  def __init__(self, query):
    self._query = query

  def asSQLExpression(self, *args, **kw):
    sql_expression_dict = self._query.asSQLExpression(*args, **kw)
    sql_expression_dict['where_expression'] = '(NOT (%s))' % \
      (sql_expression_dict['where_expression'], )
    return sql_expression_dict

  def getSQLKeyList(self, *args, **kw):
    return self._query.getSQLKeyList(*args, **kw)

  def getRelatedTableMapDict(self, *args, **kw):
    return self._query.getRelatedTableMapDict(*args, **kw)

allow_class(NegatedQuery)

class SimpleQuery(QueryMixin):
  """
  This allow to define constraints on a sql column

  format - type date : %d/%m/%Y
           type float : 1 234.12
  """
  
  def __init__(self, format=None, operator=None, range=None, key=None,
                     search_mode=None, table_alias_list=None, type=None, **kw):
    self.format = format
    if operator is None:
      operator = 'OR'
    self.operator = operator
    self.range = range
    self.search_mode = search_mode
    self.table_alias_list = table_alias_list
    key_list = kw.keys()
    if len(key_list) != 1:
      raise KeyError, 'Query must have only one key'
    self.key = key_list[0]
    self.value = kw[self.key]
    self.type = type
    self.search_key = key

  def getRelatedTableMapDict(self):
    result = {}
    table_alias_list = self.getTableAliasList()
    if table_alias_list is not None:
      result[self.getKey()] = table_alias_list
    return result  
    
  def getSQLKeyList(self):
    """
    Returns the list of keys used by this
    instance
    """
    return [self.getKey()]
    
  def asSearchTextExpression(self):
    # This will be the standard way to represent
    # complex values in listbox. Some fixed
    # point must be garanteed
    value = self.getValue()
    if isSimpleType(value) or isinstance(value, DateTime):
      return str(value)
    elif isinstance(value, (list, tuple)):
      value = map(lambda x:str(x), value)
      return (' %s ' % self.operator).join(value)
        
  def _getSearchKeyClassByType(self, type, search_key_class = None):
    """ Return search key class based on type of value. """
    name_search_key_map = {'keyword': KeyWordKey,
                           'default': DefaultKey,
                           'fulltext': FullTextKey,
                           'date': DateTimeKey,
                           'float': FloatKey,
                           'int': DefaultKey,}
    return name_search_key_map.get(type, search_key_class)
    
  def _getSearchKeyClassByValue(self, value, search_key_class = None):
    """ Return search key class based on type of value. """
    if isinstance(value, basestring):
      if value.find('%')!=-1:
        # it's likely a KeyWordKey
        search_key_class = KeyWordKey
      else:
        search_key_class = DefaultKey
    elif isinstance(value, DateTime):
      search_key_class = DateTimeKey      
    elif isinstance(value, (int, long,)):
      search_key_class = DefaultKey
    elif isinstance(value, float):
      search_key_class = FloatKey
    elif value is None:
      return RawKey
    return search_key_class

  def _asSQLExpression(self, search_key_class, key, value, format=None, mode=None, range_value=None, stat__=None):
    """ Generate SQL expressions based on respective search_key passed. """
    lexer = getSearchKeyInstance(search_key_class)
    where_expression, select_expression_list = \
             lexer.buildSQLExpression(key, value, format, mode, range_value, stat__)
    sql_expressions = {'where_expression': where_expression,
                       'select_expression_list': select_expression_list,}
    return sql_expressions
    
  def asSQLExpression(self, key_alias_dict=None, keyword_search_keys=None,
                      datetime_search_keys=None, full_text_search_keys=None,
                      ignore_empty_string=1, stat__=0):
    """
    Build the sql expressions string
    """
    search_key_class = None
    value = self.getValue()
    key = self.getKey()
    operator = self.getOperator()
    type = self.getType()
    format = self.getFormat()
    search_mode = self.getSearchMode()
    range_value = self.getRange()
    search_key = self.getSearchKey()

    if keyword_search_keys is None:
      keyword_search_keys = []
    if datetime_search_keys is None:
      datetime_search_keys = []
    if full_text_search_keys is None:
      full_text_search_keys = []

    # key can have an alias definition which we should acquire
    if key_alias_dict is not None:
      key = key_alias_dict.get(key, None)

    search_key_class = None
    where_expression_list = []
    select_expression_list = []    
    sql_expressions = {'where_expression': '1', 
                       'select_expression_list': []}
    
    # try to get search key type by the key definitions passed
    if search_key_class is None:
      if search_key == EXACT_MATCH_SEARCH_MODE:
        search_key_class =  RawKey
      elif search_key == KEYWORD_SEARCH_MODE or \
          (key in keyword_search_keys):
        search_key_class =  KeyWordKey
      elif search_key == DATETIME_SEARCH_MODE or \
        (key in datetime_search_keys):
        search_key_class =  DateTimeKey
      elif search_key == FULL_TEXT_SEARCH_MODE or \
        (key in full_text_search_keys):
        search_key_class =  FullTextKey
    
    # get search class based on explicitly passed key type
    if search_key_class is None:
      search_key_class = self._getSearchKeyClassByType(type)
    
    # some use cases where we can just return SQL without grammar staff
    if key is None or (ignore_empty_string and \
                       isinstance(value, basestring) and \
                       value.strip() == ''):
      # do not further generate sql expressions because
      # we ignore empty strings by default
      return sql_expressions
    elif ignore_empty_string==0 and isinstance(value, basestring) and value.strip() == '':
      # explicitly requested not to ignore empty strings
      sql_expressions = {'where_expression': "%s = ''" %key, 
                         'select_expression_list': []}
      return sql_expressions
    else:
      # search for 'NULL' values 
      if value is None:
        sql_expressions = {'where_expression':  "%s is NULL" % (key),
                           'select_expression_list': [],}
        return sql_expressions                 
            
      # we have a list of values and respective operator defined
      if isinstance(value, (tuple, list)):
        if range_value is None:
          # use operators to build sql expressions
          if operator in ('IN',):
            # values in list are not treated as searchable strings but 
            # they should be SQL quoted at least
            if len(value) > 1:
              if search_key_class is None:
                # no explicitly defined, try to find by value
                search_key_class = self._getSearchKeyClassByValue(value[0]) 
              search_key_instance = getSearchKeyInstance(search_key_class)
              escaped_value_list = [search_key_instance.quoteSQLString(x, format) for x in value]
              escaped_value_string = ', '.join(escaped_value_list)
              where_expression_list.append("%s IN (%s)" % (key, escaped_value_string))
            elif len(value) == 1:
              if search_key_class is None:
                # no explicitly defined, try to find by value            
                search_key_class = self._getSearchKeyClassByValue(value[0])
              search_key_instance = getSearchKeyInstance(search_key_class)               
              where_expression_list.append("%s = %s" 
                                           %(key, search_key_instance.quoteSQLString(value[0], format)))
            else:
              # empty list
              where_expression_list.append("0")          
          elif operator in ('OR', 'AND',):
            # each of the list elements can be treated as a Key, so 
            # leave SQL generation to Key itself
            if len(value) > 1:
              sql_logical_sub_expressions = []
              if search_key_class is None:
                # no explicitly defined, try to find by value
                search_key_class = self._getSearchKeyClassByValue(value[0]) 
              for item in value:
                list_item_sql_expressions = self._asSQLExpression(search_key_class, key, \
                                                                   item, format, search_mode, range_value, stat__)
                sql_logical_sub_expressions.append('%s' %list_item_sql_expressions['where_expression'])
              # join list items (now sql logical expressions) using respective operator
              where_expression = (' %s ' %operator).join(sql_logical_sub_expressions)
              where_expression_list.append("(%s)" % (where_expression))
            elif len(value) == 1:
              if search_key_class is None:
                # no explicitly defined, try to find by value            
                search_key_class = self._getSearchKeyClassByValue(value[0])            
              item_sql_expressions = self._asSQLExpression(search_key_class, key, \
                                                            value[0], format, search_mode, range_value, stat__)
              where_expression_list.append(item_sql_expressions['where_expression'])
          # join where expressions list
          where_expression = ' '.join(where_expression_list)
          sql_expressions = {'where_expression': where_expression,
                             'select_expression_list': [],}
          return sql_expressions
        else:
          # we can have range specified
          if search_key_class is None:
            # try to guess by type of first_element in list
            search_key_class = self._getSearchKeyClassByValue(value[0])
      
      # get search class based on value of value
      if search_key_class is None:
        search_key_class = self._getSearchKeyClassByValue(value)
      
      # last fallback case
      if search_key_class is None:
        search_key_class = DefaultKey
        
      # use respective search key.       
      sql_expressions = self._asSQLExpression(search_key_class, key, 
                                                value, format, search_mode, range_value, stat__)
      return sql_expressions

allow_class(SimpleQuery)

from Products.ZSQLCatalog.SearchKey.DefaultKey import DefaultKey
from Products.ZSQLCatalog.SearchKey.RawKey import RawKey
from Products.ZSQLCatalog.SearchKey.KeyWordKey import KeyWordKey
from Products.ZSQLCatalog.SearchKey.DateTimeKey import DateTimeKey
from Products.ZSQLCatalog.SearchKey.FullTextKey import FullTextKey
from Products.ZSQLCatalog.SearchKey.FloatKey import FloatKey
from Products.ZSQLCatalog.SQLCatalog import getSearchKeyInstance
