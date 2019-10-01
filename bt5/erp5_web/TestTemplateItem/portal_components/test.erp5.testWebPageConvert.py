##############################################################################
#
# Copyright (c) 2019 Nexedi SA and Contributors. All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
##############################################################################

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase

class TestWebPageConvert(ERP5TypeTestCase):

  def getTitle(self):
    return "Test Web Page Convert."

  def getBusinessTemplateList(self):
    return (
      "erp5_base",
      "erp5_web",
      "erp5_ui_test_core",
      "erp5_ui_test",
      "erp5_l10n_fr"
    )
  def afterSetUp(self):
    base_web_page = self.portal.web_page_module.get('Test_html_convert', None)
    if not base_web_page:
      base_web_page = self.portal.web_page_module.newContent(portal_type='Web Page', id='Test_html_convert')
    self.base_url = base_web_page.getAbsoluteUrl()
    self.base_web_page = base_web_page

  def test_image_relative_src_convert(self):
    test_data = '<img alt="" src="./qr_screenshot?format=" title="" type="image/svg+xml" />'
    expected_data = '<img alt="" src="%s/./qr_screenshot?format=" title="" type="image/svg+xml" />' % self.base_url
    converted_data = self.base_web_page.Base_convertHtmlToSingleFile(data = test_data)
    self.assertEqual(converted_data, expected_data)

  def test_image_reference_src_convert(self):
    test_data = '<img alt="" src="reference" title="" type="image/svg+xml" />'
    expected_data = '<img alt="" src="%s/reference" title="" type="image/svg+xml" />' % self.base_url
    converted_data = self.base_web_page.Base_convertHtmlToSingleFile(data = test_data)
    self.assertEqual(converted_data, expected_data)

  def test_image_absolute_src_convert(self):
    test_data = '<img alt="" src="http://test" title="" type="image/svg+xml" />'
    converted_data = self.base_web_page.Base_convertHtmlToSingleFile(data = test_data)
    self.assertEqual(converted_data, test_data)

  def test_image_empty_src_convert(self):
    #copy from Base_convertHtmlToSingleFile
    test_data = '<img alt="" src="" title="" type="image/svg+xml" />'
    expected_data = '<img alt="" src="data:text/html;base64," title="" type="image/svg+xml" />'
    converted_data = self.base_web_page.Base_convertHtmlToSingleFile(data = test_data)
    self.assertEqual(converted_data, expected_data)

  def test_a_relative_href_convert(self):
    test_data = '<a href="DesignDocument">Presentation</a>)'
    expected_data = '<a href="%s/DesignDocument">Presentation</a>)' % self.base_url
    converted_data = self.base_web_page.Base_convertHtmlToSingleFile(data = test_data)
    self.assertEqual(converted_data, expected_data)

  def test_a_absolute_href_convert(self):
    test_data = '<a href="http://DesignDocument">Presentation</a>)'
    converted_data = self.base_web_page.Base_convertHtmlToSingleFile(data = test_data)
    self.assertEqual(converted_data, test_data)

  def test_a_empty_href_convert(self):
    test_data = '<a href="">Presentation</a>)'
    converted_data = self.base_web_page.Base_convertHtmlToSingleFile(data = test_data)
    self.assertEqual(converted_data, test_data)

  def test_a_anchor_href_convert(self):
    test_data = '<a href="#DesignDocument">Presentation</a>)'
    converted_data = self.base_web_page.Base_convertHtmlToSingleFile(data = test_data)
    self.assertEqual(converted_data, test_data)

  def test_script_inline_convert(self):
    test_data = '<!DOCTYPE html><html><head><script>console.log("test")</script></head></html>'
    converted_data = self.base_web_page.Base_convertHtmlToSingleFile(data = test_data, allow_script=False)
    self.assertEqual(converted_data, '<!DOCTYPE html><html><head></head></html>')
    converted_data = self.base_web_page.Base_convertHtmlToSingleFile(data = test_data, allow_script=True)
    self.assertEqual(converted_data, test_data)

  def test_script_external_convert(self):
    test_data = '<!DOCTYPE html><html><head><script src="erp5_xhtml_style/erp5.js"></script></head></html>'
    converted_data = self.base_web_page.Base_convertHtmlToSingleFile(data = test_data, allow_script=True)
    expected_data ='<!DOCTYPE html><html><head><script src="%s/erp5_xhtml_style/erp5.js"></script></head></html>' % self.base_url
    self.assertEqual(converted_data, expected_data)

  def test_script_empty_convert(self):
    test_data = '<!DOCTYPE html><html><head><script src=""></script></head></html>'
    converted_data = self.base_web_page.Base_convertHtmlToSingleFile(data = test_data, allow_script=True)
    expected_data ='<!DOCTYPE html><html><head><script src="data:text/html;base64,"></script></head></html>'
    self.assertEqual(converted_data, expected_data)

  def test_link_inline_convert(self):
    test_data = '<!DOCTYPE html><html><head><style>body{}</style></head></html>'
    converted_data = self.base_web_page.Base_convertHtmlToSingleFile(data = test_data)
    self.assertEqual(converted_data, test_data)

  def test_link_external_convert(self):
    test_data = '<!DOCTYPE html><html><head> <link rel="stylesheet" href="erp5_xhtml_style/erp5.css" /> </head></html>'
    converted_data = self.base_web_page.Base_convertHtmlToSingleFile(data = test_data)
    expected_data ='<!DOCTYPE html><html><head> <link rel="stylesheet" href="%s/erp5_xhtml_style/erp5.css" /> </head></html>' % self.base_url
    self.assertEqual(converted_data, expected_data)

  def test_link_empty_convert(self):
    test_data = '<!DOCTYPE html><html><head> <link rel="stylesheet" href="" /> </head></html>'
    converted_data = self.base_web_page.Base_convertHtmlToSingleFile(data = test_data)
    expected_data ='<!DOCTYPE html><html><head> <link rel="stylesheet" href="data:text/html;base64," /> </head></html>'
    self.assertEqual(converted_data, expected_data)