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

SEARCH_MODE_MAPPING = {'in_boolean_mode': 'IN BOOLEAN MODE',
                       'with_query_expansion': 'WITH QUERY EXPANSION'}

class FullTextKey(SearchKey):
  """ FullTextKey key is an ERP5 portal_catalog search key which is used to render
      SQL expression that will try match all possible values using 
      MySQL's fulltext search support.
      See syntax see MySQL's FullText search reference: 
      http://dev.mysql.com/doc/refman/5.0/en/fulltext-search.html
  """

  tokens =  ('PLUS', 'MINUS', 'WORD', 'GREATERTHAN', 'LESSTHAN', 'LEFTPARENTHES', 
             'RIGHTPARENTHES', 'TILDE', 'ASTERISK', 'DOUBLEQUOTE',)

  # SQL expressions patterns
  relevance = '%s_relevance'
  where_match_against = "MATCH %s AGAINST ('%s' %s)"
  select_match_against_as = "MATCH %s AGAINST ('%s' %s) AS %s"

  t_PLUS = r'(\+)'
  t_MINUS = r'(\-)'
  t_GREATERTHAN = r'(\>)'
  t_LESSTHAN = r'(\<)'  
  t_LEFTPARENTHES = r'(\()'    
  t_RIGHTPARENTHES = r'(\))'
  t_TILDE = r'(\~)'   
  t_ASTERISK = r'(\*)'
  t_DOUBLEQUOTE = r'(\")'      

  def t_WORD(self, t):
    r'[\x7F-\xFF\w\d\/!@#$%^&_][\x7F-\xFF\w\d\/!@#$%^&_]*'
    #r'[\x7F-\xFF\w\d][\x7F-\xFF\w\d]*'
    # WORD may contain arbitrary letters and numbers without white space
    word_value = t.value
    t.value = "'%s'" %word_value
    return t

  def buildSQLExpression(self, key, value, 
                         format=None, mode=None, range_value=None, stat__=None):
    """ Analize token list and generate SQL expressions."""
    tokens = self.tokenize(value)
    # based on type tokens we may switch to different search mode
    mode = SEARCH_MODE_MAPPING.get(mode, '')
    if mode == '':
      # determine it based on list of tokens  i.e if we have only words 
      # leave as its but if we have '-' or '+' use boolean mode 
      for token in tokens:
        if token.type != 'WORD':
          mode = SEARCH_MODE_MAPPING['in_boolean_mode']
          break
    # split (if possible) to column.key
    if key.find('.') != -1:
      table, column = key.split('.')
      relevance_key1 = self.relevance %key.replace('.', '_')
      relevance_key2 = self.relevance %column
    else:
      relevance_key1 = self.relevance %key
      relevance_key2 = None
    select_expression_list = []
    where_expression = self.where_match_against %(key, value, mode)
    if not stat__:
      # stat__ is an internal implementation artifact to prevent adding
      # select_expression for countFolder    
      select_expression_list = [self.select_match_against_as %(key, value, mode, relevance_key1),]
      if  relevance_key2 is not None:
        select_expression_list.append(self.select_match_against_as %(key, value, mode, relevance_key2))
    return where_expression, select_expression_list
