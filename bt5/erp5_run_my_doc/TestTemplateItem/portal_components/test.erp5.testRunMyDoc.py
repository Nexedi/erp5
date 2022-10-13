##############################################################################
#
# Copyright (c) 2002-2012 Nexedi SA and Contributors. All Rights Reserved.
#               Rafael Monnerat <rafael@nexedi.com>
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
from erp5.component.test.testDms import makeFileUpload
from time import time
import base64

class TestRunMyDoc(ERP5TypeTestCase):
  """
   Basic Test for internal implementation of RunMyDocs
  """
  maxDiff = None
  def getTitle(self):
    return "Run My Doc"

  def getBusinessTemplateList(self):
    """
    Tuple of Business Templates we need to install
    """
    return ('erp5_base',
            'erp5_jquery',
            'erp5_jquery_ui',
            'erp5_knowledge_pad',
            'erp5_ingestion_mysql_innodb_catalog',
            'erp5_ingestion',
            'erp5_web',
            'erp5_dms',
            'erp5_slideshow_style',
            'erp5_ui_test_core',
            'erp5_run_my_doc')

  def afterSetUp(self):
    """
    This is ran before anything, used to set the environment
    """
    # here, you can create the categories and objects your test will depend on

  website_id = "test_page_web_site"

  def test_getDocumentListWithTestPage(self):
    """
     Assert if Test Page works with getDocumentList
    """
    test_page_reference = "developer-my.test.page"
    website = getattr(self.portal.web_site_module, self.website_id, None)
    if website is None:
      website = self.portal.web_site_module.newContent(
                                   portal_type='Web Site',
                                   id=self.website_id)
      website.publish()
      self.tic()

    test_page = self.portal.test_page_module.newContent(
              portal_type="Test Page",
              reference=test_page_reference,
              language="en",
              version="001")

    test_page.publish()
    self.tic()

    document = website.WebSection_getDocumentValue(test_page_reference)

    self.assertNotEqual(None, document)
    self.assertEqual(document.getRelativeUrl(),
                      test_page.getRelativeUrl())

  def test_Zuite_uploadScreenShot(self):
    """
      Test Screeshot upload script used by Zelenium to
      update screenshots of the documents.
    """
    image_upload = makeFileUpload('TEST-en-002.png')
    self.assertNotEqual(None, image_upload)

    # Create a web page, and check if the content is not overwriten
    web_page_reference = "WEB-PAGE-REFERENCE"
    web_page = self.portal.web_page_module.newContent(
                                     reference=web_page_reference,
                                     language="en", version="001")
    web_page.publishAlive()
    self.tic()

    image_reference = "IMAGE-REFERENCE-%s" % str(time())
    image_page = self.portal.image_module.newContent(
                                   reference=image_reference,
                                   language="en", version="001")
    image_page.publishAlive()
    self.tic()
    image_page_2 = self.portal.image_module.newContent(
                                   reference=image_reference,
                                   language="en", version="002")
    image_page_2.publishAlive()
    self.tic()

    self.portal.REQUEST.form['data_uri'] = image_upload
    fake_image_reference = "DO-NOT-EXISTANT-IMAGE"
    self.assertNotEqual(None,
                   self.portal.Zuite_uploadScreenshot(image_upload, fake_image_reference))

    self.assertNotEqual(None,
                   self.portal.Zuite_uploadScreenshot(image_upload, web_page_reference))

    self.assertEqual(None,
                   self.portal.Zuite_uploadScreenshot(image_upload, image_reference))

    self.tic()
    # The right image were updated.
    image_upload.seek(0)
    self.assertEqual(image_page_2.getData(), base64.b64decode(image_upload.read()))
    self.assertEqual(image_page_2.getFilename(), image_reference + '.png')
    self.assertEqual(image_page.getData(), '')

  def test_viewSeleniumTest(self):
    """
      Test the script that extracts Selenium Test from HTML body.
    """
    test_page_html = """<section><h1>TITLE</h1><details>DETAILS<details>
    <test><table class="test" style="display: none;"> <tbody> </tbody></table> </test>
    </section>
    <section><h1>TITLE</h1><details>DETAILS<details><test>
      <table class="test" style="display: none;">
        <tbody>
          <tr>
            <td colspan="3">&lt;span metal:use-macro=&quot;container/Zuite_viewTestMacroLibrary/macros/init_test_environment&quot; style=&quot;display: none;&quot;&gt;init&lt;/span&gt;</td>
          </tr>
          <tr>
            <td>selectAndWait</td>
            <td>name=select_module</td>
            <td>label=Test Pages</td>
          </tr>
          <tr>
            <td>verifyTextPresent</td>
            <td>Test Pages</td>
            <td> <br /> </td>
          </tr>
          <tr style="opacity: 1;">
            <td>clickAndWait</td>
            <td>css=a.fast_input &gt; span.image</td>
            <td> <br /> </td>
          </tr> </tbody></table> </test>
    </section>
    <section><h1>TITLE</h1><details>DETAILS<details><test>
      <table class="test" style="display: none;"> <tbody>
          <tr>
            <td>verifyTextPresent</td>
            <td>Test Pages</td>
            <td> <br /> </td>
          </tr> </tbody></table> </test>
    </section>"""

    expected_test_html = u"""<html>
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
    <title>TEST</title>
  </head>
  <body>
    <table name="SELENIUM-TEST" cellpadding="1" cellspacing="1" border="1">
      <thead>
        <tr class="title">
          <td colspan="3">TEST</td>
        </tr>
      </thead>
      <tbody>
        <span metal:use-macro="container/Zuite_CommonTemplate/macros/init" style="display: none;">init</span>
        <tr>
          <td>storeEval</td>
          <td>selenium.getCookieByName("manager_username")</td>
          <td>base_user</td>
        </tr>
        <tr>
          <td>storeEval</td>
          <td>selenium.getCookieByName("manager_password")</td>
          <td>base_password</td>
        </tr>
        <span metal:use-macro="container/Zuite_viewTestMacroLibrary/macros/init_test_environment" style="display: none;">init</span><tr>
            <td>selectAndWait</td>
            <td>name=select_module</td>
            <td>label=Test Pages</td>
          </tr>
          <tr>
            <td>verifyTextPresent</td>
            <td>Test Pages</td>
            <td> <br> </td>
          </tr>
          <tr style="opacity: 1;">
            <td>clickAndWait</td>
            <td>css=a.fast_input &gt; span.image</td>
            <td> <br> </td>
          </tr> <tr>
            <td>verifyTextPresent</td>
            <td>Test Pages</td>
            <td> <br> </td>
          </tr>
      </tbody>
    </table>
  </body>
</html>"""

    test_page = self.portal.test_page_module.newContent(title="TEST",
                                                        reference='TESTPAGEREFERENCE',
                                                        text_content=test_page_html)
    self.assertEqual(
      test_page.TestPage_viewSeleniumTest(), expected_test_html)

    self.tic()
    test_page.TestPage_runSeleniumTest()

    zuite = getattr(self.portal.portal_tests, 'TESTPAGEREFERENCE', None)
    self.assertNotEqual(zuite, None)

    zptest = getattr(zuite, "TEST", None)
    self.assertNotEqual(zptest, None)

    self.assertEqual(zptest._text, expected_test_html.strip())

    expected_test_html = u"""<html>
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
    <title>TEST</title>
  </head>
  <body>
    <table name="SELENIUM-TEST" cellpadding="1" cellspacing="1" border="1">
      <thead>
        <tr class="title">
          <td colspan="3">TEST</td>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>store</td>
          <td>http://toto.com</td>
          <td>base_url</td>
        </tr>
        <tr>
          <td>store</td>
          <td>titi</td>
          <td>base_user</td>
        </tr>
        <tr>
          <td>store</td>
          <td>toto</td>
          <td>base_password</td>
        </tr>
        <span metal:use-macro="container/Zuite_viewTestMacroLibrary/macros/init_test_environment" style="display: none;">init</span><tr>
            <td>selectAndWait</td>
            <td>name=select_module</td>
            <td>label=Test Pages</td>
          </tr>
          <tr>
            <td>verifyTextPresent</td>
            <td>Test Pages</td>
            <td> <br> </td>
          </tr>
          <tr style="opacity: 1;">
            <td>clickAndWait</td>
            <td>css=a.fast_input &gt; span.image</td>
            <td> <br> </td>
          </tr> <tr>
            <td>verifyTextPresent</td>
            <td>Test Pages</td>
            <td> <br> </td>
          </tr>
      </tbody>
    </table>
  </body>
</html>"""


    # Mimic usage of TestPage_viewSeleniumTest?url=...
    self.portal.REQUEST['url'] = "http://toto.com"
    self.portal.REQUEST['user'] = "titi"
    self.portal.REQUEST['password'] = "toto"

    self.assertEqual(test_page.TestPage_viewSeleniumTest(REQUEST=self.portal.REQUEST),
                      expected_test_html)
    self.tic()
    test_page.TestPage_runSeleniumTest()

    zuite = getattr(self.portal.portal_tests, 'TESTPAGEREFERENCE', None)
    self.assertNotEqual(zuite, None)

    zptest = getattr(zuite, "TEST", None)
    self.assertNotEqual(zptest, None)

    self.assertEqual(zptest._text, expected_test_html.strip())
