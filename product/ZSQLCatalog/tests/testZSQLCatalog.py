##############################################################################
#
# Copyright (c) 2006 Nexedi SA and Contributors. All Rights Reserved.
#          Jerome Perrin <jerome@nexedi.com>
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
##############################################################################

import unittest
import sys

from DateTime import DateTime
from Products.ZSQLMethods.SQL import SQL as ZSQLMethod
from Products.CMFCore.Expression import Expression

from Products.ZSQLCatalog.SQLCatalog import Catalog as SQLCatalog
from Products.ZSQLCatalog.ZSQLCatalog import ZCatalog as ZSQLCatalog
from Products.ZSQLCatalog.SQLCatalog import Query
from Products.ZSQLCatalog.SQLCatalog import ComplexQuery
from Products.ZSQLCatalog.SQLCatalog import NegatedQuery


class TestZSQLCatalog(unittest.TestCase):
  """Tests for ZSQL Catalog.
  """
  def setUp(self):
    self._catalog = ZSQLCatalog()
  # TODO ?


class TestSQLCatalog(unittest.TestCase):
  """Tests for SQL Catalog.
  """
  def setUp(self):
    self._catalog = SQLCatalog('dummy_catalog')
    self._catalog._setObject('z_dummy_method',
                             ZSQLMethod('z_dummy_method', '', '', '', ''))
    self._catalog.sql_catalog_object_list = ('z_dummy_method', )

  def test_getFilterableMethodList(self):
    self.failUnless(self._catalog.z_dummy_method in
                    self._catalog.getFilterableMethodList())

  def test_manage_editFilter(self):
    request = dict(z_dummy_method_box=1, z_dummy_method_expression='python: 1')
    self._catalog.manage_editFilter(REQUEST=request)
    self.assertTrue(self._catalog.filter_dict.has_key('z_dummy_method'))

  def test_isMethodFiltered(self):
    request = dict(z_dummy_method_box=1, z_dummy_method_expression='python: 1')
    self._catalog.manage_editFilter(REQUEST=request)
    self.assertTrue(self._catalog.isMethodFiltered('z_dummy_method'))
    self.assertFalse(self._catalog.isMethodFiltered('not_exist'))

  def test_getFilterExpression(self):
    request = dict(z_dummy_method_box=1, z_dummy_method_expression='python: 1')
    self._catalog.manage_editFilter(REQUEST=request)
    self.assertEquals('python: 1', self._catalog.getExpression('z_dummy_method'))
    self.assertEquals('', self._catalog.getExpression('not_exists'))

  def test_getFilterExpressionInstance(self):
    request = dict(z_dummy_method_box=1, z_dummy_method_expression='python: 1')
    self._catalog.manage_editFilter(REQUEST=request)
    self.assertTrue(isinstance(
        self._catalog.getExpressionInstance('z_dummy_method'), Expression))
    self.assertEquals(None, self._catalog.getExpressionInstance('not_exists'))

  def test_isPortalTypeSelected(self):
    request = dict(z_dummy_method_box=1, z_dummy_method_type=['Selected'])
    self._catalog.manage_editFilter(REQUEST=request)
    self.assertTrue(
        self._catalog.isPortalTypeSelected('z_dummy_method', 'Selected'))
    self.assertFalse(
        self._catalog.isPortalTypeSelected('z_dummy_method', 'Not Selected'))
    self.assertFalse(
        self._catalog.isPortalTypeSelected('not_exists', 'Selected'))


