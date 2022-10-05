# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2013 Nexedi SA and Contributors. All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly adviced to contract a Free Software
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
# Foundation, Inc., 51 Franklin Street - Fifth Floor, Boston, MA 02110-1301, USA.
#
##############################################################################

import unittest
from unittest import expectedFailure
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase

class TestI18NSearch(ERP5TypeTestCase):
  def getTitle(self):
    return "I18N Search"

  def getBusinessTemplateList(self):
    return ('erp5_base', )

  def afterSetUp(self):
    self.person_module = self.portal.person_module
    self.person1 = self.person_module.newContent(
      portal_type='Person',
      first_name='Gabriel',
      last_name='Fauré',
      description='Quick brown fox jumps over the lazy dog.',
      )
    self.person2 = self.person_module.newContent(
      portal_type='Person',
      first_name='武者小路',
      last_name='実篤',
      description='Slow white fox jumps over the diligent dog.',
      )
    self.person3 = self.person_module.newContent(
      portal_type='Person',
      first_name='( - + )',
      last_name='',
      )
    self.tic()

  def beforeTearDown(self):
    self.person_module.manage_delObjects(ids=list(tuple(self.person_module.objectIds())))
    self.tic()

  def test_full_text_searchable_text(self):
    # check if 'é' == 'e' collation works
    result = self.person_module.searchFolder(SearchableText='Faure')
    self.assertEqual(len(result), 1)
    self.assertEqual(result[0].getPath(), self.person1.getPath())

    # check if a partial string of CJK string matches
    result = self.person_module.searchFolder(SearchableText='武者')
    self.assertEqual(len(result), 1)
    self.assertEqual(result[0].getPath(), self.person2.getPath())

    # check boolean language mode search
    result = self.person_module.searchFolder(SearchableText='+quick +fox +dog')
    self.assertEqual(len(result), 1)
    self.assertEqual(result[0].getPath(), self.person1.getPath())

    # check sort on fulltext column
    self.assertTrue('ORDER BY\n  `full_text`.`SearchableText` ASC' in self.portal.portal_catalog(SearchableText='Faure', sort_on=(('SearchableText', 'ascending'),), src__=1))

    # check sort on fulltext search score
    self.assertTrue('ORDER BY\n  full_text_SearchableText__score__ ASC' in self.portal.portal_catalog(SearchableText='Faure', sort_on=(('SearchableText__score__', 'ascending'),), src__=1))

  @expectedFailure
  def test_catalog_full_text_title(self):
    # catalog_full_text is not used by default anymore (it was already deactivated a long
    # time ago because of performance issues whene joining a full text table with a simple
    # InnoDB table, but documents were still indexed in). Thus I deactivated the catalog list
    # method in order to stop wasting resources, then this test is no use anymore.

    # check if 'é' == 'e' collation works
    result = self.person_module.searchFolder(**{'catalog_full_text.title':'Faure'})
    self.assertEqual(len(result), 1)
    self.assertEqual(result[0].getPath(), self.person1.getPath())

    # check if a partial string of CJK string matches
    result = self.person_module.searchFolder(**{'catalog_full_text.title':'武者'})
    self.assertEqual(len(result), 1)
    self.assertEqual(result[0].getPath(), self.person2.getPath())

    # check boolean language mode search
    result = self.person_module.searchFolder(**{'catalog_full_text.description':'+quick +fox +dog'})
    self.assertEqual(len(result), 1)
    self.assertEqual(result[0].getPath(), self.person1.getPath())

    # check search with a special character
    for query in ('(', ')', ):
      result = self.person_module.searchFolder(**{'catalog_full_text.title':query})
      self.assertEqual(len(result), 1)
      self.assertEqual(result[0].getPath(), self.person3.getPath())

    # check sort on fulltext column
    self.assertFalse('ORDER BY\n  title__score__ ASC' in self.portal.portal_catalog(**{
      'catalog_full_text.title':'Faure',
      'sort_on':(('catalog_full_text.title', 'ascending'),),
      'src__':1
      }))

    # check sort on fulltext search score
    self.assertTrue('ORDER BY\n  catalog_full_text_title__score__' in self.portal.portal_catalog(**{
      'catalog_full_text.title':'Faure',
      'sort_on':(('catalog_full_text.title__score__', 'ascending'),),
      'src__':1
      }))
    self.assertTrue('ORDER BY\n  catalog_full_text_title__score__' in self.portal.portal_catalog(**{
      'catalog_full_text.title':'Faure',
      'sort_on':(('title__score__', 'ascending'),),
      'src__':1
      }))

  @expectedFailure
  def test_full_text_title(self):
    # check if 'é' == 'e' collation works
    result = self.person_module.searchFolder(title='Faure')
    self.assertEqual(len(result), 1)
    self.assertEqual(result[0].getPath(), self.person1.getPath())

    # check if a partial string of CJK string matches
    result = self.person_module.searchFolder(title='武者')
    self.assertEqual(len(result), 1)
    self.assertEqual(result[0].getPath(), self.person2.getPath())

    # check boolean language mode search
    result = self.person_module.searchFolder(description='+quick +fox +dog')
    self.assertEqual(len(result), 1)
    self.assertEqual(result[0].getPath(), self.person1.getPath())

    # check search with a special character
    for query in ('(', ')', ):
      result = self.person_module.searchFolder(title=query)
      self.assertEqual(len(result), 1)
      self.assertEqual(result[0].getPath(), self.person3.getPath())

    # check fulltext search for automatically generated related keys.
    self.assertTrue('MATCH' in self.portal.portal_catalog(destination_title='Faure', src__=1))

    # check sort on fulltext column
    self.assertTrue('ORDER BY\n  `catalog`.`title` ASC' in self.portal.portal_catalog(title='Faure', sort_on=(('title', 'ascending'),), src__=1))

    # check sort on fulltext search score
    self.assertTrue('ORDER BY\n  catalog_full_text_title__score__' in self.portal.portal_catalog(title='Faure', sort_on=(('title__score__', 'ascending'),), src__=1))

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestI18NSearch))
  return suite
