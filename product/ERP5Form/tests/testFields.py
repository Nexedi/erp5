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

# Make it possible to use Globals.get_request
class DummyRequest(dict):
  def set(self, k, v):
    self[k] = v

global request
request = DummyRequest()

def get_request():
  global request
  return request

# apply patch (before it's imported by other modules)
import Globals
Globals.get_request = get_request


# Initialize ERP5Form Product to load monkey patches
from Testing import ZopeTestCase
ZopeTestCase.installProduct('ERP5Form')

from Products.Formulator.StandardFields import FloatField
from Products.Formulator.StandardFields import StringField

from Products.ERP5Type.Core.Folder import Folder
from Products.ERP5Form.Form import ERP5Form


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
  
  def test_render_string_value(self):
    self.field.values['precision'] = 2
    self.field.values['editable'] = 0
    self.assertEquals('12.34', self.field.render("12.34"))
    self.assertEquals('not float', self.field.render("not float"))

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


class TestProxyField(unittest.TestCase):
  def setUp(self):
    self.container = Folder('container').__of__(Folder('root'))
    self.container._setObject('Base_viewProxyFieldLibrary',
                               ERP5Form('Base_viewProxyFieldLibrary', 'Proxys'))
    self.container._setObject('Base_view',
                               ERP5Form('Base_view', 'View'))
    global request
    request = DummyRequest()

  def test_get_template_field(self):
    self.container.Base_viewProxyFieldLibrary.manage_addField(
                        'my_title', 'Title', 'StringField')
    original_field = self.container.Base_viewProxyFieldLibrary.my_title
    self.container.Base_view.manage_addField(
                      'my_title', 'Not Title', 'ProxyField')
    proxy_field = self.container.Base_view.my_title
    proxy_field.manage_edit_xmlrpc(dict(form_id='Base_viewProxyFieldLibrary',
                                        field_id='my_title',))
    self.assertEquals(original_field, proxy_field.getTemplateField())

  def test_simple_surcharge(self):
    self.container.Base_viewProxyFieldLibrary.manage_addField(
                        'my_title', 'Title', 'StringField')
    original_field = self.container.Base_viewProxyFieldLibrary.my_title
    self.assertEquals('Title', original_field.get_value('title'))

    self.container.Base_view.manage_addField(
                      'my_title', 'Not Title', 'ProxyField')
    proxy_field = self.container.Base_view.my_title
    proxy_field.manage_edit_xmlrpc(dict(form_id='Base_viewProxyFieldLibrary',
                                        field_id='my_title',))
    self.assert_(proxy_field.is_delegated('title'))
    self.assertEquals('Title', proxy_field.get_value('title'))

  def test_get_value_default(self):
    # If the proxy field is named 'my_id', it will get 'id'
    # property on the context, regardless of the id of the proxified field
    self.container.Base_viewProxyFieldLibrary.manage_addField(
                        'my_title', 'Title', 'StringField')
    original_field = self.container.Base_viewProxyFieldLibrary.my_title

    self.container.Base_view.manage_addField(
                      'my_id', 'ID', 'ProxyField')
    proxy_field = self.container.Base_view.my_id
    proxy_field.manage_edit_xmlrpc(dict(form_id='Base_viewProxyFieldLibrary',
                                        field_id='my_title',))
    self.assertEquals('container', self.container.getId())
    self.assertEquals('container', proxy_field.get_value('default'))

  def test_tales_context(self):
    # in the TALES context, "field" will be the proxyfield, not the original
    # field.
    self.container.Base_viewProxyFieldLibrary.manage_addField(
                        'my_title', 'Title', 'StringField')
    original_field = self.container.Base_viewProxyFieldLibrary.my_title
    original_field.manage_tales_xmlrpc(dict(title='field/getId'))
    self.assertEquals('my_title', original_field.get_value('title'))

    self.container.Base_view.manage_addField(
                      'my_reference', 'Not Title', 'ProxyField')
    proxy_field = self.container.Base_view.my_reference
    proxy_field.manage_edit_xmlrpc(dict(form_id='Base_viewProxyFieldLibrary',
                                        field_id='my_title',))
    # 'my_reference' is the ID of the proxy field
    self.assertEquals('my_reference', proxy_field.get_value('title'))



def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestFloatField))
  suite.addTest(unittest.makeSuite(TestStringField))
  suite.addTest(unittest.makeSuite(TestProxyField))
  return suite

