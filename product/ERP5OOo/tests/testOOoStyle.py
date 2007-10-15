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

import unittest
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Testing import ZopeTestCase
from Products.ERP5OOo.tests.utils import Validator

HTTP_OK = 200


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
    if not hasattr(person_module, 'pers'):
      person_module.newContent(id='pers', portal_type='Person')
    self.portal.changeSkin(self.skin)
    self.validator = Validator()

  def _validate(self, odf_file_data):
    error_list = self.validator.validate(odf_file_data)
    if error_list:
      self.fail(''.join(error_list))

  def test_skin_selection(self):
    self.assertTrue(self.skin in
              self.portal.portal_skins.getSkinSelections())

  def test_list_view(self):
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

