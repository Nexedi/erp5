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
# of the License,] or (at your option) any later version.
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
    
from Products.ZSQLCatalog.Query.SimpleQuery import SimpleQuery as Query
from Products.ZSQLCatalog.Query.ComplexQuery import ComplexQuery
from Products.ZSQLCatalog.SQLCatalog import getSearchKeyInstance

import ply.yacc as yacc
import ply.lex as lex
         
class BaseKey:
  """ BaseKey is a base class that implements a parser of 
      search grammar used in ERP5. It also implements all generic 
      search key class methods."""
  
  # main logical operators
  operators = ('OR', 'AND',)
  default_operator = '='
  
  # in ERP5 search grammer white space is extremely important
  # so we can not ignore it.
  #t_ignore  = ' \t' 
  
  # no need to rack down line numbers
  #def t_newline(self, t):
  #  r'\n+'
  #  #t.lexer.lineno += len(t.value)
  
  def t_error(self, t):
    #print "Illegal character '%s'" % t.value[0]
    t.lexer.skip(1)
    
  def p_error(self, p):
    pass
 
  def build(self, **kwargs):
    """ This method will initialize respective search key class with 
        tokens' definitions. """
    self.lexer = lex.lex(object = self, **kwargs)
  
  def tokenize(self, data):
    """ Return list of tokens according to respective 
        search key tokens' definitions. """
    result = []
    self.lexer.input(data)
    while 1:
      tok = self.lexer.token()
      if not tok: 
        break
      result.append(tok) 
    return result

  # Grouping of tokens
  def getOperatorForTokenList(self, tokens):
    """ Generic implementation that will return respective 
        operator for a token list. The first found occurence wins."""
    token = tokens[0]        
    token_type = token.type
    if token_type in self.sub_operators:
      return token.value, tokens[1:]
    else:
      return self.default_operator, tokens    
        
  def groupByLogicalOperator(self, tokens, logical_operator ='OR'):
    """ Split tokens list into one or many OR concatanated tokens list 
    """
    sub_tokens_or_groups = []
    tmp_token_list = []
    for token in tokens:
      if token.type != logical_operator:
        tmp_token_list.append(token)
      else:
        sub_tokens_or_groups.append(tmp_token_list)
        tmp_token_list = []
    # append remainig last tokens
    sub_tokens_or_groups.append(tmp_token_list)
    return sub_tokens_or_groups    
  
  # SQL quoting (each search key should override them it if needed)
  def quoteSQLKey(self, key, format):
    """ Return a quoted string of the value. """
    return key  
    
  def quoteSQLString(self, value, format):
    """ Return a quoted string of the value. """
    return "'%s'" %value    
  
  # SQL generation
  def buildSQLExpression(self, key, value, 
                         format = None, mode = None, range_value = None, stat__=0):
    """ Generic implementation. Leave details to respective key. """
    if range_value is not None:
      # if range_value we handle directly (i.e no parsing of search string)
      where_expressions, select_expressions = \
         self.buildSQLExpressionFromRange(key, value, 
                                          format, mode, range_value, stat__) 
    else:
      # search string parsing is needed
      where_expressions, select_expressions = \
        self.buildSQLExpressionFromSearchString(key, str(value), 
                                                format, mode, range_value, stat__) 
    return where_expressions, select_expressions    
    
  def buildSQLExpressionFromSearchString(self, key, value, format, mode, range_value, stat__):
    complex_query = self.buildQuery(key, value, format, mode, range_value, stat__)
    if complex_query is None:
      # Query could not be generated from search string
      sql_expression = {'where_expression': '1', 
                        'select_expression_list': []}
    else:
      sql_expression = complex_query(keyword_search_keys = [],
                                     datetime_search_keys = [], 
                                     full_text_search_keys = [])
    return sql_expression['where_expression'], sql_expression['select_expression_list']
     
  def buildQuery(self, key, value, format, mode, range_value, stat__):
    """ Build Query """
    query_list = []   
    # tokenize searchs string into tokens for Search Key
    tokens = self.tokenize(value)
    
    # split tokens list into one or more 'OR' tokens lists
    tokens_or_groups = self.groupByLogicalOperator(tokens, 'OR')
    
    # remove empty tokens lists
    tokens_or_groups = filter(lambda x: len(x), tokens_or_groups)
    
    # get a ComplexQuery for a sub token list    
    for tokens_or_group in tokens_or_groups:
      query = self.buildQueryForTokenList(tokens_or_group, key, value, format)
      if query is not None:
        # query could be generated for token list
        query_list.append(query)
    
    if len(query_list):
      # join query list in one really big ComplexQuery
      return ComplexQuery(*query_list, 
                          **{'operator':'OR'}) 

  def buildQueryForTokenList(self, tokens, key, value, format):
    """ Build a ComplexQuery for a token list """
    query_list = []
    logical_groups = self.groupByLogicalOperator(tokens, 'AND')
    for group_tokens in logical_groups:
      token_values = [x.value for x in group_tokens]
      sub_operator, sub_tokens = self.getOperatorForTokenList(group_tokens)
      sub_tokens_values = [x.value for x in sub_tokens]
      query_kw = {key: ' '.join(sub_tokens_values),
                  'type': self.default_key_type,
                  'format': format,
                  'range': sub_operator}
      query_list.append(Query(**query_kw))

    # join query list in one really big ComplexQuery
    complex_query = ComplexQuery(*query_list, 
                                 **{'operator': 'AND'})
    return complex_query                       
                   
  def buildSQLExpressionFromRange(self, key, value, format, mode, range_value, stat__):
    """ This method will generate SQL expressions
       from explicitly passed list of values and 
       range_value in ('min', 'max', ..)"""
    key = self.quoteSQLKey(key, format)  
    where_expression = ''
    select_expressions = []
    if isinstance(value, (list, tuple)):
      if len(value) > 1:
        # value should contain at least two items
        query_min = self.quoteSQLString(value[0], format)
        query_max = self.quoteSQLString(value[1], format)
      else:
        # value contains only one item
        query_min = query_max = self.quoteSQLString(value[0], format)          
    else:
      query_min = query_max = self.quoteSQLString(value, format)
    if range_value == 'min':
      where_expression = "%s >= %s" % (key, query_min)
    elif range_value == 'max':
      where_expression = "%s < %s" % (key, query_max)
    elif range_value == 'minmax' :
      where_expression = "%s >= %s AND %s < %s" % (key, query_min, key, query_max)
    elif range_value == 'minngt' :
      where_expression = "%s >= %s AND %s <= %s" % (key, query_min, key, query_max)
    elif range_value == 'ngt':
      where_expression =  "%s <= %s" % (key, query_max)
    elif range_value == 'nlt':
      where_expression = "%s > %s" % (key, query_max)
    elif range_value == 'like':
      where_expression = "%s LIKE %s" % (key, query_max)
    elif range_value == 'not_like':
      where_expression = "%s NOT LIKE %s" % (key, query_max)
    elif range_value in ('=', '>', '<', '>=', '<=','!=',):
      where_expression = "%s %s %s" % (key, range_value, query_max)    
    return where_expression, select_expressions

    
    
##  def groupByOperator(self, tokens, group_by_operators_list = operators):
##    """ Generic implementation of splitting tokens into logical
##        groups defided by respective list of logical operator
##        defined for respective search key.  """
##    items = []
##    last_operator = None
##    operators_mapping_list = []
##    last_operator = {'operator': None,
##                     'tokens': []}
##    for token in tokens:
##      token_type = token.type
##      token_value = token.value
##      if token_type in group_by_operators_list:
##        # (re) init it
##        last_operator = {'operator': token,
##                         'tokens': []}
##        operators_mapping_list.append(last_operator)
##      else:
##        # not an operator just a value token
##        last_operator['tokens'].append(token)
##        if last_operator not in operators_mapping_list:
##          operators_mapping_list.append(last_operator)
##    return operators_mapping_list      
