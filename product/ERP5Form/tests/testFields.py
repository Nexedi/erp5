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

import unittest

# Load monkey patches
from Testing import ZopeTestCase
ZopeTestCase.installProduct('ERP5Form')

from Products.Formulator.StandardFields import FloatField
from Products.Formulator.StandardFields import StringField
from Products.Formulator.TALESField import TALESMethod


class TestFloatField(unittest.TestCase):
  """Tests Float field
  """
  def setUp(self):
    self.field = FloatField('test_field')
    self.widget = self.field.widget

  def test_format_thousand_separator(self):
    self.field.values['input_style'] = '-1 234.5'
    self.assertEquals('1 000.0', self.widget.format_value(self.field, 1000))

  def test_format_percent_style(self):
    self.field.values['input_style'] = '-12.3%'
    self.assertEquals('10.0%', self.widget.format_value(self.field, 0.1))

  def test_format_precision(self):
    self.field.values['precision'] = 0
    self.assertEquals('12', self.widget.format_value(self.field, 12.34))

    self.field.values['precision'] = 2
    self.assertEquals('0.01', self.widget.format_value(self.field, 0.011))
    # value is rounded
    self.assertEquals('0.01', self.widget.format_value(self.field, 0.009999))

  def test_render_view(self):
    self.field.values['input_style'] = '-1 234.5'
    self.field.values['precision'] = 2
    self.field.values['editable'] = 0
    self.assertEquals('1&nbsp;000.00', self.field.render(1000))

  def test_render_big_numbers(self):
    self.field.values['precision'] = 2
    self.field.values['editable'] = 0
    self.assertEquals('10000000000000000000.00',
                      self.field.render(10000000000000000000))


class TestStringField(unittest.TestCase):
  """Tests string field
  """
  def setUp(self):
    self.field = StringField('test_field')
    self.widget = self.field.widget

  def test_escape_html(self):
    self.field.values['editable'] = 0
    self.assertEquals('&lt;script&gt;', self.field.render("<script>"))


def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestFloatField))
  suite.addTest(unittest.makeSuite(TestStringField))
  return suite

