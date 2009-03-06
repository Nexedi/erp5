##############################################################################
# -*- coding: utf-8 -*-
# Copyright (c) 2007 Nexedi SA and Contributors. All Rights Reserved.
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
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Form.Selection import Selection
from Testing import ZopeTestCase
from Products.ERP5OOo.tests.utils import Validator

HTTP_OK = 200

# setting this to a true value allow the use of a debugger
debug = 0

class TestOOoStyle(ERP5TypeTestCase, ZopeTestCase.Functional):
  """Tests ODF styles for ERP5."""
  skin = None
  content_type = None

  def getBusinessTemplateList(self):
    return ('erp5_base', 'erp5_ods_style', 'erp5_odt_style',)

  def afterSetUp(self):
    if not self.skin:
      raise NotImplementedError('Subclasses must define skin')
    
    self.auth = 'ERP5TypeTestCase:'
    person_module = self.portal.person_module
    if person_module._getOb('pers', None) is None:
      person_module.newContent(id='pers', portal_type='Person')
      get_transaction().commit()
      self.tic()
    person_module.pers.setFirstName('Bob')
    if person_module.pers._getOb('img', None) is None:
      person_module.pers.newContent(portal_type='Image', id='img')
    self.portal.changeSkin(self.skin)
    self.validator = Validator()
    # make sure selections are empty
    self.portal.portal_selections.setSelectionFor(
                        'person_module_selection', Selection())

  if debug:
    def publish(self, path, basic=None, **kw):
      kw['handle_errors'] = False
      return ZopeTestCase.Functional.publish(self, path, basic, **kw)

  def _validate(self, odf_file_data):
    error_list = self.validator.validate(odf_file_data)
    if error_list:
      self.fail(''.join(error_list))
  
  def _assertFieldInGroup(self, field_type, form_id, group):
    for f in self.portal[form_id].get_fields_in_group(group):
      if f.meta_type == 'ProxyField':
        if f.getRecursiveTemplateField().meta_type == field_type:
          break
      if f.meta_type == field_type:
        break
    else:
      self.fail('No %s found in %s (%s group)' % (field_type, form_id, group))

  def test_skin_selection(self):
    self.assertTrue(self.skin in
              self.portal.portal_skins.getSkinSelections())

  def test_form_list(self):
    response = self.publish(
                   '/%s/person_module/PersonModule_viewPersonList'
                    % self.portal.getId(), self.auth)
    self.assertEquals(HTTP_OK, response.getStatus())
    content_type = response.getHeader('content-type')
    self.assertTrue(content_type.startswith(self.content_type), content_type)
    content_disposition = response.getHeader('content-disposition')
    self.assertEquals('inline', content_disposition.split(';')[0])
    self._validate(response.getBody())

  def test_form_list_domain_tree(self):
    self.portal.portal_selections.setListboxDisplayMode(
                  self.portal.REQUEST, 'DomainTreeMode',
                  'person_module_selection')
    # XXX no proper API on selection / selection tool for this ?
    self.portal.portal_selections.setSelectionParamsFor(
                  selection_name='person_module_selection',
                  params=dict(domain_path='portal_categories',
                              domain_url='group',
                              domain_list=()))
    response = self.publish(
                   '/%s/person_module/PersonModule_viewPersonList'
                    % self.portal.getId(), self.auth)
    self.assertEquals(HTTP_OK, response.getStatus())
    content_type = response.getHeader('content-type')
    self.assertTrue(content_type.startswith(self.content_type), content_type)
    content_disposition = response.getHeader('content-disposition')
    self.assertEquals('inline', content_disposition.split(';')[0])
    self._validate(response.getBody())

  def test_form_view(self):
    # form_view on a form without listbox
    self.portal.person_module.pers.setDefaultAddressZipCode(59000)
    response = self.publish(
        '/%s/person_module/pers/default_address/GeographicAddress_view'
        % self.portal.getId(), self.auth)
    self.assertEquals(HTTP_OK, response.getStatus())
    content_type = response.getHeader('content-type')
    self.assertTrue(content_type.startswith(self.content_type), content_type)
    content_disposition = response.getHeader('content-disposition')
    self.assertEquals('inline', content_disposition.split(';')[0])
    self._validate(response.getBody())

  def test_form_view_empty_listbox(self):
    # form_view on a form with an empty listbox
    if hasattr(self.portal.person_module.pers, 'default_address'):
      self.portal.person_module.pers._delObject('default_address')
    response = self.publish(
                   '/%s/person_module/pers/Person_view'
                   % self.portal.getId(), self.auth)
    self.assertEquals(HTTP_OK, response.getStatus())
    content_type = response.getHeader('content-type')
    self.assertTrue(content_type.startswith(self.content_type), content_type)
    content_disposition = response.getHeader('content-disposition')
    self.assertEquals('inline', content_disposition.split(';')[0])
    self._validate(response.getBody())

  def test_form_view_non_empty_listbox(self):
    self.portal.person_module.pers.setDefaultAddressZipCode(59000)
    response = self.publish(
                   '/%s/person_module/pers/Person_view'
                   % self.portal.getId(), self.auth)
    self.assertEquals(HTTP_OK, response.getStatus())
    content_type = response.getHeader('content-type')
    self.assertTrue(content_type.startswith(self.content_type), content_type)
    content_disposition = response.getHeader('content-disposition')
    self.assertEquals('inline', content_disposition.split(';')[0])
    self._validate(response.getBody())

  def test_form_view_format(self):
    # empty format= does not uses oood for conversion
    response = self.publish(
                   '/%s/person_module/pers/Person_view?format='
                   % self.portal.getId(), self.auth)
    self.assertEquals(HTTP_OK, response.getStatus())
    content_type = response.getHeader('content-type')
    self.assertTrue(content_type.startswith(self.content_type), content_type)
    content_disposition = response.getHeader('content-disposition')
    self.assertEquals('inline', content_disposition.split(';')[0])
    self._validate(response.getBody())

  def test_report_view(self):
    response = self.publish(
                   '/%s/person_module/pers/Base_viewHistory'
                    % self.portal.getId(), self.auth)
    self.assertEquals(HTTP_OK, response.getStatus())
    content_type = response.getHeader('content-type')
    self.assertTrue(content_type.startswith(self.content_type), content_type)
    content_disposition = response.getHeader('content-disposition')
    self.assertEquals('inline', content_disposition.split(';')[0])
    self._validate(response.getBody())

  def test_report_view_landscape(self):
    response = self.publish(
       '/%s/person_module/pers/Base_viewHistory?landscape=1'
        % self.portal.getId(), self.auth)
    self.assertEquals(HTTP_OK, response.getStatus())
    content_type = response.getHeader('content-type')
    self.assertTrue(content_type.startswith(self.content_type), content_type)
    content_disposition = response.getHeader('content-disposition')
    self.assertEquals('inline', content_disposition.split(';')[0])
    self._validate(response.getBody())

  def test_report_view_sheet_per_report_section(self):
    response = self.publish(
       '/%s/person_module/pers/Base_viewHistory?sheet_per_report_section=1'
        % self.portal.getId(), self.auth)
    self.assertEquals(HTTP_OK, response.getStatus())
    content_type = response.getHeader('content-type')
    self.assertTrue(content_type.startswith(self.content_type), content_type)
    content_disposition = response.getHeader('content-disposition')
    self.assertEquals('inline', content_disposition.split(';')[0])
    self._validate(response.getBody())

  def test_form_view_encoding(self):
    self.portal.person_module.pers.setFirstName('Jérome')
    response = self.publish('/%s/person_module/pers/Person_view'
                          % self.portal.getId(), basic=self.auth)
    self.assertEquals(HTTP_OK, response.getStatus())
    content_type = response.getHeader('content-type')
    self.assertTrue(content_type.startswith(self.content_type), content_type)
    content_disposition = response.getHeader('content-disposition')
    self.assertEquals('inline', content_disposition.split(';')[0])
    self._validate(response.getBody())

  def test_report_view_encoding(self):
    self.portal.person_module.pers.setFirstName('Jérome')
    response = self.publish('/%s/person_module/pers/Base_viewHistory'
                          % self.portal.getId(), basic=self.auth)
    self.assertEquals(HTTP_OK, response.getStatus())
    content_type = response.getHeader('content-type')
    self.assertTrue(content_type.startswith(self.content_type), content_type)
    content_disposition = response.getHeader('content-disposition')
    self.assertEquals('inline', content_disposition.split(';')[0])
    self._validate(response.getBody())

  def test_form_list_encoding(self):
    self.portal.person_module.pers.setFirstName('Jérome')
    response = self.publish(
       '/%s/person_module/PersonModule_viewPersonList'
        % self.portal.getId(), basic=self.auth)
    self.assertEquals(HTTP_OK, response.getStatus())
    content_type = response.getHeader('content-type')
    self.assertTrue(content_type.startswith(self.content_type), content_type)
    content_disposition = response.getHeader('content-disposition')
    self.assertEquals('inline', content_disposition.split(';')[0])
    self._validate(response.getBody())

  def test_image_field_form_view(self):
    self._assertFieldInGroup('ImageField', 'Image_view', 'right')
    response = self.publish(
       '/%s/person_module/pers/img/Image_view'
        % self.portal.getId(), basic=self.auth)
    self.assertEquals(HTTP_OK, response.getStatus())
    content_type = response.getHeader('content-type')
    self.assertTrue(content_type.startswith(self.content_type), content_type)
    content_disposition = response.getHeader('content-disposition')
    self.assertEquals('inline', content_disposition.split(';')[0])
    self._validate(response.getBody())

  def test_image_field_form_view_bottom_group(self):
    self._assertFieldInGroup(
        'ImageField', 'Image_viewFullSizedImage', 'bottom')
    response = self.publish(
       '/%s/person_module/pers/img/Image_viewFullSizedImage'
        % self.portal.getId(), basic=self.auth)
    self.assertEquals(HTTP_OK, response.getStatus())
    content_type = response.getHeader('content-type')
    self.assertTrue(content_type.startswith(self.content_type), content_type)
    content_disposition = response.getHeader('content-disposition')
    self.assertEquals('inline', content_disposition.split(';')[0])
    self._validate(response.getBody())

  def test_textarea_center_group(self):
    self._assertFieldInGroup('TextAreaField', 'Person_view', 'center')
    self.assert_('my_description' in [f.getId() for f in
        self.portal.Person_view.get_fields_in_group('center')])
    self.portal.person_module.pers.setDescription('<Escape>&\nnewline')
    response = self.publish(
                   '/%s/person_module/pers/Person_view'
                   % self.portal.getId(), self.auth)
    self.assertEquals(HTTP_OK, response.getStatus())
    content_type = response.getHeader('content-type')
    self.assertTrue(content_type.startswith(self.content_type), content_type)
    content_disposition = response.getHeader('content-disposition')
    self.assertEquals('inline', content_disposition.split(';')[0])
    body = response.getBody()
    self._validate(body)

    if self.skin == 'ODT':
      # Is it good to do this only for ODT ?
      from Products.ERP5OOo.OOoUtils import OOoParser
      parser = OOoParser()
      parser.openFromString(body)
      content_xml = parser.oo_files['content.xml']
      self.assert_('&lt;Escape&gt;&amp;<text:line-break/>newline' in content_xml)
     

class TestODTStyle(TestOOoStyle):
  skin = 'ODT'
  content_type = 'application/vnd.oasis.opendocument.text'


class TestODSStyle(TestOOoStyle):
  skin = 'ODS'
  content_type = 'application/vnd.oasis.opendocument.spreadsheet'


def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestODTStyle))
  suite.addTest(unittest.makeSuite(TestODSStyle))
  return suite

