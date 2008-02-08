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

from Products.ZSQLCatalog.Query.SimpleQuery import SimpleQuery as Query
from Products.ZSQLCatalog.Query.ComplexQuery import ComplexQuery
from Products.ZSQLCatalog.SQLCatalog import getSearchKeyInstance
from Key import BaseKey
from pprint import pprint

class KeyWordKey(BaseKey):
  """ KeyWordKey key is an ERP5 portal_catalog search key which is used to render
      SQL expression that will try to match all possible values in a greedy manner.
      It supports following special operator ['=', '%', '>' , '>=', '<', '<='] in
      addition to main logical operators like ['OR', 'or', 'AND', 'and'].
      
      Examples for title column: 
        * 'foo or bar'  --> "title LIKE '%foo%' OR title LIKE '%bar%'"
        * 'foo or =bar'  --> "title LIKE '%foo%' OR title = 'bar'"
        * 'Organisation Module' -->  "title LIKE '%Organisation Module%'"
        * '"Organisation Module"' --> "title LIKE '%Organisation Module%'"
        * '="Organisation Module"' --> "title  = 'Organisation Module'"
    
  """
  
  tokens =  ('OR', 'AND', 'NOT', 
             'KEYWORD', 'WORDSET', 'WORD', 'EXPLICITEQUALLITYWORD',
             'GREATERTHAN', 'GREATERTHANEQUAL', 
             'LESSTHAN', 'LESSTHANEQUAL')
  
  sub_operators = ('GREATERTHAN', 'GREATERTHANEQUAL', 
                    'LESSTHAN', 'LESSTHANEQUAL', 'NOT')
  
  # this is the default operator
  default_operator = 'like'  
  
  # if token's list starts with left sided operator
  # use this map to transfer it to range operator
  token_operator_range_map = {'like': 'like',
                              '!=': 'not_like',
                              '=': '=',}
                    
  # Note: Order of placing rules (t_WORD for example) is very important
  def t_OR(self, t):
    r'(\s+OR\s+|\s+or\s+)'
    # operator must have leading and trailing ONLY one white space character
    # otherwise it's treated as a WORD
    t.value = 'OR'
    return t

  def t_AND(self, t):
    r'(\s+AND\s+|\s+and\s+)'
    # operator must have leading and trailing ONLY one white space character
    # otherwise it's treated as a WORD
    t.value = 'AND'
    return t  

  def t_NOT(self, t):
    r'(\s+NOT\s+|\s+not\s+|!=)'
    # operator must have leading and trailing ONLY one white space character
    # otherwise it's treated as a WORD
    t.value = t.value.upper().strip()
    return t     

  t_GREATERTHANEQUAL = r'>='
  t_LESSTHANEQUAL = r'<='
  t_GREATERTHAN = r'>'
  t_LESSTHAN = r'<'

  def t_EXPLICITEQUALLITYWORD(self, t):
    r'=[\x7F-\xFF\w\d\/~!@#$^&*()_+][\x7F-\xFF\w\d\/~!@#$^&*()_+]*'
    # EXPLICITEQUALLITYWORD may contain arbitrary letters and numbers without white space
    # EXPLICITEQUALLITYWORD must contain '=' at the beginning
    value = t.value.strip()
    # get rid of leading '='
    t.value = value[1:]
    return t        
    
  def t_KEYWORD(self, t):
    r'%?[\x7F-\xFF\w\d/~!@#$%^&*()_+][\x7F-\xFF\w\d/~!@#$%^&*()_+]*%?'
    # KEYWORD may starts(1) and may ends (2) with '%' but always must either #1 or #2
    # be true. It may contains arbitrary letters, numbers and white space
    value = t.value.strip()
    if not value.startswith('%') and not value.endswith('%'):  
      t.type = 'WORD'  
    t.value = value
    return t    
    
  def t_WORD(self, t):
    r'[\x7F-\xFF\w\d\/~!@#$^&*()_+][\x7F-\xFF\w\d\/~!@#$^&*()_+]*'
    # WORD may contain arbitrary letters and numbers without white space
    # WORD may contain '%' but not at the beginning or end (otherwise it's KEYWORD)
    value = t.value.strip()
    t.value = value
    return t     
  
  def t_WORDSET(self, t):
    r'=?"[\x7F-\xFF\w\d\s\/~!@#$%^&*()_+][\x7F-\xFF\w\d\s\/~!@#$%^&*()_+]*"'
    # WORDSET is a combination of WORDs separated by white space
    # and starting/ending with " (optionally with '=')
    value = t.value.replace('"', '')
    t.value = "%s" %value
    return t 
    
  def quoteSQLString(self, value, format):
    """ Return a quoted string of the value. """
    return "'%s'" %value
  
  def getOperatorForTokenList(self, tokens):
    """ Generic implementation that will return respective 
        operator for a token list. The first found occurence wins."""
    token = tokens[0]        
    token_type = token.type
    if token_type in self.sub_operators:
      return token.value, tokens[1:]
    elif token.type == 'EXPLICITEQUALLITYWORD':
      # even though it's keyword key we can still explicitly define 
      # that we want equality
      return '=', tokens
    else:
      return self.default_operator, tokens  
  
  def buildQueryForTokenList(self, tokens, key, value, format):
    """ Build a ComplexQuery for a token list """
    query_list = []
    for group_tokens in self.groupByLogicalOperator(tokens, 'AND'):
      token_values = [x.value for x in group_tokens]
      sub_operator, sub_tokens = self.getOperatorForTokenList(group_tokens)
      first_token = sub_tokens[0]
      range = self.token_operator_range_map.get(sub_operator)
      
      sub_tokens_values = [x.value for x in sub_tokens]
      right_side_expression = ' '.join(sub_tokens_values)
      if first_token.type == 'WORDSET' and first_token.value.startswith('='):
        range = '='
        right_side_expression = first_token.value[1:]
      elif first_token.type in ('WORDSET', 'WORD',) and range == 'like':
        # add trailing and leading '%' to get more results
        right_side_expression = '%%%s%%' %right_side_expression
      query_kw = {key: right_side_expression,
                  'range': range}
      query_list.append(Query(**query_kw))

    # join query list in one really big ComplexQuery
    complex_query = ComplexQuery(*query_list, 
                                 **{'operator': 'AND'})
    return complex_query

    
