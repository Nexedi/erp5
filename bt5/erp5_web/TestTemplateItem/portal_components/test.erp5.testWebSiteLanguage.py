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

import unittest

WEB_SITE_ID = "test_language_indexation"

class TestWebSiteLanguageIndexation(ERP5TypeTestCase):

  def getTitle(self):
    return "Test Web Site Language Indexation."

  def getBusinessTemplateList(self):
    return (
      "erp5_base",
      "erp5_web",
      "erp5_ui_test_core",
      "erp5_l10n_fr"
    )

  def setupWebSite(self, **kw):
    """
    Setup Web Site
    """

    if WEB_SITE_ID in self.portal.web_site_module:
      self.portal.web_site_module.manage_delObjects(WEB_SITE_ID)

    website = self.portal.web_site_module.newContent(
      portal_type="Web Site",
      id=WEB_SITE_ID,
      available_language_list=['en', 'fr'],
      **kw
    )
    website.publish()
    return website

  def assertDocumentIndexed(self, doc, expected_result):
    sql_foo_list = self.portal.portal_catalog(relative_url=doc.getRelativeUrl())
    self.assertEquals(len(sql_foo_list), int(expected_result))

  def test_isSubtreeIndexable(self):
    web_site = self.setupWebSite()
    self.tic()

    # Check that web site itself is indexable
    self.assertDocumentIndexed(web_site, True)

    # Test that document created in the context of a web site
    # is correctly indexed
    foo_module = web_site.restrictedTraverse('foo_module')
    foo = foo_module.newContent(portal_type='Foo')
    self.tic()
    self.assertDocumentIndexed(foo, True)

    # Test that document created in an "asContext" web site
    # is not indexed
    foo_module = web_site.asContext().restrictedTraverse('foo_module')
    foo = foo_module.newContent(portal_type='Foo')
    self.tic()
    self.assertDocumentIndexed(foo, False)

    # Test that document created in the context of a temp web site
    # is not indexed
    tmp_web_site = web_site.getParentValue().newContent(temp_object=True,
                                                        portal_type='Web Site')
    foo_module = tmp_web_site.restrictedTraverse('foo_module')
    foo = foo_module.newContent(portal_type='Foo')
    self.tic()
    self.assertDocumentIndexed(foo, False)

    # Test that document created in the context of a temp web section
    # is not indexed
    web_section = web_site.newContent(temp_object=True,
                                      portal_type='Web Section')
    foo_module = web_section.restrictedTraverse('foo_module')
    foo = foo_module.newContent(portal_type='Foo')
    self.tic()
    self.assertDocumentIndexed(foo, False)

    # Test that document created in the context of a temp web site
    # for language is correctly indexed
    foo_module = web_site.restrictedTraverse('fr/foo_module')
    foo = foo_module.newContent(portal_type='Foo')
    self.tic()
    self.assertDocumentIndexed(foo, True)

    # Test that document created in the context of a temp web site
    # for language inside a temp web site is not indexed
    foo_module = web_site.asContext().restrictedTraverse('fr/foo_module')
    foo = foo_module.newContent(portal_type='Foo')
    self.tic()
    self.assertDocumentIndexed(foo, False)

