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

class TestRunMyDoc(ERP5TypeTestCase):
  """
   Basic Test for internal implementation of RunMyDocs
  """

  def getTitle(self):
    return "Run My Doc"

  def getBusinessTemplateList(self):
    """
    Tuple of Business Templates we need to install
    """
    # Include all list here.
    return ['erp5_base'
            'erp5_jquery'
            'erp5_jquery_ui'
            'erp5_knowledge_pad'
            'erp5_web'
            'erp5_dms'
            'erp5_slideshow_style'
            'erp5_ui_test_core',
            'erp5_run_my_doc']

  def afterSetUp(self):
    """
    This is ran before anything, used to set the environment
    """
    # here, you can create the categories and objects your test will depend on
    pass

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
      self.stepTic()

    test_page = self.portal.test_page_module.newContent(
              portal_type="Test Page",
              reference=test_page_reference,
              language="en",
              version="001")
              
    test_page.publish()
    self.stepTic()
    
    document = website.WebSection_getDocumentValue(test_page_reference)
    
    self.assertNotEquals(None, document)
    self.assertEquals(document.getRelativeUrl(),
                      test_page.getRelativeUrl())
    