##  def buildSQLExpressionFromSearchString(self, key, value, format, mode, range_value, stat__):
##    """ Tokenize/analyze passed string value and generate SQL query expressions. """
##    where_expressions = []
##    select_expressions = []
##    tokens = self.tokenize(value)
##    operators_mapping_list = self.groupByOperator(tokens)
##    
##    # find if any logical operator exists
##    tokens_values = []
##    logical_operator_found = 0
##    for token in tokens:
##      if token.type not in ('WORD',):
##        logical_operator_found = 1
##        break
##      tokens_values.append(token.value.replace("'", ""))
##      
##    # build expressions
##    if not logical_operator_found:
##      # no logical operator found so we assume that we search 
##      # for a combination of words
##      where_expressions.append("%s LIKE '%%%s%%'" %(key, ' '.join(tokens_values)))
##    else:
##      # in the search string we have explicitly defined an operator
##      for item in operators_mapping_list:
##        row_tokens_values = []
##        tokens = item['tokens']
##        operator = item['operator']
##        operator_value = None
##        if operator is not None:
##          # operator is standalone expression
##          where_expressions.append('%s' %operator.value)
##        if len(tokens):
##          # no it's not a stand alone expression, 
##          # determine it from list of tokens
##          sub_where_expression = ''
##          tokens_number = len(tokens)
##          if tokens_number == 1:
##            # no left sided operator (<, >, >=, <=) found
##            token = tokens[0]
##            if token.type == 'WORD':
##              sub_where_expression = "LIKE '%%%s%%'" %token.value
##            elif token.type == 'KEYWORD':
##              sub_where_expression = "LIKE '%s'" %token.value
##            elif token.type == 'EXPLICITEQUALLITYWORD':
##             sub_where_expression = "= '%s'" %token.value
##            elif token.type == 'WORDSET' and token.value.startswith('='):
##              # if WORDSET starts with '=' it's an equality
##              sub_where_expression = " = '%s'" %token.value[1:]
##            else:
##              sub_where_expression = "LIKE '%%%s%%'" %token.value
##          else:
##            # we have two or more tokens, by definition first one should be 
##            # logical operator like (<, >, >=, <=)
##            operator = tokens[0]
##            operator_value = operator.value
##            if operator.type in ('KEYWORD', 'WORDSET', 'WORD'):
##              # no operator for this token list, assume it's 'LIKE'
##              sub_where_expression = "LIKE '%s'" %' '.join([x.value for x in tokens])
##            else:
##              # we have operator and by convention if operator is used it's applyied to one token only
##              sub_where_expression = "%s'%s'" %(operator_value, tokens[1].value)
##          where_expressions.append('%s %s' %(key, sub_where_expression))
##    return where_expressions, select_expressions
