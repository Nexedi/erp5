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

import unittest
from DateTime import DateTime
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ZSQLCatalog.SearchKey.DefaultKey import DefaultKey
from Products.ZSQLCatalog.SearchKey.RawKey import RawKey
from Products.ZSQLCatalog.SearchKey.KeywordKey import KeywordKey
from Products.ZSQLCatalog.SearchKey.DateTimeKey import DateTimeKey
from Products.ZSQLCatalog.SearchKey.FullTextKey import FullTextKey
from Products.ZSQLCatalog.SearchKey.FloatKey import FloatKey
from Products.ZSQLCatalog.SQLCatalog import getSearchKeyInstance
from Products.ZSQLCatalog.SearchKey.ScriptableKey import ScriptableKey, KeyMappingKey

class TestSearchKeyLexer(ERP5TypeTestCase):
  """Test search keys
  """
  run_all_test = 1
  quiet = 0
  
  def compare(self, search_key_class, search_value, expected_token_types):
    """ """
    key = getSearchKeyInstance(search_key_class)
    tokens = key.tokenize(search_value)  
    token_types = [x.type for x in tokens]
    self.assertSameSet(token_types, expected_token_types)  

  
  def test_01ProperPoolInitialization(self, quiet=quiet, run=run_all_test):
    """ Check that search key pool is properly initialized """
    if not run: return
    for search_key_class in (DefaultKey, RawKey, KeyWordKey, DateTimeKey, 
                         FullTextKey, FloatKey, ScriptableKey, KeyMappingKey):
      self.assertTrue(isinstance(getSearchKeyInstance(search_key_class), search_key_class))

  def test_02DefaultKey(self, quiet=quiet, run=run_all_test):
    """ Check lexer for DefaultKey."""
    if not run: return
    self.compare(DefaultKey, 'John', ('WORD',))
    self.compare(DefaultKey, 'group/nexedi', ('WORD',))
    self.compare(DefaultKey, 'John OR Petar', 
                             ('WORD', 'OR', 'WORD',))    
    self.compare(DefaultKey, 'John AND Petar', 
                            ('WORD', 'AND', 'WORD',))   
    self.compare(DefaultKey, 'John AND Petar OR Petar', 
                             ('WORD', 'AND', 'WORD', 'OR', 'WORD'))
    # at end operator is considered as WORD
    self.compare(DefaultKey, 'John OR', 
                             ('WORD', 'WORD'))  
    self.compare(DefaultKey, '=John OR "WORD SET"', 
                             ('WORD', 'OR', 'WORDSET')) 
    # multiple lines are considered as one WORD
    multi_lines = """colour/apparel_model_module/1/1
morphology/apparel_model_module/1/5
size/Child/34"""                         
    self.compare(DefaultKey, multi_lines, ('WORD',))  
    # non ASCII chars support
    self.compare(DefaultKey, 
                'S\xc3\xa9bastien or !="Doe John1" and Doe', 
                ('WORD', 'OR', 'NOT', 'WORDSET', 'AND', 'WORD',))  
                             
  def test_03KeyWordKey(self, quiet=quiet, run=run_all_test):
    """ Check lexer for KeyWordKey."""
    if not run: return
    self.compare(KeyWordKey, 'John', ('WORD',))
    self.compare(KeyWordKey, '%John', ('KEYWORD',))   
    self.compare(KeyWordKey, '%John%', ('KEYWORD',))  
    self.compare(KeyWordKey, 'John%', ('KEYWORD',))  
    self.compare(KeyWordKey, 'John% OR JOHN', 
                            ('KEYWORD', 'OR', 'WORD',))
    self.compare(KeyWordKey, 'John% and "JOHN John"', 
                            ('KEYWORD', 'AND', 'WORDSET',))
    self.compare(KeyWordKey, '<John% and >"JOHN John"', 
                            ('LESSTHAN', 'KEYWORD', 'AND', 
                             'GREATERTHAN', 'WORDSET',)) 
    self.compare(KeyWordKey, '<=John% and >="JOHN John"', 
                            ('LESSTHANEQUAL', 'KEYWORD', 'AND', 
                             'GREATERTHANEQUAL', 'WORDSET',))                             
    self.compare(KeyWordKey, '=John% and >="JOHN John"', 
                            ('EXPLICITEQUALLITYWORD', 'KEYWORD', 'AND', 
                             'GREATERTHANEQUAL', 'WORDSET',))
                             
  def test_04DateTimeKey(self, quiet=quiet, run=run_all_test):
    """ Check lexer for DateTimeKey."""
    if not run: return
    self.compare(DateTimeKey, '2007.12.23', ('DATE',))     
    self.compare(DateTimeKey, 
                 '=2007.12.23 22:00:00 Universal or =23/12/2007 10:10 and !=2009-12-12',
                 ('EQUAL', 'DATE', 'OR', 'EQUAL', 'DATE', 'AND', 'NOT', 'DATE',))   
    self.compare(DateTimeKey, 
                 '>=2007.12.23 22:00:00 GMT+02 or <=23/12/2007 and >2009/12/12 and <2009-11-11',
                 ('GREATERTHANEQUAL', 'DATE', 'OR', 'LESSTHANEQUAL', 'DATE', 
                   'AND', 'GREATERTHAN', 'DATE', 'AND', 'LESSTHAN', 'DATE'))
                     
  def test_05FullTextKey(self, quiet=quiet, run=run_all_test):
    """ Check lexer for FullTextKey."""  
    if not run: return
    self.compare(FullTextKey, 'John Doe', 
                 ('WORD', 'WORD',)) 
    self.compare(FullTextKey, '+John -Doe', 
                 ('PLUS', 'WORD', 'MINUS', 'WORD',)) 

  def test_06ScriptableKey(self, quiet=quiet, run=run_all_test):
    """ Check lexer for ScriptableKey."""  
    if not run: return
    self.compare(ScriptableKey, 
                'John Doe AND portal_type:Person OR creation_date>=2005/12/12',
                ('WORD', 'WORD', 'AND', 'KEYMAPPING', 'OR', 'KEYMAPPING',))
    self.compare(ScriptableKey, 
                'John Doe OR creation_date>=2005/12/12',
                ('WORD', 'WORD', 'OR', 'KEYMAPPING',))                
                   
