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
from DateTime import DateTime
from Key import BaseKey
from pprint import pprint

 
class DateTimeKey(BaseKey):
  """ DateTimeKey key is an ERP5 portal_catalog search key which is used to render
      SQL expression that will try to match values in DateTime MySQL columns.
      It supports following special operator ['=', '%', '>' , '>=', '<', '<='] in
      addition to main logical operators like ['OR', 'or', 'AND', 'and'].
      
      Note: because all ERP5 datetime values are indexed in MySQL in 'UTC' 
      the respective passed date will be first converted to 'UTC' before inserted into
      respective SQL query!
      
      Examples (GMT+02, Bulgaria/Sofia for 'delivery.start_date'):
      
        * '15/01/2008' --> "delivery.start_date = '2008-01-14 22:00'"
        
        * '>=15/01/2008' --> "delivery.start_date >= '2008-01-14 22:00'"      
        
        * '>=15/01/2008 or <=20/01/2008' 
          --> "delivery.start_date >= '2008-01-14 22:00' or delivery.start_date<='2008-01-19 22:00'"
        
        * '>=15/01/2008 10:00 GMT+02 OR <=20/01/2008 05:12 Universal'
          -->
          "delivery.start_date >= '2008-01-15 08:00 Universal' 
            OR 
          delivery.start_date <= '2008-01-20 05:12 Universal'
          "
  """
  
  tokens =  ('DATE', 'OR', 'AND', 'NOT', 'EQUAL',
             'GREATERTHAN', 'GREATERTHANEQUAL',
             'LESSTHAN', 'LESSTHANEQUAL')
             
  sub_operators =  ('GREATERTHAN', 'GREATERTHANEQUAL', 
                    'LESSTHAN', 'LESSTHANEQUAL', 'NOT', 'EQUAL',)
 
  def t_OR(self, t):
    r'(\s+OR\s+|\s+or\s+)'
    # operator has leading and trailing ONLY one white space character
    t.value = 'OR'
    return t

  def t_AND(self, t):
    r'(\s+AND\s+|\s+and\s+)'
    # operator has leading and trailing ONLY one white space character
    t.value = 'AND'
    return t 
  
  def t_NOT(self, t):
    r'(\s+NOT\s+|\s+not\s+|!=)'
    # operator has leading and trailing ONLY one white space character
    t.value = t.value.upper().strip()
    return t   

  t_GREATERTHANEQUAL = r'>='  
  t_LESSTHANEQUAL = r'<='  
  t_GREATERTHAN = r'>'
  t_LESSTHAN = r'<'
  t_EQUAL = r'='    
  t_DATE = r'\d{1,4}[(/|\.|\-) /.]\d{1,4}[(/|\.|\-) /.]\d{1,4}((\s.)*\d{0,2}:\d{0,2}(:\d{0,2})?)?(\sUniversal|\sGMT\+\d\d)?|\d\d\d\d%?'
          
  def quoteSQLString(self, value, format):
    """ Return a quoted string of the value. 
        Make sure to convert it to UTC first."""
    if getattr(value, 'ISO', None) is not None:
      value = "'%s'" % value.toZone('UTC').ISO()
    else:
      value = "'%s'" %DateTime(value).toZone('UTC').ISO()
    return value
       
  def buildQueryForTokenList(self, tokens, key, value, format):
    """ Build a ComplexQuery for a token list """
    query_list = []
    for group_tokens in self.groupByLogicalOperator(tokens, 'AND'):
      token_values = [x.value for x in group_tokens]
      sub_operator, sub_tokens = self.getOperatorForTokenList(group_tokens)
      date_value = sub_tokens[0].value
      days_offset = 0
      # some format require special handling
      if format != '%Y':
        # full format (Year/Month/Day)
        if sub_operator in ('=',):
          # 2007/01/01 00:00 <= date < 2007/01/02
          days_offset = 1
      elif format == '%Y':
        # incomplete format only Year because DateTime can not handle
        # extend format and value by assumption that start of year is ment
        # add days ofset accordingly
        format = '%%%s/%%m/%%d' %format
        date_value = '%s/01/01' %date_value
        days_offset_map = {'=' : 366, '>' : 366, 
                           '>=' : 366, '<': -366, '<=':-366}
        days_offset = days_offset_map[sub_operator]
  
      # convert to UTC in given format
      is_valid_date = 1
      try:
        if format != '%m/%d/%Y':
          # treat ambigious dates as "days before month before year"
          date_value = DateTime(date_value, datefmt="international").toZone('UTC')
        else:
          # US style "month before day before year"
          date_value = DateTime(date_value).toZone('UTC')
      except:
        is_valid_date = 0
      
      query_kw = None       
      if is_valid_date:
        if sub_operator == '=':
          # transform to range 'key >= date  AND  date < key'
          query_kw = {key: (date_value, date_value + days_offset,),
                      'range': 'minmax'} 
        else:
          query_kw = {key: date_value + days_offset,
                      'range': sub_operator}   
        query_kw['type'] = 'date'              
      else:
        # not a valid date, try to get an year range
        is_year = 1
        date_value = date_value.replace('%', '')
        try: date_value = int(date_value)
        except: is_year = 0
        if is_year:
          date_value = '%s/01/01' % date_value
          date_value = DateTime(date_value).toZone('UTC')
          query_kw = {key: (date_value, date_value + 366,),
                      'type': 'date',
                      'range': 'minmax'} 
                      
      # append only if it was possible to generate query
      if query_kw is not None:
        query_list.append(Query(**query_kw))                    
        
    # join query list in one really big ComplexQuery
    if len(query_list):
      complex_query = ComplexQuery(*query_list, 
                                   **{'operator': 'AND'})
      return complex_query   
       
##  def buildSQLExpressionFromSearchString(self, key, value, format, mode, range_value, stat__):
##    """ Tokenize/analyze passed string value and generate SQL query expressions. """
##    where_expression = ''
##    key = self.quoteSQLKey(key, format)
##    tokens = self.tokenize(value)
##    operators_mapping_list = self.groupByOperator(tokens)
##    # new one
##    for item in operators_mapping_list:
##      row_tokens_values = []
##      tokens = item['tokens']
##      operator = item['operator']
##      operator_value = None
##      if operator is not None:
##        # operator is standalone expression
##        operator_value = operator.value
##        where_expressions.append('%s' %operator_value)
##      if len(tokens):
##        # no it's not a stand alone expression, 
##        # determine it from list of tokens
##        operator_value, sub_tokens = self.getOperatorForTokenList(tokens)
##        row_tokens_values = [self.quoteSQLString(x.value, format) for x in sub_tokens]
##        where_expression = "%s %s %s" %(key, operator_value, ' '.join(row_tokens_values))
##    return where_expression, []
