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
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase

class TestI18NSearch(ERP5TypeTestCase):
  def getTitle(self):
    return "I18N Search"

  def getBusinessTemplateList(self):
    return ('erp5_full_text_mroonga_catalog',
            'erp5_base',)

  def test_full_test_search(self):
    person_module = self.portal.person_module
    person1 = person_module.newContent(
      portal_type='Person',
      first_name='Gabriel',
      last_name='Fauré',
      )
    person2 = person_module.newContent(
      portal_type='Person',
      first_name='武者小路',
      last_name='実篤'
      )
    self.tic()
    # check if 'é' == 'e' collation works
    result = person_module.searchFolder(SearchableText='Faure')
    self.assertEqual(len(result), 1)
    self.assertEqual(result[0].getPath(), person1.getPath())
    # check if a partial string of CJK string matches
    result = person_module.searchFolder(SearchableText='武者')
    self.assertEqual(len(result), 1)
    self.assertEqual(result[0].getPath(), person2.getPath())

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestI18NSearch))
  return suite
