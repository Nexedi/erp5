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
  __allow_access_to_unprotected_subobjects__ = 1
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
from Products.Formulator.MethodField import Method
from Products.Formulator.TALESField import TALESMethod

from Products.ERP5Type.Core.Folder import Folder
from Products.ERP5Form.Form import ERP5Form
from Products.ERP5Form.Form import purgeFieldValueCache
from Products.ERP5Form.Form import getFieldValue
from Products.ERP5Form import Form
from Products.ERP5Form import ProxyField


class TestFloatField(unittest.TestCase):
  """Tests Float field
  """

  def getTitle(self):
    return "Float Field"

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

    purgeFieldValueCache() # call this before changing internal field values.
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

  def getTitle(self):
    return "String Field"

  def setUp(self):
    self.field = StringField('test_field')
    self.widget = self.field.widget

  def test_escape_html(self):
    self.field.values['editable'] = 0
    self.assertEquals('&lt;script&gt;', self.field.render("<script>"))


class TestProxyField(unittest.TestCase):

  def getTitle(self):
    return "Proxy Field"

  def setUp(self):
    self.container = Folder('container').__of__(Folder('root'))
    self.container._setObject('Base_viewProxyFieldLibrary',
                               ERP5Form('Base_viewProxyFieldLibrary', 'Proxys'))
    self.container._setObject('Base_view',
                               ERP5Form('Base_view', 'View'))
    global request
    request = DummyRequest()
    self.container.REQUEST = request

  def addField(self, form, id, title, field_type):
    form.manage_addField(id, title, field_type)
    field = getattr(form, id)
    field._p_oid = makeDummyOid()
    return field

  def test_get_template_field(self):
    original_field = self.addField(self.container.Base_viewProxyFieldLibrary,
                                   'my_title', 'Title', 'StringField')
    proxy_field = self.addField(self.container.Base_view,
                                'my_title', 'Not Title', 'ProxyField')
    self.assertEquals(None, proxy_field.getTemplateField())
    self.assertEquals(None, proxy_field.get_value('enable'))
    self.assertEquals(None, proxy_field.get_value('default'))

    proxy_field.manage_edit_xmlrpc(dict(form_id='Base_viewProxyFieldLibrary',
                                        field_id='my_title',))
    self.assertEquals(original_field, proxy_field.getTemplateField())

  def test_simple_surcharge(self):
    original_field = self.addField(self.container.Base_viewProxyFieldLibrary,
                                   'my_title', 'Title', 'StringField')
    self.assertEquals('Title', original_field.get_value('title'))

    proxy_field = self.addField(self.container.Base_view,
                                'my_title', 'Not Title', 'ProxyField')
    proxy_field.manage_edit_xmlrpc(dict(form_id='Base_viewProxyFieldLibrary',
                                        field_id='my_title',))
    self.assert_(proxy_field.is_delegated('title'))
    self.assertEquals('Title', proxy_field.get_value('title'))

  def test_simple_not_surcharge(self):
    original_field = self.addField(self.container.Base_viewProxyFieldLibrary,
                                   'my_title', 'Title', 'StringField')
    self.assertEquals('Title', original_field.get_value('title'))

    proxy_field = self.addField(self.container.Base_view,
                                'my_title', 'Proxy Title', 'ProxyField')
    proxy_field.manage_edit_xmlrpc(dict(form_id='Base_viewProxyFieldLibrary',
                                        field_id='my_title',))
    # XXX no API for this ?
    proxy_field._surcharged_edit(dict(title='Proxy Title'), ['title'])

    self.failIf(proxy_field.is_delegated('title'))
    self.assertEquals('Proxy Title', proxy_field.get_value('title'))

  def test_get_value_default(self):
    # If the proxy field is named 'my_id', it will get 'id'
    # property on the context, regardless of the id of the proxified field
    original_field = self.addField(self.container.Base_viewProxyFieldLibrary,
                                   'my_title', 'Title', 'StringField')
    proxy_field = self.addField(self.container.Base_view,
                                'my_id', 'ID', 'ProxyField')
    proxy_field.manage_edit_xmlrpc(dict(form_id='Base_viewProxyFieldLibrary',
                                        field_id='my_title',))
    self.assertEquals('container', self.container.getId())
    self.assertEquals('container', proxy_field.get_value('default'))

  def test_field_tales_context(self):
    # in the TALES context, "field" will be the proxyfield, not the original
    # field.
    original_field = self.addField(self.container.Base_viewProxyFieldLibrary,
                                   'my_title', 'Title', 'StringField')
    original_field.manage_tales_xmlrpc(dict(title='field/getId'))
    self.assertEquals('my_title', original_field.get_value('title'))

    proxy_field = self.addField(self.container.Base_view,
                                'my_reference', 'Not Title', 'ProxyField')
    proxy_field.manage_edit_xmlrpc(dict(form_id='Base_viewProxyFieldLibrary',
                                        field_id='my_title',))
    # 'my_reference' is the ID of the proxy field
    self.assertEquals('my_reference', proxy_field.get_value('title'))

  def test_form_tales_context(self):
    # in the TALES context, "form" will be the form containing the proxyfield,
    # not the original form (ie. the field library).
    original_field = self.addField(self.container.Base_viewProxyFieldLibrary,
                                   'my_title', 'Title', 'StringField')
    original_field.manage_tales_xmlrpc(dict(title='form/getId'))
    self.assertEquals('Base_viewProxyFieldLibrary',
                       original_field.get_value('title'))

    proxy_field = self.addField(self.container.Base_view,
                                'my_title', 'Title', 'ProxyField')
    proxy_field.manage_edit_xmlrpc(dict(form_id='Base_viewProxyFieldLibrary',
                                        field_id='my_title',))
    self.assertEquals('Base_view', proxy_field.get_value('title'))

  def test_get_value_cache_on_TALES_target(self):
    # If the proxy field defines its target using TALES, then no caching should
    # happen.
    original_field = self.addField(self.container.Base_viewProxyFieldLibrary,
                                   'my_title', 'Title', 'StringField')
    other_field = self.addField(self.container.Base_viewProxyFieldLibrary,
                                   'my_other_field', 'Other', 'StringField')
    proxy_field = self.addField(self.container.Base_view,
                                'my_id', 'ID', 'ProxyField')
    proxy_field.manage_edit_xmlrpc(dict(form_id='Base_viewProxyFieldLibrary'))
    proxy_field.manage_tales_xmlrpc(dict(field_id='request/field_id'))

    self.container.REQUEST.set('field_id', 'my_title')
    self.assertEquals(original_field, proxy_field.getTemplateField())
    self.assertEquals('Title', proxy_field.get_value('title'))

    self.container.REQUEST.set('field_id', 'my_other_field')
    self.assertEquals(other_field, proxy_field.getTemplateField())
    self.assertEquals('Other', proxy_field.get_value('title'))


