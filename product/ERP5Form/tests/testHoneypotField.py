# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2007 Nexedi SARL and Contributors. All Rights Reserved.
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

# TODO: Some tests from this file can be merged into Formulator

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
import unittest
from Products.Formulator.Validator import ValidationError
from Products.ERP5Form import HoneypotField
from Products.Formulator.StandardFields import FloatField

class TestHoneypotField(ERP5TypeTestCase):
  """Tests Honeypot field
  """

  def getTitle(self):
    return "Honeypot Field"

  def afterSetUp(self):
    self.field = HoneypotField.HoneypotField('test_field')
    self.widget = self.field.widget
    self.validator = self.field.validator

  def test_raise_error_when_no_value_submit(self):
    self.assertRaises(ValidationError,
      self.validator.validate, self.field, 'field_test_field',
      self.portal.REQUEST)

  def test_raise_error_when_no_default_value_submit(self):
    self.portal.REQUEST.set('field_test_field', 'test')
    self.assertRaises(ValidationError,
      self.validator.validate, self.field, 'field_test_field',
      self.portal.REQUEST)
   
  def test_ok_when_default_value_submit(self):
     self.field.values['default'] = 'test'
     self.portal.REQUEST.set('field_test_field', 'test')
     self.assertEqual('test', self.validator.validate(self.field, 'field_test_field',
     self.portal.REQUEST))

     self.field.values['default'] = ''
     self.portal.REQUEST.set('field_test_field', '')
     self.assertEqual('', self.validator.validate(self.field, 'field_test_field',
     self.portal.REQUEST))

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestHoneypotField))
  return suite