class TestSearchKeyQuery(ERP5TypeTestCase):
  """Test search keys query generation
  """
  run_all_test = 1
  quiet = 0

  def compare(self, search_key_class, 
              key, value, expected_where_expression, expected_select_expression, format=None):
    """ compare generated SQL (as string)"""
    search_key_instance = getSearchKeyInstance(search_key_class)
    where_expression, select_expressions = \
       search_key_instance.buildSQLExpression(key, value, format)
    self.assertEqual(expected_where_expression, where_expression)
    self.assertEqual(expected_select_expression, select_expressions)

  def test_01DefaultKey(self, quiet=quiet, run=run_all_test):
    """ Check DefaultKey query generation"""
    if not run: return    
    self.compare(DefaultKey,
                'title',
                'John Doe', 
                "((((title = 'John Doe'))))",
                [])
    self.compare(DefaultKey,
                'title',
                '<John Doe', 
                "((((title < 'John Doe'))))",
                []) 
    self.compare(DefaultKey,
                'title',
                '>John Doe', 
                "((((title > 'John Doe'))))",
                [])
    self.compare(DefaultKey,
                'title',
                '>=John Doe or <=Doe John', 
                "((((title >= 'John Doe'))) OR (((title <= 'Doe John'))))",
                [])
    self.compare(DefaultKey,
                'title',
                '=John Doe and Doe John', 
                "((((title = 'John Doe') AND (title = 'Doe John'))))",
                [])
    self.compare(DefaultKey,
                'title',
                '!=John Doe or !=Doe John', 
                "((((title != 'John Doe'))) OR (((title != 'Doe John'))))",
                [])                  
    self.compare(DefaultKey,
                'title',
                '"John Doe" or "Doe John"', 
                "((((title = 'John Doe'))) OR (((title = 'Doe John'))))",
                []) 
    self.compare(DefaultKey,
                'title',
                '!="John Doe" or !="Doe John"', 
                "((((title != 'John Doe'))) OR (((title != 'Doe John'))))",
                [])
    self.compare(DefaultKey,
                'title',
                '%John and !=Doe%', 
                "((((title = '%John') AND (title != 'Doe%'))))",
                [])
                
  def test_02KeyWordKey(self, quiet=quiet, run=run_all_test):
    """ Check DefaultKey query generation"""
    if not run: return    
    self.compare(KeyWordKey,
                'title',
                'John Doe', 
                "((((title LIKE '%John Doe%'))))",
                [])
    self.compare(KeyWordKey,
                'title',
                '!=John Doe', 
                "((((title NOT LIKE 'John Doe'))))",
                [])       
    self.compare(KeyWordKey,
                'title',
                '%John Doe', 
                "((((title LIKE '%John Doe'))))",
                [])
    self.compare(KeyWordKey,
                'title',
                '%John Doe%', 
                "((((title LIKE '%John Doe%'))))",
                [])
    self.compare(KeyWordKey,
                'title',
                '%John Doe% or =Doe John', 
                "((((title LIKE '%John Doe%'))) OR (((title = 'Doe John'))))",
                [])       
                
  def test_03DateTimeKey(self, quiet=quiet, run=run_all_test):
    """ Check DefaultKey query generation"""
    if not run: return 
    now = DateTime()
    sql_quoted = now.toZone('UTC').ISO()
    self.compare(DateTimeKey,
                'delivery.start_date',
                '<%s' %now, 
                "((((delivery.start_date < '%s'))))" %sql_quoted,
                [])
    self.compare(DateTimeKey,
                'delivery.start_date',
                '>=%s' %now, 
                "((((delivery.start_date >= '%s'))))" %sql_quoted,
                [])
    self.compare(DateTimeKey,
                'delivery.start_date',
                '>=%s and <=%s' %(now, now), 
                "((((delivery.start_date >= '%s') AND (delivery.start_date <= '%s'))))"  %(sql_quoted, sql_quoted),
                [])
    # if only date is given assume range within the same day (24 hours)
    self.compare(DateTimeKey,
                'delivery.start_date',
                '%s' %now, 
                "((((delivery.start_date >= '%s' AND delivery.start_date < '%s'))))"  \
                  %(now.toZone('UTC').ISO(), (now +1).toZone('UTC').ISO()),
                [])   
    # %d/%m/%Y
    date_value = '11/01/2008'
    self.compare(DateTimeKey,
                'delivery.start_date',
                '<%s' %date_value, 
                "((((delivery.start_date < '%s'))))" %DateTime(date_value, datefmt="international").toZone('UTC').ISO(),
                [],
                '%d/%m/%Y')
    # %Y/%m/%d
    date_value = '2008/01/11'
    self.compare(DateTimeKey,
                'delivery.start_date',
                '>%s' %date_value, 
                "((((delivery.start_date > '%s'))))" %DateTime(date_value, datefmt="international").toZone('UTC').ISO(),
                [],
                '%Y/%m/%d')
    # %m/%d/%Y (US style)
    date_value = '01/11/2008'
    self.compare(DateTimeKey,
                'delivery.start_date',
                '>=%s' %date_value, 
                "((((delivery.start_date >= '%s'))))" %DateTime(date_value).toZone('UTC').ISO(),
                [],
                '%m/%d/%Y')
    # give only year value, should generate a range catching all dates
    # for respective year (converted to UTC)
    date_value = '2008'
    start_utc = DateTime('2008/01/01')
    self.compare(DateTimeKey,
                'delivery.start_date',
                '%s' %date_value, 
                "((((delivery.start_date >= '%s' AND delivery.start_date < '%s'))))" \
                  %(start_utc.toZone('UTC').ISO(), (start_utc + 366).toZone('UTC').ISO()),
                [])
    # same as above use case but adding '%' like operator
    date_value = '2118%'
    start_utc = DateTime('2118/01/01')
    self.compare(DateTimeKey,
                'delivery.start_date',
                '%s' %date_value, 
                "((((delivery.start_date >= '%s' AND delivery.start_date < '%s'))))" \
                  %(start_utc.toZone('UTC').ISO(), (start_utc + 366).toZone('UTC').ISO()),
                [])
                       
  
  def test_04FloatKey(self, quiet=quiet, run=run_all_test):
    """ Check FloatKey query generation"""
    if not run: return  
    self.compare(FloatKey, 
                'delivery.stock',
                '>10.123456', 
                "((((delivery.stock > '10.123456'))))",
                [])
    self.compare(FloatKey, 
                'delivery.stock',
                '>=10.123456', 
                "((((delivery.stock >= '10.123456'))))",
                [],) 
    self.compare(FloatKey, 
                'delivery.stock',
                '<10.123456', 
                "((((delivery.stock < '10.123456'))))",
                [])   
    self.compare(FloatKey, 
                'delivery.stock',
                '<=10.123456', 
                "((((delivery.stock <= '10.123456'))))",
                [])   
    self.compare(FloatKey, 
                'delivery.stock',
                '>=7.10 and <=10.123456', 
                "((((delivery.stock >= '7.10') AND (delivery.stock <= '10.123456'))))",
                [])
    self.compare(FloatKey, 
                'delivery.stock',
                '>7.111 or >=10.66744', 
                "((((delivery.stock > '7.111'))) OR (((delivery.stock >= '10.66744'))))",
                [])
    self.compare(FloatKey, 
                'delivery.stock',
                '>7.111 or >=10.66744', 
                "((((TRUNCATE(delivery.stock,4) > '7.111'))) OR (((TRUNCATE(delivery.stock,4) >= '10.66744'))))",
                [],
                '11.1111')                 
                
  def test_05RawKey(self, quiet=quiet, run=run_all_test):
    """ Check FullTextKey query generation"""
    if not run: return  
    self.compare(RawKey, 
                'delivery.stock',
                '1ab521ty', 
                "delivery.stock = '1ab521ty'",
                [])    
                
  def test_06FullTextKey(self, quiet=quiet, run=run_all_test):
    """ Check FullTextKey query generation"""
    if not run: return
    self.compare(FullTextKey, 
                'full_text.SearchableText',
                'john', 
                "MATCH full_text.SearchableText AGAINST ('john' )",
                ["MATCH full_text.SearchableText AGAINST ('john' ) AS full_text_SearchableText_relevance", 
                "MATCH full_text.SearchableText AGAINST ('john' ) AS SearchableText_relevance"])    
    
  def test_07ScriptableKey(self, quiet=quiet, run=run_all_test):
    """ Check ScriptableKey query generation"""
    if not run: return    
    self.compare(ScriptableKey, 
                '',
                'John Doe', 
                "((((((((((SearchableText = 'John Doe'))))) OR (((((reference = 'John Doe'))))) OR (((((title = 'John Doe'))))))))))",
                [])
    
def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestSearchKeyLexer))
  suite.addTest(unittest.makeSuite(TestSearchKeyQuery))  
  return suite
