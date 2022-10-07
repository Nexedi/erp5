# -*- coding: utf-8 -*-
##############################################################################
#
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

import io
import unittest
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.tests.utils import DummyLocalizer
from Products.ERP5Form.Selection import Selection
from Testing import ZopeTestCase
from Products.ERP5OOo.tests.utils import Validator
import six.moves.http_client
import lxml.html
import PyPDF2

HTTP_OK = six.moves.http_client.OK

# setting this to True allows the .publish() calls to provide tracebacks
debug = False

class TestOOoStyle(ERP5TypeTestCase, ZopeTestCase.Functional):
  """Tests ODF styles for ERP5."""
  skin = None
  content_type = None

  def getBusinessTemplateList(self):
    return ('erp5_core_proxy_field_legacy', 'erp5_ui_test', 'erp5_base',
            'erp5_ods_style', 'erp5_odt_style',)

  def afterSetUp(self):
    if not self.skin:
      raise NotImplementedError('Subclasses must define skin')

    gender = self.portal.portal_categories.gender
    if 'male' not in gender.objectIds():
      gender.newContent(id='male')
      self.portal.portal_caches.clearAllCache()

    self.auth = 'ERP5TypeTestCase:'
    person_module = self.portal.person_module
    if person_module._getOb('pers', None) is None:
      person_module.newContent(id='pers', portal_type='Person')
      self.tic()
    person_module.pers.setFirstName('Bob')
    person_module.pers.setGender(None)
    person_module.pers.setCareerRole(None)

    if person_module.pers._getOb('img', None) is None:
      person_module.pers.newContent(portal_type='Embedded File', id='img')

    if person_module._getOb('pers_without_image', None) is None:
      person = person_module.newContent(
                              portal_type='Person',
                              id = 'pers_without_image',
                              first_name = 'Test')
      self.tic()

    self.portal.changeSkin(self.skin)
    self.validator = Validator()
    # make sure selections are empty
    name = 'person_module_selection'
    self.portal.portal_selections.setSelectionFor(name, Selection(name))

  def publish(self, *args, **kw):
    kw['handle_errors'] = not debug
    return super(TestOOoStyle, self).publish(*args, **kw)

  def _validate(self, odf_file_data):
    error_list = self.validator.validate(odf_file_data)
    if error_list:
      self.fail(''.join(error_list))

  def _assertFieldInGroup(self, field_type, form_id, group):
    for f in getattr(self.portal, form_id).get_fields_in_group(group):
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
    self.assertEqual(HTTP_OK, response.getStatus())
    content_type = response.getHeader('content-type')
    self.assertTrue(content_type.startswith(self.content_type), content_type)
    content_disposition = response.getHeader('content-disposition')
    self.assertEqual('attachment', content_disposition.split(';')[0])
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
    self.assertEqual(HTTP_OK, response.getStatus())
    content_type = response.getHeader('content-type')
    self.assertTrue(content_type.startswith(self.content_type), content_type)
    content_disposition = response.getHeader('content-disposition')
    self.assertEqual('attachment', content_disposition.split(';')[0])
    self._validate(response.getBody())

  def test_form_view(self):
    # form_view on a form without listbox
    self.portal.person_module.pers.setDefaultAddressZipCode(59000)
    response = self.publish(
        '/%s/person_module/pers/default_address/GeographicAddress_view'
        % self.portal.getId(), self.auth)
    self.assertEqual(HTTP_OK, response.getStatus())
    content_type = response.getHeader('content-type')
    self.assertTrue(content_type.startswith(self.content_type), content_type)
    content_disposition = response.getHeader('content-disposition')
    self.assertEqual('attachment', content_disposition.split(';')[0])
    self._validate(response.getBody())

  def test_form_view_empty_listbox(self):
    # form_view on a form with an empty listbox
    if hasattr(self.portal.person_module.pers, 'default_address'):
      self.portal.person_module.pers._delObject('default_address')
    response = self.publish(
                   '/%s/person_module/pers/Person_view'
                   % self.portal.getId(), self.auth)
    self.assertEqual(HTTP_OK, response.getStatus())
    content_type = response.getHeader('content-type')
    self.assertTrue(content_type.startswith(self.content_type), content_type)
    content_disposition = response.getHeader('content-disposition')
    self.assertEqual('attachment', content_disposition.split(';')[0])
    self._validate(response.getBody())

  def test_form_view_non_empty_listbox(self):
    self.portal.person_module.pers.setDefaultAddressZipCode(59000)
    response = self.publish(
                   '/%s/person_module/pers/Person_view'
                   % self.portal.getId(), self.auth)
    self.assertEqual(HTTP_OK, response.getStatus())
    content_type = response.getHeader('content-type')
    self.assertTrue(content_type.startswith(self.content_type), content_type)
    content_disposition = response.getHeader('content-disposition')
    self.assertEqual('attachment', content_disposition.split(';')[0])
    self._validate(response.getBody())

  def test_form_view_empty_format(self):
    # empty format= does not use oood for conversion
    response = self.publish(
                   '/%s/person_module/pers/Person_view?format='
                   % self.portal.getId(), self.auth)
    self.assertEqual(HTTP_OK, response.getStatus())
    content_type = response.getHeader('content-type')
    self.assertTrue(content_type.startswith(self.content_type), content_type)
    content_disposition = response.getHeader('content-disposition')
    self.assertEqual('attachment', content_disposition.split(';')[0])
    self._validate(response.getBody())

  def test_form_view_pdf_format(self):
    # format=pdf uses oood for conversion
    response = self.publish(
                   '/%s/person_module/pers/Person_view?format=pdf'
                   % self.portal.getId(), self.auth)
    self.assertEqual(HTTP_OK, response.getStatus())
    content_type = response.getHeader('content-type')
    self.assertEqual(content_type, 'application/pdf')
    content_disposition = response.getHeader('content-disposition')
    self.assertEqual('attachment', content_disposition.split(';')[0])

  def test_form_view_html_format(self):
    # format=html is rendered inline
    response = self.publish(
                   '/%s/person_module/pers/Person_view?format=html'
                   % self.portal.getId(), self.auth)
    self.assertEqual(HTTP_OK, response.getStatus())
    content_type = response.getHeader('content-type')
    self.assertEqual(content_type, 'text/html; charset=utf-8')
    content_disposition = response.getHeader('content-disposition')
    self.assertEqual('inline', content_disposition.split(';')[0])

  def test_report_view_form_view(self):
    # Test report view rendering forms using form_view
    self.assertEqual('form_view', self.portal.Base_viewWorkflowHistory.pt)
    response = self.publish(
                   '/%s/person_module/pers/Base_viewHistory'
                    % self.portal.getId(), self.auth)
    self.assertEqual(HTTP_OK, response.getStatus())
    content_type = response.getHeader('content-type')
    self.assertTrue(content_type.startswith(self.content_type), content_type)
    content_disposition = response.getHeader('content-disposition')
    self.assertEqual('attachment', content_disposition.split(';')[0])
    self._validate(response.getBody())

  def test_report_view_form_list(self):
    # Test report view rendering forms using form_list
    self.portal.Base_viewWorkflowHistory.pt = 'form_list'
    try:
      # publish commits a transaction, so we have to restore the original page
      # template on the form
      response = self.publish(
                   '/%s/person_module/pers/Base_viewHistory'
                    % self.portal.getId(), self.auth)
    finally:
      self.portal.Base_viewWorkflowHistory.pt = 'form_view'
      self.commit()
    self.assertEqual(HTTP_OK, response.getStatus())
    content_type = response.getHeader('content-type')
    self.assertTrue(content_type.startswith(self.content_type), content_type)
    content_disposition = response.getHeader('content-disposition')
    self.assertEqual('attachment', content_disposition.split(';')[0])
    self._validate(response.getBody())


  def test_report_view_landscape(self):
    response = self.publish(
       '/%s/person_module/pers/Base_viewHistory?landscape=1'
        % self.portal.getId(), self.auth)
    self.assertEqual(HTTP_OK, response.getStatus())
    content_type = response.getHeader('content-type')
    self.assertTrue(content_type.startswith(self.content_type), content_type)
    content_disposition = response.getHeader('content-disposition')
    self.assertEqual('attachment', content_disposition.split(';')[0])
    self._validate(response.getBody())

  def test_report_view_sheet_per_report_section(self):
    response = self.publish(
       '/%s/person_module/pers/Base_viewHistory?sheet_per_report_section=1'
        % self.portal.getId(), self.auth)
    self.assertEqual(HTTP_OK, response.getStatus())
    content_type = response.getHeader('content-type')
    self.assertTrue(content_type.startswith(self.content_type), content_type)
    content_disposition = response.getHeader('content-disposition')
    self.assertEqual('attachment', content_disposition.split(';')[0])
    self._validate(response.getBody())

  def test_report_view_report_section_title(self):
    response = self.publish(
       '/%s/foo_module/FooModule_viewHierarchyTestReport'
        % self.portal.getId(), self.auth)
    self.assertEqual(HTTP_OK, response.getStatus())
    content_type = response.getHeader('content-type')
    self.assertTrue(content_type.startswith(self.content_type), content_type)
    self._validate(response.getBody())

    # check the hierarchy is properly kept ...
    if self.skin == 'ODT':
      # ... in pdf
      response = self.publish(
         '/%s/foo_module/FooModule_viewHierarchyTestReport?format=pdf'
          % self.portal.getId(), self.auth)
      pdf = PyPDF2.PdfFileReader(io.BytesIO(response.getBody()))

      def getOutlineTitles(outlines):
        for outline in outlines:
          if isinstance(outline, list):
            yield list(getOutlineTitles(outline))
          else:
            yield outline['/Title']
      self.assertEqual(
          list(getOutlineTitles(pdf.getOutlines())),
          [
              "1. First",
              [
                  "1.1 First / First",
                  "1.2 First / Second",
                  ["1.2.1 First / Second / First"],
              ],
              "2. Second",
          ],
      )

      # ..and in html
      response = self.publish(
         '/%s/foo_module/FooModule_viewHierarchyTestReport?format=html'
          % self.portal.getId(), self.auth)
      tree = lxml.html.fromstring(response.getBody())
      self.assertEqual(
          [node.text for node in tree.findall('.//h1')],
          ['1. First', '2. Second'])
      self.assertEqual(
          [node.text for node in tree.findall('.//h2')],
          ['1.1 First / First', '1.2 First / Second'])
      self.assertEqual(
          [node.text for node in tree.findall('.//h3')],
          ['1.2.1 First / Second / First'])

  def test_form_view_encoding(self):
    self.portal.person_module.pers.setFirstName('Jérome')
    response = self.publish('/%s/person_module/pers/Person_view'
                          % self.portal.getId(), basic=self.auth)
    self.assertEqual(HTTP_OK, response.getStatus())
    content_type = response.getHeader('content-type')
    self.assertTrue(content_type.startswith(self.content_type), content_type)
    content_disposition = response.getHeader('content-disposition')
    self.assertEqual('attachment', content_disposition.split(';')[0])
    self._validate(response.getBody())

  def test_control_character_encoding(self):
    # XML does not allow certain control characters
    self.portal.person_module.pers.setFirstName('This character: \x14 is not allowed in XML')
    response = self.publish('/%s/person_module/pers/Person_view'
                          % self.portal.getId(), basic=self.auth)
    self.assertEqual(HTTP_OK, response.getStatus())
    content_type = response.getHeader('content-type')
    self.assertTrue(content_type.startswith(self.content_type), content_type)
    content_disposition = response.getHeader('content-disposition')
    self.assertEqual('attachment', content_disposition.split(';')[0])
    self._validate(response.getBody())

  def test_form_view_category(self):
    self.portal.person_module.pers.setGender('male')
    response = self.publish('/%s/person_module/pers/Person_view'
                          % self.portal.getId(), basic=self.auth)
    self.assertEqual(HTTP_OK, response.getStatus())
    content_type = response.getHeader('content-type')
    self.assertTrue(content_type.startswith(self.content_type), content_type)
    content_disposition = response.getHeader('content-disposition')
    self.assertEqual('attachment', content_disposition.split(';')[0])
    self._validate(response.getBody())

  def test_form_view_broken_category(self):
    self.portal.person_module.pers.setGender('not exist')
    self.portal.person_module.pers.setCareerRole('not exist')
    response = self.publish('/%s/person_module/pers/Person_view'
                          % self.portal.getId(), basic=self.auth)
    self.assertEqual(HTTP_OK, response.getStatus())
    content_type = response.getHeader('content-type')
    self.assertTrue(content_type.startswith(self.content_type), content_type)
    content_disposition = response.getHeader('content-disposition')
    self.assertEqual('attachment', content_disposition.split(';')[0])
    self._validate(response.getBody())

  def test_form_view_embedded_image(self):
    # with image
    response = self.publish('/%s/person_module/pers/Person_viewDetails'
                          % self.portal.getId(), basic=self.auth)
    self.assertEqual(HTTP_OK, response.getStatus())
    content_type = response.getHeader('content-type')
    self.assertTrue(content_type.startswith(self.content_type), content_type)
    content_disposition = response.getHeader('content-disposition')
    self.assertEqual('attachment', content_disposition.split(';')[0])
    self._validate(response.getBody())
    # without image
    response = self.publish('/%s/person_module/pers_without_image/Person_viewDetails'
                          % self.portal.getId(), basic=self.auth)
    self.assertEqual(HTTP_OK, response.getStatus())
    content_type = response.getHeader('content-type')
    self.assertTrue(content_type.startswith(self.content_type), content_type)
    content_disposition = response.getHeader('content-disposition')
    self.assertEqual('attachment', content_disposition.split(';')[0])
    self._validate(response.getBody())

  def test_report_view_encoding(self):
    self.portal.person_module.pers.setFirstName('Jérome')
    response = self.publish('/%s/person_module/pers/Base_viewHistory'
                          % self.portal.getId(), basic=self.auth)
    self.assertEqual(HTTP_OK, response.getStatus())
    content_type = response.getHeader('content-type')
    self.assertTrue(content_type.startswith(self.content_type), content_type)
    content_disposition = response.getHeader('content-disposition')
    self.assertEqual('attachment', content_disposition.split(';')[0])
    self._validate(response.getBody())

  def test_form_list_encoding(self):
    self.portal.person_module.pers.setFirstName('Jérome')
    response = self.publish(
       '/%s/person_module/PersonModule_viewPersonList'
        % self.portal.getId(), basic=self.auth)
    self.assertEqual(HTTP_OK, response.getStatus())
    content_type = response.getHeader('content-type')
    self.assertTrue(content_type.startswith(self.content_type), content_type)
    content_disposition = response.getHeader('content-disposition')
    self.assertEqual('attachment', content_disposition.split(';')[0])
    self._validate(response.getBody())

  def test_image_field_form_view(self):
    self._assertFieldInGroup('ImageField', 'Image_view', 'right')
    response = self.publish(
       '/%s/person_module/pers/img/Image_view'
        % self.portal.getId(), basic=self.auth)
    self.assertEqual(HTTP_OK, response.getStatus())
    content_type = response.getHeader('content-type')
    self.assertTrue(content_type.startswith(self.content_type), content_type)
    content_disposition = response.getHeader('content-disposition')
    self.assertEqual('attachment', content_disposition.split(';')[0])
    self._validate(response.getBody())

  def test_image_field_form_view_bottom_group(self):
    self._assertFieldInGroup(
        'ImageField', 'Image_viewFullSizedImage', 'bottom')
    response = self.publish(
       '/%s/person_module/pers/img/Image_viewFullSizedImage'
        % self.portal.getId(), basic=self.auth)
    self.assertEqual(HTTP_OK, response.getStatus())
    content_type = response.getHeader('content-type')
    self.assertTrue(content_type.startswith(self.content_type), content_type)
    content_disposition = response.getHeader('content-disposition')
    self.assertEqual('attachment', content_disposition.split(';')[0])
    self._validate(response.getBody())

  def test_textarea_center_group(self):
    self._assertFieldInGroup('TextAreaField', 'Person_view', 'center')
    self.assert_('my_description' in [f.getId() for f in
        self.portal.Person_view.get_fields_in_group('center')])
    self.portal.person_module.pers.setDescription('<Escape>&\nnewline')
    response = self.publish(
                   '/%s/person_module/pers/Person_view'
                   % self.portal.getId(), self.auth)
    self.assertEqual(HTTP_OK, response.getStatus())
    content_type = response.getHeader('content-type')
    self.assertTrue(content_type.startswith(self.content_type), content_type)
    content_disposition = response.getHeader('content-disposition')
    self.assertEqual('attachment', content_disposition.split(';')[0])
    body = response.getBody()
    self._validate(body)

    if self.skin == 'ODT':
      # Is it good to do this only for ODT ?
      from Products.ERP5OOo.OOoUtils import OOoParser
      parser = OOoParser()
      parser.openFromString(body)
      content_xml = parser.oo_files['content.xml']
      self.assert_('&lt;Escape&gt;&amp;<text:line-break/>newline' in content_xml)

  def test_untranslatable_columns(self):
    self.portal.ListBoxZuite_reset()
    self.portal.Localizer = DummyLocalizer()
    message_catalog = self.portal.Localizer.erp5_ui
    # XXX odt style does not seem to display a listbox if it is empty ???
    self.portal.foo_module.newContent(portal_type='Foo')
    message = self.id()
    self.portal.FooModule_viewFooList.listbox.ListBox_setPropertyList(
      field_columns = ['do_not_translate | %s' % message,],
      field_untranslatablecolumns = ['do_not_translate | %s' % message,],
    )
    self.tic()
    self.portal.changeSkin(self.skin)
    response = self.publish(
                   '/%s/foo_module/FooModule_viewFooList?portal_skin='
                   % self.portal.getId(), self.auth)
    self.assertEqual(HTTP_OK, response.getStatus())
    content_type = response.getHeader('content-type')
    self.assertTrue(content_type.startswith(self.content_type), content_type)
    content_disposition = response.getHeader('content-disposition')
    self.assertEqual('attachment', content_disposition.split(';')[0])
    body = response.getBody()
    self._validate(body)

    from Products.ERP5OOo.OOoUtils import OOoParser
    parser = OOoParser()
    parser.openFromString(body)
    content_xml = parser.oo_files['content.xml']
    self.assertTrue(message in content_xml)

    # This untranslatable column have not been translated
    self.assertTrue(message not in message_catalog._translated)

  def test_form_view_ZMI(self):
    """We can edit form_view in the ZMI."""
    response = self.publish('/%s/form_view/manage_main'
       % self.portal.getId(), self.auth)
    self.assertEqual(HTTP_OK, response.getStatus())
    content_type = response.getHeader('content-type')
    self.assertEquals('text/html;charset=utf-8', content_type.lower())
    self.assertFalse(response.getHeader('content-disposition'))
    # Simplistic assertion that we are viewing the ODF XML source
    self.assertTrue('office:document-content' in response.getBody())

  def test_form_list_ZMI(self):
    """We can edit form_list in the ZMI."""
    response = self.publish('/%s/form_list/manage_main'
       % self.portal.getId(), self.auth)
    self.assertEqual(HTTP_OK, response.getStatus())
    content_type = response.getHeader('content-type')
    self.assertEquals('text/html;charset=utf-8', content_type.lower())
    self.assertFalse(response.getHeader('content-disposition'))
    self.assertTrue('office:document-content' in response.getBody())

  def test_report_view_ZMI(self):
    """We can edit report_view in the ZMI."""
    response = self.publish('/%s/report_view/manage_main'
       % self.portal.getId(), self.auth)
    self.assertEqual(HTTP_OK, response.getStatus())
    content_type = response.getHeader('content-type')
    self.assertEquals('text/html;charset=utf-8', content_type.lower())
    self.assertFalse(response.getHeader('content-disposition'))
    self.assertTrue('office:document-content' in response.getBody())

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

