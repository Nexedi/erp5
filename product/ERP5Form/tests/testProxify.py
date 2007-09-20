##############################################################################
#
# Copyright (c) 2007 Nexedi SARL and Contributors. All Rights Reserved.
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

from Products.Formulator.TALESField import TALESMethod
from Products.ERP5Type.Core.Folder import Folder
from Products.ERP5Form.Form import ERP5Form
from Products.ERP5Form.ProxyField import purgeFieldValueCache


class TestProxify(unittest.TestCase):

  def setUp(self):
    # base field library
    self.container = Folder('container').__of__(Folder('root'))
    self.container._setObject('Base_view',
                               ERP5Form('Base_view', 'Base'))
    base_view = self.base_view = self.container.Base_view
    base_view.manage_addField('my_string_field', 'String Field', 'StringField')
    base_view.manage_addField('my_list_field', 'List Field', 'ListField')
    base_view.my_string_field.values['display_width'] = 30
    base_view.my_list_field.values['size'] = 1

    # address view
    self.container._setObject('Address_view',
                              ERP5Form('Address_view', 'Address'))
    address_view = self.address_view = self.container.Address_view
    address_view.manage_addField('my_region', 'Country', 'StringField')
    address_view.my_region.values['size'] = 1
    address_view.my_region.tales['items'] = TALESMethod('here/portal_categories/region/getCategoryChildTitleItemList')

    # person view
    self.container._setObject('Person_view',
                               ERP5Form('Person_view', 'Person'))
    person_view = self.person_view = self.container.Person_view
    person_view.manage_addField('my_name', 'Name', 'StringField')
    person_view.manage_addField('my_default_region', 'Country', 'ListField')
    person_view.my_name.values['size'] = 20
    person_view.my_default_region.values['size'] = 1
    person_view.my_default_region.tales['items'] = TALESMethod('here/portal_categories/region/getCategoryChildTranslatedLogicalPathItemList')
    person_view.my_default_region.values['scrap_variable'] = 'obsolete'

    global request
    request = DummyRequest()

  def test_single_level_proxify(self):
    self.person_view.proxifyField({'my_name':'Base_view.my_string_field'})

    field = self.person_view.my_name
    self.assertEqual(field.meta_type, 'ProxyField')
    self.assertEqual(field.get_value('form_id'), 'Base_view')
    self.assertEqual(field.get_value('field_id'), 'my_string_field')
    self.assertEqual(field.is_delegated('title'), False)
    self.assertEqual(field.get_value('title'), 'Name')
    self.assertEqual(field.is_delegated('size'), False)
    self.assertEqual(field.get_value('size'), 20)
    self.assertEqual(field.is_delegated('enabled'), True)
    self.assertEqual(field.get_value('enabled'), 1)
    self.assertEqual(field.is_delegated('description'), True)
    self.assertEqual(field.get_value('description'), '')

    purgeFieldValueCache() # must purge cache before changing internal field value.
    template_field = self.base_view.my_string_field
    template_field.values['description'] = 'Description'
    self.assertEqual(field.get_value('description'), 'Description')

  def test_multi_level_proxify(self):
    self.address_view.proxifyField({'my_region':'Base_view.my_list_field'})
    self.person_view.proxifyField({'my_default_region':'Address_view.my_region'})

    field = self.person_view.my_default_region
    self.assertEqual(field.meta_type, 'ProxyField')
    self.assertEqual(field.get_value('form_id'), 'Address_view')
    self.assertEqual(field.get_value('field_id'), 'my_region')
    self.assertEqual(field.getTemplateField().getId(), 'my_region')
    self.assertEqual(field.getRecursiveTemplateField().getId(), 'my_list_field')
    self.assertEqual(field.is_delegated('title'), True)
    self.assertEqual(field.get_value('title'), 'Country')
    self.assertEqual(field.is_delegated('size'), True)
    self.assertEqual(field.get_value('size'), 1)
    self.assertEqual(field.is_delegated('items'), False)
    self.assertEqual(field.get_tales('items')._text,
                     'here/portal_categories/region/getCategoryChildTranslatedLogicalPathItemList')
    self.assertEqual(field.is_delegated('enabled'), True)
    self.assertEqual(field.get_value('enabled'), 1)
    self.assertEqual(field.is_delegated('description'), True)
    self.assertEqual(field.get_value('description'), '')

    self.assertEqual(field.has_value('scrap_variable'), 0)

    purgeFieldValueCache() # must purge cache before changing internal field value.
    template_field = self.address_view.my_region
    template_field.values['title'] = 'Region'
    self.assertEqual(field.get_value('title'), 'Region')

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestProxify))
  return suite