class TestQuery(unittest.TestCase):
  """Test SQL bits generated from Queries
  """
  def testSimpleQuery(self):
    q = Query(title='Foo')
    self.assertEquals(
          dict(where_expression="((((title = 'Foo'))))",
               select_expression_list=[]),
          q.asSQLExpression(keyword_search_keys=[],
                            datetime_search_keys = [],
                            full_text_search_keys=[]))

  def testQueryMultipleKeys(self):
    # using multiple keys is invalid and raises
    # KeyError: 'Query must have only one key'
    self.assertRaises(KeyError, Query, title='Foo', reference='bar')

  def testNoneQuery(self):
    q = Query(title=None)
    self.assertEquals(
          dict(where_expression="title is NULL",
               select_expression_list=[]),
          q.asSQLExpression(keyword_search_keys=[], 
                            datetime_search_keys = [],
                            full_text_search_keys=[]))

  def testEmptyQueryNotIgnoreEmptyString(self):
    q = Query(title='')
    # if you want to search with an empty string, pass ignore_empty_string=0 to
    # asSQLExpression. XXX not to __init__ ?
    self.assertEquals(
          dict(where_expression="title = ''",
               select_expression_list=[]),
          q.asSQLExpression(ignore_empty_string=0,
                            keyword_search_keys=[],
                            datetime_search_keys = [],
                            full_text_search_keys=[]))

  def testEmptyQuery(self):
    q = Query(title='')
    # query are true by default
    self.assertEquals(
          dict(where_expression="1",
               select_expression_list=[]),
          q.asSQLExpression(keyword_search_keys=[], 
                            datetime_search_keys = [],
                            full_text_search_keys=[]))
    
  def testMultiValuedQuery(self):
    q = Query(title=['Foo', 'Bar'])
    self.assertEquals(
          dict(where_expression="(((((title = 'Foo')))) OR ((((title = 'Bar')))))",
               select_expression_list=[]),
          q.asSQLExpression(keyword_search_keys=[], 
                            datetime_search_keys = [],
                            full_text_search_keys=[]))

  def testINQuery(self):
    q = Query(title=['Foo', 'Bar'], operator='IN')
    self.assertEquals(
          dict(where_expression="title IN ('Foo', 'Bar')",
               select_expression_list=[]),
          q.asSQLExpression(keyword_search_keys=[], 
                            datetime_search_keys = [],
                            full_text_search_keys=[]))

  def testEmptyINQuery(self):
    q = Query(title=[], operator='IN')
    self.assertEquals(
          dict(where_expression="0",
               select_expression_list=[]),
          q.asSQLExpression(keyword_search_keys=[],
                            datetime_search_keys = [],
                            full_text_search_keys=[]))

  def testMinQuery(self):
    q = Query(title='Foo', range='min')
    self.assertEquals(
          dict(where_expression="title >= 'Foo'",
               select_expression_list=[]),
          q.asSQLExpression(keyword_search_keys=[], 
                            datetime_search_keys = [],
                            full_text_search_keys=[]))
    
  def testMaxQuery(self):
    q = Query(title='Foo', range='max')
    self.assertEquals(
          dict(where_expression="title < 'Foo'",
               select_expression_list=[]),
          q.asSQLExpression(keyword_search_keys=[], 
                            datetime_search_keys = [],
                            full_text_search_keys=[]))

  # format
  def testDateFormat(self):
    date = DateTime(2001, 02, 03)
    q = Query(date=date, format='%Y/%m/%d', type='date')
    self.assertEquals(
          dict(where_expression=
            "((((date >= '%s' AND date < '%s'))))" \
                 %(date.toZone('UTC').ISO(), (date + 1).toZone('UTC').ISO()),
               select_expression_list=[]),
          q.asSQLExpression(keyword_search_keys=[], 
                            datetime_search_keys = [],
                            full_text_search_keys=[]))
  
  # full text
  def testSimpleQueryFullText(self):
    q = Query(title='Foo')
    self.assertEquals(dict(where_expression="MATCH title AGAINST ('Foo' )",
                           select_expression_list=
                        ["MATCH title AGAINST ('Foo' ) AS title_relevance"]),
          q.asSQLExpression(keyword_search_keys=[],
                            datetime_search_keys = [],
                            full_text_search_keys=['title']))

  def testSimpleQueryFullTextSearchMode(self):
    q = Query(title='Foo',
              search_mode='in_boolean_mode')
    self.assertEquals(dict(
      where_expression="MATCH title AGAINST ('Foo' IN BOOLEAN MODE)",
      select_expression_list=
        ["MATCH title AGAINST ('Foo' IN BOOLEAN MODE) AS title_relevance"]),
          q.asSQLExpression(keyword_search_keys=[],
                            datetime_search_keys = [],
                            full_text_search_keys=['title']))
  
  def testSimpleQueryFullAutomaticTextSearchMode(self):
    q = Query(title='Foo*',)
    self.assertEquals(dict(
      where_expression="MATCH title AGAINST ('Foo*' IN BOOLEAN MODE)",
      select_expression_list=
        ["MATCH title AGAINST ('Foo*' IN BOOLEAN MODE) AS title_relevance"]),
          q.asSQLExpression(full_text_search_keys=['title']))

  def testSimpleQueryFullTextStat__(self):
    # stat__ is an internal implementation artifact to prevent adding
    # select_expression for countFolder
    q = Query(title='Foo')
    self.assertEquals(dict(
                    where_expression="MATCH title AGAINST ('Foo' )",
                    select_expression_list=[]),
          q.asSQLExpression(keyword_search_keys=[],
                            datetime_search_keys = [],
                            full_text_search_keys=['title'],
                            stat__=1))

  def testSimpleQueryKeywordSearchKey(self):
    q = Query(title='Foo')
    self.assertEquals(dict(where_expression="((((title LIKE '%Foo%'))))",
                           select_expression_list=[]),
          q.asSQLExpression(keyword_search_keys=['title'],
                            datetime_search_keys = [],
                            full_text_search_keys=[]))

  def testQueryKeywordSearchKeyWithPercent(self):
    q = Query(title='Fo%oo')
    self.assertEquals(dict(where_expression="((((title LIKE 'Fo%oo'))))",
                           select_expression_list=[]),
          q.asSQLExpression(keyword_search_keys=['title'],))

  def testQueryKeywordSearchKeyWithPercentAndOnlyOneLetter(self):
    q = Query(title='F%o')
    self.assertEquals(dict(where_expression="((((title LIKE 'F%o'))))",
                           select_expression_list=[]),
          q.asSQLExpression(keyword_search_keys=['title']))

  def testQueryKeywordSearchKeyWithPercentOnly(self):
    q = Query(title='%')
    self.assertEquals(dict(where_expression="((((title LIKE '%'))))",
                           select_expression_list=[]),
          q.asSQLExpression(keyword_search_keys=['title'],))

  def testQueryKeywordSearchKeyWithMinus(self):
    q = Query(title='F-o')
    self.assertEquals(dict(where_expression="((((title LIKE '%F-o%'))))",
                           select_expression_list=[]),
          q.asSQLExpression(keyword_search_keys=['title'],
                            datetime_search_keys = [],
                            full_text_search_keys=[]))

  def testQueryKeywordSearchKeyWithSpace(self):
    q = Query(title='F o')
    self.assertEquals(dict(where_expression="((((title LIKE '%F o%'))))",
                           select_expression_list=[]),
          q.asSQLExpression(keyword_search_keys=['title'],
                            datetime_search_keys = [],
                            full_text_search_keys=[]))

  def testQueryKeywordSearchKeyWithPercentAtTheEnd(self):
    q = Query(title='F%')
    self.assertEquals(dict(where_expression="((((title LIKE 'F%'))))",
                           select_expression_list=[]),
          q.asSQLExpression(keyword_search_keys=['title'],))
    q = Query(title='Fo%')
    self.assertEquals(dict(where_expression="((((title LIKE 'Fo%'))))",
                           select_expression_list=[]),
          q.asSQLExpression(keyword_search_keys=['title'],))

  def testQueryKeywordSearchKeyWithPercentAtTheBeginning(self):
    q = Query(title='%o')
    self.assertEquals(dict(where_expression="((((title LIKE '%o'))))",
                           select_expression_list=[]),
          q.asSQLExpression(keyword_search_keys=['title'],))
    q = Query(title='%oo')
    self.assertEquals(dict(where_expression="((((title LIKE '%oo'))))",
                           select_expression_list=[]),
          q.asSQLExpression(keyword_search_keys=['title'],))

  def testNegatedQuery(self):
    q1 = Query(title='Foo')
    q = NegatedQuery(q1)
    self.assertEquals(
        dict(where_expression="(NOT (((((title = 'Foo'))))))",
                           select_expression_list=[]),
          q.asSQLExpression(keyword_search_keys=[],
                            datetime_search_keys = [],
                            full_text_search_keys=[]))

  # complex queries
  def testSimpleComplexQuery(self):
    q1 = Query(title='Foo')
    q2 = Query(reference='Bar')
    q = ComplexQuery(q1, q2)
    self.assertEquals(
        dict(where_expression="((((((title = 'Foo'))))) AND (((((reference = 'Bar'))))))",
                           select_expression_list=[]),
          q.asSQLExpression(keyword_search_keys=[],
                            datetime_search_keys = [],
                            full_text_search_keys=[]))

  def testNegatedComplexQuery(self):
    q1 = Query(title='Foo')
    q2 = Query(reference='Bar')
    q3 = ComplexQuery(q1, q2)
    q = NegatedQuery(q3)
    self.assertEquals(
      # maybe too many parents here
     dict(where_expression="(NOT (((((((title = 'Foo'))))) AND (((((reference = 'Bar'))))))))",
          select_expression_list=[]),
     q.asSQLExpression(keyword_search_keys=[],
                       datetime_search_keys = [],
                       full_text_search_keys=[]))

  
  # forced keys
  def testSimpleQueryForcedKeywordSearchKey(self):
    q = Query(title='Foo', key='Keyword')
    self.assertEquals("((((title LIKE '%Foo%'))))",
          q.asSQLExpression(keyword_search_keys=[],
                            datetime_search_keys = [],
                            full_text_search_keys=[])['where_expression'])

  def testSimpleQueryForcedFullText(self):
    q = Query(title='Foo', key='FullText')
    self.assertEquals("MATCH title AGAINST ('Foo' )",
          q.asSQLExpression(keyword_search_keys=[],
                            datetime_search_keys = [],                            
                            full_text_search_keys=[])['where_expression'])

  def testSimpleQueryForcedExactMatch(self):
    q = Query(title='Foo', key='ExactMatch')
    self.assertEquals("title = 'Foo'",
          q.asSQLExpression(keyword_search_keys=['title'],
                            datetime_search_keys = [],  
                            full_text_search_keys=[])['where_expression'])

  def testSimpleQueryForcedExactMatchOR(self):
    q = Query(title='Foo% OR %?ar', key='ExactMatch')
    self.assertEquals("title = 'Foo% OR %?ar'",
          q.asSQLExpression(keyword_search_keys=['title'],
                            datetime_search_keys = [],
                            full_text_search_keys=[])['where_expression'])

  def testQuotedStringDefaultKey(self):
    q = Query(title='Foo d\'Ba')
    self.assertEquals(
              dict(where_expression="((((title = 'Foo d''Ba'))))",
                   select_expression_list=[]),
                q.asSQLExpression())

  def testQuotedStringKeywordKey(self):
    q = Query(title='Foo d\'Ba', type='keyword')
    self.assertEquals(
              dict(where_expression="((((title LIKE '%Foo d''Ba%'))))",
                   select_expression_list=[]),
                q.asSQLExpression())

  def testQuotedStringFullTextKey(self):
    q = Query(title='Foo d\'Ba', type='fulltext')
    self.assertEquals(
        dict(where_expression="MATCH title AGAINST ('Foo d''Ba' )",
             select_expression_list=["MATCH title AGAINST ('Foo d''Ba' )"
                                     " AS title_relevance"]),
          q.asSQLExpression())

  def testQuotedStringDateKey(self):
    q = Query(title='Foo d\'Ba', type='date')
    self.assertEquals(
        # I don't know exactly what we should expect here.
              dict(where_expression="1",
                   select_expression_list=[]),
                q.asSQLExpression())

  def testQuotedStringFloatKey(self):
    q = Query(title='Foo d\'Ba', type='float')
    self.assertEquals(
        # I don't know exactly what we should expect here.
        # At least it's safe.
              dict(where_expression="1",
                   select_expression_list=[]),
                q.asSQLExpression())

  def testQuotedStringIntKey(self):
    q = Query(title='Foo d\'Ba', type='int')
    self.assertEquals(
              dict(where_expression="((((title = 'Foo d''Ba'))))",
                   select_expression_list=[]),
                q.asSQLExpression())


def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestSQLCatalog))
  suite.addTest(unittest.makeSuite(TestZSQLCatalog))
  suite.addTest(unittest.makeSuite(TestQuery))
  return suite

