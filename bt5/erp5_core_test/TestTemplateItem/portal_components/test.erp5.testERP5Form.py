# -*- coding: utf-8 -*-
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

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.Formulator.TALESField import TALESMethod
from Products.ERP5Type.Core.Folder import Folder
from Products.ERP5Form.Form import field_value_cache


class TestERP5Form(ERP5TypeTestCase):
  def afterSetUp(self):

    self.portal.portal_skins.custom.manage_addProduct[
      'PageTemplates'].manage_addPageTemplate(
        'Base_viewTestRenderer', 'Base_viewTestRenderer')
    self.page_template = self.portal.portal_skins.custom.Base_viewTestRenderer
    self.page_template.write('''
      <html>
        <form>
          <tal:block tal:repeat="field form/get_fields">
            <tal:block tal:replace="structure field/render" />
          </tal:block>
        </form>
      </html>
    ''')

    self.portal.portal_skins.custom.manage_addProduct['ERP5Form'].addERP5Form(
      'Base_viewTest', 'Test')
    self.form = self.portal.portal_skins.custom.Base_viewTest
    self.form.manage_addField('my_string_field', 'String Field', 'StringField')
    self.form.my_string_field.values['default'] = "test string field"

    self.form.pt = self.page_template.getId()

  def beforeTearDown(self):
    self.abort()
    for custom_skin in (self.form.getId(), self.page_template.getId(),):
      if custom_skin in self.portal.portal_skins.custom.objectIds():
        self.portal.portal_skins.custom.manage_delObjects([custom_skin])
        self.commit()

  def test_call(self):
    html = self.form()
    self.assertIn("test string field", html)

  def test_zmi(self):
    # minimal tests for custom ZMI views
    self.assertTrue(self.form.formProxify())
    self.assertTrue(self.form.formUnProxify())
    self.assertTrue(self.form.formShowRelatedProxyFields())

  def test_zmi_form_order_disabled_fields(self):
    self.assertIn('my_string_field', self.form.formOrder())
    self.form.my_string_field.values['enabled'] = False
    self.assertIn('my_string_field', self.form.formOrder())

  def test_publish_set_content_type(self):
    resp = self.publish(self.form.getPath())
    self.assertIn(b"test string field", resp.getBody())
    self.assertEqual(resp.getHeader('Content-Type'), 'text/html; charset=utf-8')


