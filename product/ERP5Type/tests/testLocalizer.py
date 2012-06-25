# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2012 Nexedi SA and Contributors. All Rights Reserved.
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
from Persistence import PersistentMapping

class TestLocalizer(ERP5TypeTestCase):
  def afterSetUp(self):
    self.message_catalog = self.Localizer.erp5_ui
    if 'fr' not in self.message_catalog.get_available_languages():
      self.message_catalog.add_language('fr')
    self.message_catalog._messages.clear()

  def test_non_ascii_msgid(self):
    self.assertEqual(self.portal.Base_translateString('This is 1€.', lang='fr'),
                     "This is 1€.")
    # newly created key should be unicode.
    self.assertFalse('This is 1€.' in self.message_catalog._messages)
    self.assertTrue(u'This is 1€.' in self.message_catalog._messages)
    self.message_catalog.message_edit(u'This is 1€.', 'fr', u"C'est 1€.", '')
    self.assertEqual(self.portal.Base_translateString('This is 1€.', lang='fr'),
                     "C'est 1€.")
    self.assertFalse('This is 1€.' in self.message_catalog._messages)
    self.assertTrue(u'This is 1€.' in self.message_catalog._messages)

  def test_migrated_non_ascii_msgid(self):
    # register str key to simulate existing message that was already
    # created by old Localizer.
    self.message_catalog._messages['This is 1€.'] = PersistentMapping(
      {'fr':"C'est 1€.", 'note':'',})
    self.assertEqual(self.portal.Base_translateString('This is 1€.', lang='fr'),
                     "C'est 1€.")
    # translate() should not create a unicode key if str key already exists.
    self.assertTrue('This is 1€.' in self.message_catalog._messages)
    self.assertFalse(u'This is 1€.' in self.message_catalog._messages)
    self.message_catalog.message_edit(u'This is 1€.', 'fr', u"Ceci est 1€.", '')
    self.assertEqual(self.portal.Base_translateString('This is 1€.', lang='fr'),
                     "Ceci est 1€.")
    # message_edit() should not create a unicode key if str key already exists.
    self.assertTrue('This is 1€.' in self.message_catalog._messages)
    self.assertFalse(u'This is 1€.' in self.message_catalog._messages)

  def test_non_ascii_mapping(self):
    self.assertEqual(self.portal.Base_translateString('This is 1${currency}.', lang='fr',
                                                      mapping={'currency':'€'}),
                     "This is 1€.")
    self.message_catalog.message_edit(u'This is 1${currency}.', 'fr', u"C'est 1${currency}.", '')
    self.assertEqual(self.portal.Base_translateString('This is 1${currency}.', lang='fr',
                                                      mapping={'currency':'€'}),
                     "C'est 1€.")

  def test_non_literal_mapping(self):
    self.assertEqual(self.portal.Base_translateString('This is ${obj}.', lang='fr',
                                                      mapping={'obj':[1,2]}),
                     "This is [1, 2].")
    self.message_catalog.message_edit(u'This is ${obj}.', 'fr', u"C'est ${obj}.", '')
    self.assertEqual(self.portal.Base_translateString('This is ${obj}.', lang='fr',
                                                      mapping={'obj':[1,2]}),
                     "C'est [1, 2].")

  def test_import_migrated_non_ascii_msgid(self):
    # register str key to simulate existing message that was already
    # created by old Localizer.
    self.message_catalog._messages['This is 1€.'] = PersistentMapping(
      {'fr':"C'est 1€.", 'note':'',})
    self.message_catalog.po_import(
      'fr',
      'msgid "This is 1€."\nmsgstr "Ceci est 1€."')
    self.assertEqual(self.portal.Base_translateString('This is 1€.', lang='fr'),
                     "Ceci est 1€.")
    # po_import() converts existing str key to unicode key.
    self.assertFalse('This is 1€.' in self.message_catalog._messages)
    self.assertTrue(u'This is 1€.' in self.message_catalog._messages)

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestLocalizer))
  return suite
