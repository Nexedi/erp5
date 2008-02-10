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

from SearchKey import SearchKey
from pprint import pprint

class DefaultKey(SearchKey):
  """ DefaultKey key is an ERP5 portal_catalog search key which is used to render
      SQL expression that will try to exactly one value.
      It supports following special operator ['=', '%', '>' , '>=', '<', '<='] in
      addition to main logical operators like ['OR', 'or', 'AND', 'and'].

      Examples for title column:
        * 'foo or bar'  --> "title = 'foo' OR title = 'bar'"
        * 'foo or =bar'  --> "title = 'foo' OR title = 'bar'"
        * '%foo% or bar' --> "title = '%foo%' OR title = 'bar'"
        * 'Organisation Module' -->  "title = 'Organisation Module'"
        * '"Organisation Module"' --> "title = 'Organisation Module'"
        * '="Organisation Module"' --> "title = 'Organisation Module'"
  """

  # default type of sub Queries to be generated out fo a search string
  default_key_type = 'default'

  tokens =  ('OR', 'AND', 'NOT', 'WORDSET', 'WORD',
             'GREATERTHAN', 'GREATERTHANEQUAL',
             'LESSTHAN', 'LESSTHANEQUAL')

  sub_operators = ('GREATERTHAN', 'GREATERTHANEQUAL',
                    'LESSTHAN', 'LESSTHANEQUAL', 'NOT')


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
    t.value = '!='
    return t

  t_GREATERTHANEQUAL = r'>='
  t_LESSTHANEQUAL = r'<='
  t_GREATERTHAN = r'>'
  t_LESSTHAN = r'<'

  def t_WORD(self, t):
    r'[\x7F-\xFF\w\d\/\-~!@#$%^&*()_+\n][\x7F-\xFF\w\d\/\-~!@#$%^&*()_+\n]*'
    #r'[\x7F-\xFF\w\d\/%][\x7F-\xFF\w\d\/%]*'
    # WORD may contain arbitrary letters and numbers without white space
    # WORD may contain '%' but not at the beginning or end (otherwise it's KEYWORD)
    value = t.value.strip()
    t.value = "%s" %value
    return t

  def t_WORDSET(self, t):
    r'"[\x7F-\xFF\w\d\s\/~!@#$%^&*()_+][\x7F-\xFF\w\d\s\/~!@#$%^&*()_+]*"'
    #r'"[\x7F-\xFF\w\d\s/%][\x7F-\xFF\w\d\s/%]*"'
    # WORDSET is a combination of WORDs separated by white space
    # and starting/ending with "
    value = t.value.replace('"', '').strip()
    t.value = "%s" %value
    return t

  def quoteSQLString(self, value, format):
    """ Return a quoted string of the value. """
    if isinstance(value, (int, long,)):
      return str(value)
    return "'%s'" %value


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
##      if token.type not in ('WORDSET', 'WORD',):
##        logical_operator_found = 1
##        break
##      tokens_values.append(token.value.replace("'", ""))
##
##    # build expressions
##    if not logical_operator_found:
##      # no logical operator found so we assume that we search for a combination of words
##      where_expressions.append("%s = '%s'" %(key, ' '.join(tokens_values)))
##    else:
##      # in the search string we have explicitly defined an operator
##      for item in operators_mapping_list:
##        row_tokens_values = []
##        tokens = item['tokens']
##        operator = item['operator']
##        operator_value = None
##        if operator is not None:
##          # operator is standalone expression
##          operator_value = operator.value
##          where_expressions.append('%s' %operator_value)
##        if len(tokens):
##          # no it's not a stand alone expression,
##          # determine it from list of tokens
##          operator_value, sub_tokens = self.getOperatorForTokenList(tokens)
##          row_tokens_values = [x.value for x in sub_tokens]
##          where_expressions.append("%s %s '%s'" %(key, operator_value, ' '.join(row_tokens_values)))
##    return where_expressions, select_expressions   