class TestProxify(ERP5TypeTestCase):

  def afterSetUp(self):
    # base field library
    self.container = Folder('container').__of__(self.portal)
    self.container.manage_addProduct['ERP5Form'].addERP5Form('Base_view', 'Base')
    base_view = self.base_view = self.container.Base_view
    base_view.manage_addField('my_string_field', 'String Field', 'StringField')
    base_view.manage_addField('my_list_field', 'List Field', 'ListField')
    base_view.manage_addField('my_relation_string_field', 'Old Relation String Field', 'RelationStringField')
    base_view.manage_addField('my_gender', 'Gender', 'ListField')
    base_view.manage_addField('my_custom_description', 'Description', 'TextAreaField')
    base_view.manage_addField('my_another_description', 'Description', 'TextAreaField')
    base_view.my_string_field.values['display_width'] = 30
    base_view.my_list_field.values['size'] = 1
    base_view.my_gender.values['items'] = [('Male', 'Male'), ('Female', 'Female')]
    base_view.my_another_description.values['editable'] = 0

    # old instance does not have recently added properties.
    del base_view.my_relation_string_field.values['proxy_listbox_ids']
    del base_view.my_relation_string_field.values['relation_form_id']

    # address view
    self.container.manage_addProduct['ERP5Form'].addERP5Form('Address_view', 'Address')
    address_view = self.address_view = self.container.Address_view
    address_view.manage_addField('my_region', 'Country', 'StringField')
    address_view.my_region.values['size'] = 1
    address_view.my_region.tales['items'] = TALESMethod('here/portal_categories/region/getCategoryChildTitleItemList')

    # person view
    self.container.manage_addProduct['ERP5Form'].addERP5Form('Person_view', 'Person')
    person_view = self.person_view = self.container.Person_view
    person_view.manage_addField('my_name', 'Name', 'StringField')
    person_view.manage_addField('my_default_region', 'Country', 'ListField')
    person_view.manage_addField('my_custom_description', 'Description', 'TextAreaField')
    person_view.manage_addField('my_custom_description2', 'Description', 'TextAreaField')
    person_view.manage_addField('my_another_description', 'Description', 'TextAreaField')
    person_view.my_name.values['display_maxwidth'] = 20
    person_view.my_default_region.values['size'] = 1
    person_view.my_default_region.tales['items'] = TALESMethod('here/portal_categories/region/getCategoryChildTranslatedLogicalPathItemList')
    person_view.my_default_region.values['scrap_variable'] = 'obsolete'
    person_view.manage_addField('my_career_subordination_title', 'Organisation', 'RelationStringField')
    person_view.my_career_subordination_title.values['base_category'] = 'subordination'
    person_view.my_career_subordination_title.values['portal_type'] = [('Organisation', 'Organisation')]
    person_view.my_career_subordination_title.values['proxy_listbox_ids'] = [('OrganisationModule_viewOrganisationList/listbox', 'Organisation')]
    person_view.my_custom_description.values['editable'] = 0
    person_view.my_another_description.values['editable'] = 0

  def test_single_level_proxify(self):
    # StringField
    self.person_view.proxifyField({'my_name':'Base_view.my_string_field'})
    field = self.person_view.my_name
    self.assertEqual(field.meta_type, 'ProxyField')
    self.assertEqual(field.get_value('form_id'), 'Base_view')
    self.assertEqual(field.get_value('field_id'), 'my_string_field')
    self.assertEqual(field.is_delegated('title'), False)
    self.assertEqual(field.get_value('title'), 'Name')
    self.assertEqual(field.is_delegated('display_maxwidth'), False)
    self.assertEqual(field.get_value('display_maxwidth'), 20)
    self.assertEqual(field.is_delegated('enabled'), True)
    self.assertEqual(field.get_value('enabled'), 1)
    self.assertEqual(field.is_delegated('description'), True)
    self.assertEqual(field.get_value('description'), '')

    field_value_cache.clear() # must purge cache before changing internal field value.
    template_field = self.base_view.my_string_field
    template_field.values['description'] = 'Description'
    self.assertEqual(field.get_value('description'), 'Description')

    field_value_cache.clear()

    # ListField
    self.person_view.manage_addField('my_gender', 'Gender', 'ListField')
    self.person_view.proxifyField({'my_gender':'Base_view.my_gender'})
    field = self.person_view.my_gender
    self.assertEqual(field.is_delegated('title'), True)
    self.assertEqual(field.get_value('title'), 'Gender')
    self.assertEqual(field.is_delegated('items'), True)
    self.assertEqual(field.get_value('items'), [('Male', 'Male'), ('Female', 'Female')])

    field_value_cache.clear()
    self.assertFalse(field.checkConsistency())

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
    self.assertTrue(field.has_value('items'))
    self.assertEqual(field.is_delegated('enabled'), True)
    self.assertEqual(field.get_value('enabled'), 1)
    self.assertEqual(field.is_delegated('description'), True)
    self.assertEqual(field.get_value('description'), '')

    self.assertEqual(field.has_value('scrap_variable'), 0)

    field_value_cache.clear() # must purge cache before changing internal field value.
    template_field = self.address_view.my_region
    template_field.values['title'] = 'Region'
    self.assertEqual(field.get_value('title'), 'Region')
    self.assertFalse(field.checkConsistency())

  def test_force_delegate(self):
    self.person_view.proxifyField({'my_name':'Base_view.my_string_field'},
                                  force_delegate=1)

    field = self.person_view.my_name
    self.assertEqual(field.meta_type, 'ProxyField')
    self.assertEqual(field.get_value('form_id'), 'Base_view')
    self.assertEqual(field.get_value('field_id'), 'my_string_field')
    self.assertEqual(field.is_delegated('title'), True)
    self.assertEqual(field.is_delegated('size'), True)
    self.assertEqual(field.is_delegated('enabled'), True)
    self.assertEqual(field.is_delegated('description'), True)
    self.assertFalse(field.checkConsistency())

  def test_keep_empty_value(self):
    #Non editable fields
    self.person_view.proxifyField({'my_custom_description': 'Base_view.my_custom_description',
                                   'my_custom_description2': 'Base_view.my_custom_description',
                                   'my_another_description': 'Base_view.my_another_description'},
                                  keep_empty_value=True)
    field = self.person_view.my_custom_description
    self.assertEqual(field.is_delegated('title'), True)
    self.assertEqual(field.get_value('title'), 'Description')
    self.assertEqual(field.is_delegated('editable'), False)
    self.assertEqual(field.get_value('editable'), 0)

    field = self.person_view.my_custom_description2
    self.assertEqual(field.is_delegated('title'), True)
    self.assertEqual(field.get_value('title'), 'Description')
    self.assertEqual(field.is_delegated('editable'), True)
    self.assertEqual(field.get_value('editable'), 1)

    field = self.person_view.my_another_description
    self.assertEqual(field.is_delegated('title'), True)
    self.assertEqual(field.get_value('title'), 'Description')
    self.assertEqual(field.is_delegated('editable'), True)
    self.assertEqual(field.get_value('editable'), 0)
    self.assertFalse(field.checkConsistency())

  def test_unproxify(self):
    #Proxify First
    self.address_view.proxifyField({'my_region':'Base_view.my_list_field'})
    self.person_view.proxifyField({'my_default_region':'Address_view.my_region'})
    field_value_cache.clear()
    #UnProxify
    self.person_view.unProxifyField({'my_default_region':'on'})
    field = self.person_view.my_default_region
    self.assertEqual(field.meta_type, 'ListField')
    self.assertEqual(field.get_value('title'), 'Country')
    self.assertEqual(field.get_tales('items')._text,
                     'here/portal_categories/region/getCategoryChildTranslatedLogicalPathItemList')

    #Test unproxify with old instance.
    #Proxify First
    self.person_view.proxifyField({'my_career_subordination_title':'Base_view.my_relation_string_field'})
    field_value_cache.clear()
    #UnProxify
    self.person_view.unProxifyField({'my_career_subordination_title':'on'})
    field = self.person_view.my_career_subordination_title
    self.assertEqual(field.meta_type, 'RelationStringField')
    self.assertEqual(field.get_value('title'), 'Organisation')
    self.assertEqual(field.get_value('proxy_listbox_ids'), [('OrganisationModule_viewOrganisationList/listbox', 'Organisation')])
    self.assertFalse(field.checkConsistency())