class TestFieldValueCache(unittest.TestCase):
  """Tests field value caching system
  """

  def getTitle(self):
    return "Field Value Cache"

  def setUp(self):
    self.root = Folder('root')
    self.root.form = ERP5Form('form', 'Form')

    form = self.root.form
    form.field = StringField('test_field')
    form.field._p_oid = makeDummyOid()
    # method field
    form.field.values['external_validator'] = Method('this_is_a_method')
    # on-memory field (not in zodb)
    form.on_memory_field = StringField('test_on_memory_field')
    form.on_memory_field._p_oid = None
    # proxy field
    form.proxy_field = ProxyField.ProxyField('test_proxy_field')
    form.proxy_field._p_oid = makeDummyOid()
    form.proxy_field.values['form_id'] = 'form'
    form.proxy_field.values['field_id'] = 'field'
    # proxy field with tales
    form.proxy_field_tales = ProxyField.ProxyField('test_proxy_field')
    form.proxy_field_tales._p_oid = makeDummyOid()
    form.proxy_field_tales.tales['form_id'] = TALESMethod('string:form')
    form.proxy_field_tales.tales['field_id'] = TALESMethod('string:field')

  def test_method_field(self):
    field = self.root.form.field
    value = getFieldValue(field, field, 'external_validator')
    self.assertEqual(False, value.value is field.values['external_validator'])
    self.assertEqual(True, type(value.value) is Method)

  def test_using_cache_or_not(self):
    # check standard field in zodb
    # make sure that this will use cache.
    cache_size = len(Form._field_value_cache)
    self.root.form.field.get_value('title')
    self.assertEqual(True, cache_size < len(Form._field_value_cache))

    # check on-memory field
    # make sure that this will not use cache.
    cache_size = len(Form._field_value_cache)
    self.root.form.on_memory_field.get_value('title')
    self.assertEqual(True, cache_size == len(Form._field_value_cache))

    # check proxy field
    # make sure that this will use cache.
    cache_size = len(ProxyField._field_value_cache)
    self.root.form.proxy_field.get_value('title')
    self.assertEqual(True, cache_size < len(ProxyField._field_value_cache))

    # check proxy field with tales
    # make sure that this will not use cache.
    cache_size = len(ProxyField._field_value_cache)
    self.root.form.proxy_field_tales.get_value('title')
    self.assertEqual(True, cache_size == len(ProxyField._field_value_cache))


def makeDummyOid():
  import time, random
  return '%s%s' % (time.time(), random.random())


def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestFloatField))
  suite.addTest(unittest.makeSuite(TestStringField))
  suite.addTest(unittest.makeSuite(TestProxyField))
  suite.addTest(unittest.makeSuite(TestFieldValueCache))
  return suite
