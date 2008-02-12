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
from Products.PythonScripts.Utility import allow_class

from SearchKey import SearchKey
from pprint import pprint

# these keys are used to build query in case for ScriptableKey 
# when no key was specified in fornt of value
DEFAULT_SEARCH_KEYS = ('SearchableText', 'reference', 'title',)

class KeyMappingKey(SearchKey):
  """ Usable lexer class used (internally) by ScriptableKey lexer than can parse following:
      VALUE OPERATOR VALUE

      Examples:
        * "portal_type : Person"
        * "creation_date > 2007-01-01"
  """

  tokens =  ('OPERATOR', 'COLONOPERATOR', 'VALUE',)

  t_OPERATOR = r'>=|<=|>|<'
  t_VALUE = r'[\x7F-\xFF\w\d\/~!@#$^&*()_+-][\x7F-\xFF\w\d\/~!@#$^&*()_+-]*'

  def t_COLONOPERATOR(self, t):
    r':'
    # ':' is the same as '=' (equality)
    t.value = '='
    return t

class ScriptableKey(SearchKey):
  """ KeyWordKey key is an ERP5 portal_catalog search key which is used to generate a 
      ComplexQuery instance out of an arbitrary search string.

      Examples: 
        * "John Doe AND portal_type:Person AND creation_date > 2007-01-01" 

        would be turned into following ComplexQuery:

        *  ComplexQuery(Query(portal_type='Person'),
                       Query(creation_date='2007-01-01', operator='>'),
                       ComplexQuery(Query(searchable_text='John Doe'),
                                    Query(title='John Doe'),
                                    Query(reference='John Doe'),
                                    operator='OR')
                       operator='AND'))
  """
  sub_operators =  ('GREATERTHAN', 'GREATERTHANEQUAL', 
                    'LESSTHAN', 'LESSTHANEQUAL',)

  tokens =  ('OR', 'AND',  
             'DATE', 'WORD', 'KEYMAPPING',
             'GREATERTHAN', 'GREATERTHANEQUAL', 
             'LESSTHAN', 'LESSTHANEQUAL', 'EQUAL')

  t_GREATERTHANEQUAL = r'>='  
  t_LESSTHANEQUAL = r'<='  
  t_GREATERTHAN = r'>'
  t_LESSTHAN = r'<'
  t_EQUAL = r'='

  # Note: Order of placing rules (t_WORD for example) is very important
  def t_OR(self, t):
    r'\s+(OR|or)\s+'
    # operator must have leading and trailing ONLY one white space character
    # otherwise it's treated as a WORD
    t.value = 'OR'
    return t

  def t_AND(self, t):
    r'\s+(AND|and)\s+'
    # operator must have leading and trailing ONLY one white space character
    # otherwise it's treated as a WORD
    t.value = 'AND'
    return t  

  def t_KEYMAPPING(self, t):
    r'[^<>=:\s]+\s*(>|<|<=|>=|:)\s*\S+'
    # KEYMAPPING has following format: KEY OPERATOR VALUE 
    # where OPERATOR in ['<', '>', '<=', '>=', ':']
    # example: 'creation_date < 2007-12-12'
    value = t.value.strip()
    t.value = value
    return t 

  def t_WORD(self, t):
    r'[^<>=\s:]+'
    # WORD may contain arbitrary letters and numbers without white space
    # WORD may contain '%' but not at the beginning or end (otherwise it's KEYWORD)
    value = t.value.strip()
    t.value = value
    return t

  def buildQueryForTokenList(self, tokens):
    """ Build a ComplexQuery for a token list """
    query_list = []
    for group in self.groupByLogicalOperator(tokens, 'AND'):
      group_tokens = group
      first_group_token = group_tokens[0]
      if first_group_token.type == 'KEYMAPPING':
        # user specified a full sub query definition following this format:
        # 'key operator value'
        sub_search_string = group_tokens[0].value
        keymapping_lexer = getSearchKeyInstance(KeyMappingKey)
        sub_tokens = keymapping_lexer.tokenize(sub_search_string)
        sub_tokens_values = [x.value for x in sub_tokens]
        search_key, search_operator, search_value = sub_tokens_values
        query_kw = {search_key: search_value,
                    'range' : search_operator,}
        query_list.append(Query( **query_kw))
      elif first_group_token.type in self.sub_operators:
        # user specified a incomplete sub query definition following this format:
        # 'operator value'. Assume that he ment to search for 'title' and
        # use supplied 'operator'
        search_operator = first_group_token.value
        simple_query_value = ' '.join([x.value for x in group_tokens[1:]])
        query_kw = {'title': simple_query_value,
                    'range' : search_operator,}
        query_list.append(Query( **query_kw))
      else:
        # user specified a VERY incomplete sub query definition following this format:
        # 'value'. Let's search against most common search_keys and assume operator
        # is '=' (by default) and try to get as much possible results
        simple_query_value = ' '.join([x.value for x in group_tokens])
        sub_query_list = []
        for default_key in DEFAULT_SEARCH_KEYS:
          query_kw = {default_key: simple_query_value}
          sub_query_list.append(Query(**query_kw))
        query_list.append(ComplexQuery(*sub_query_list, 
                                       **{'operator':'OR'}))
    # join query list in one really big ComplexQuery
    complex_query = ComplexQuery(*query_list, 
                                 **{'operator':'AND'})
    return complex_query

  def buildQuery(self, key, value, 
                format=None, mode=None, range_value=None, stat__=None):
    """ Build ComplexQuery from passed search string value.
        When grouping expressions we use the following assumptions 
        that 'OR' operator has higher priority in a sense:

         * "John Doe AND portal_type:Person OR creation_date>=2005/12/12"

         is considered as:

         * (John Doe AND portal_type:Person) OR (creation_date>=2005/12/12)"
    """
    query_list = []
    tokens = self.tokenize(value)

    # split tokens list into one or many OR concatanated expressions
    sub_tokens_or_groups = self.groupByLogicalOperator(tokens, 'OR')

    # get a ComplexQuery for a sub token list    
    for tokens_or_group in sub_tokens_or_groups:
      query_list.append(self.buildQueryForTokenList(tokens_or_group))

    # join query list in one really big ComplexQuery
    complex_query = ComplexQuery(*query_list, 
                                 **{'operator':'OR'})      
    return complex_query

allow_class(ScriptableKey)
