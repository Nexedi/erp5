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

"""This module provides utilities for testing ODF files.

Validator: a class defining a `validate` method that expects odf file content
as first argument and returns list of errors.

"""

import os
import sys
import tempfile
import zipfile
import popen2
from cStringIO import StringIO

try:
  import lxml
except ImportError:
  lxml = None
try:
  import odfpy
except ImportError:
  odfpy = None

if lxml:
  class LXMLValidator:
    """Validate ODF document using RelaxNG and lxml"""
    schema_url = \
      'http://docs.oasis-open.org/office/v1.1/OS/OpenDocument-schema-v1.1.rng'

    def __init__(self, schema_url=schema_url):
      self.schema_url = schema_url
      self.schema_path = os.path.join(
        os.path.dirname(__file__), os.path.basename(schema_url))
      self.relaxng =  lxml.etree.RelaxNG(lxml.etree.parse(self.schema_path))

    def validate(self, odf_file_content):
      error_list = []
      odf_file = StringIO(odf_file_content)
      for f in ('content.xml', 'meta.xml', 'styles.xml', 'settings.xml'):
        error_list.extend(self._validateXML(odf_file, f))
      return error_list

    def _validateXML(self, odf_file, content_file_name):
      zfd = zipfile.ZipFile(odf_file)
      lxml.etree.parse(StringIO(zfd.read(content_file_name)))
      return []
      """
      # The following is the past implementation that validates with
      # RelaxNG schema. But recent LibreOffice uses extended odf
      # format by default, that does not pass the RelaxNG validation.
      doc.docinfo.URL = content_file_name
      self.relaxng.validate(doc)
      return [error for error in str(self.relaxng.error_log).splitlines(True)]
      """

  Validator = LXMLValidator

elif odfpy:

  class OdflintValidator:
    """Validates ODF files using odflint, available on pypi
    http://opendocumentfellowship.org/development/projects/odfpy
    """
    def validate(self, odf_file_content):
      fd, file_name = tempfile.mkstemp()
      os.write(fd, odf_file_content)
      os.close(fd)
      stdout, stdin = popen2.popen4('odflint %s' % file_name)
      stdin.close()
      error_list = ''
      for line in stdout:
        if line.startswith('Error: '):
          error_list += line
      os.unlink(file_name)
      return error_list

  Validator = OdflintValidator

else:

  class NoValidator:
    """Does not actually validate, but keep the interface."""
    def validate(self, odf_file_content):
      print >> sys.stderr, 'No validator available'

  Validator = NoValidator

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.tests.utils import DummyLocalizer
from Products.ERP5Form.Selection import Selection
from Testing import ZopeTestCase
import httplib
HTTP_OK = httplib.OK
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
      person_module.newContent(
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
      from erp5.component.module.OOoUtils import OOoParser
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

    from erp5.component.module.OOoUtils import OOoParser
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
    self.assertEquals('text/html;charset=UTF-8', content_type)
    self.assertFalse(response.getHeader('content-disposition'))
    # Simplistic assertion that we are viewing the ODF XML source
    self.assertTrue('office:document-content' in response.getBody())

  def test_form_list_ZMI(self):
    """We can edit form_list in the ZMI."""
    response = self.publish('/%s/form_list/manage_main'
       % self.portal.getId(), self.auth)
    self.assertEqual(HTTP_OK, response.getStatus())
    content_type = response.getHeader('content-type')
    self.assertEquals('text/html;charset=UTF-8', content_type)
    self.assertFalse(response.getHeader('content-disposition'))
    self.assertTrue('office:document-content' in response.getBody())

  def test_report_view_ZMI(self):
    """We can edit report_view in the ZMI."""
    response = self.publish('/%s/report_view/manage_main'
       % self.portal.getId(), self.auth)
    self.assertEqual(HTTP_OK, response.getStatus())
    content_type = response.getHeader('content-type')
    self.assertEquals('text/html;charset=UTF-8', content_type)
    self.assertFalse(response.getHeader('content-disposition'))
    self.assertTrue('office:document-content' in response.getBody())

class TestOOoStyleWithFlare(TestOOoStyle):
  """Tests ODF styles for ERP5 with Flare."""
  def getTitle(self):
    return "Test OOo Style with Flare"

  def afterSetUp(self):
    default_pref = self.portal.portal_preferences.default_site_preference
    default_pref.setPreferredConversionCacheFactory('dms_cache_factory')
    if default_pref.getPreferenceState() != 'global':
      default_pref.enable()
    TestOOoStyle.afterSetUp(self)
