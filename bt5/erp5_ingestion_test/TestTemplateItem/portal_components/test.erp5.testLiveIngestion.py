# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010 Nexedi SA and Contributors. All Rights Reserved.
#                    Nicolas Delaby <nicolas@erp5.org>
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


from Products.ERP5Type.tests.ERP5TypeLiveTestCase import ERP5TypeLiveTestCase
from Products.CMFCore.utils import getToolByName
import random
import string

# test files' home
FILE_NAME_REGULAR_EXPRESSION = "(?P<reference>[A-Z&é@{]{3,7})-(?P<language>[a-z]{2})-(?P<version>[0-9]{3})"
REFERENCE_REGULAR_EXPRESSION = "(?P<reference>[A-Z&é@{]{3,7})(-(?P<language>[a-z]{2}))?(-(?P<version>[0-9]{3}))?"

class TestIngestion(ERP5TypeLiveTestCase):
  """
    ERP5 Document Management System - test url ingestion mechanism
  """

  _path_to_delete_list = []

  def getTitle(self):
    """
      Return the title of the current test set.
    """
    return "ERP5 Live DMS - URL Ingestion"

  def afterSetUp(self):
    """
      Initialize the ERP5 site.
    """
    self.login()
    self.portal = self.getPortal()
    self.setSystemPreference()

  def beforeTearDown(self):
    portal = self.portal
    # delete created documents by test
    for path in self._path_to_delete_list:
      document = portal.unrestrictedTraverse(path, None)
      if document is None:
        continue
      doucument_id = document.getId()
      document_parent = document.getParentValue()
      document_parent._delObject(doucument_id)
    # Unindex deleted documents
    self.tic()

  def setSystemPreference(self):
    default_pref = self.getDefaultSystemPreference()
    default_pref.setPreferredDocumentFilenameRegularExpression(FILENAME_REGULAR_EXPRESSION)
    default_pref.setPreferredDocumentReferenceRegularExpression(REFERENCE_REGULAR_EXPRESSION)

  def contributeFileWithUrl(self, script_id, filename=None):
    """compute url and call portal_contributions.newContentFromUrl
    """
    portal = self.portal
    contribution_tool = getToolByName(portal, 'portal_contributions')
    # seed parameter is here to ensure entropy for document id generation
    seed = ''.join([random.choice(string.ascii_letters) for i in xrange(20)])
    url = portal.absolute_url()
    url += '/%s?seed=%s' % (script_id, seed)
    if filename:
      url += '&filename=%s' % filename
    document = contribution_tool.newContentFromURL(url=url)
    self._path_to_delete_list.append(document.getPath())
    return document

  def test_01_contributeTextFileWithFilenamefromUrl(self):
    """
      Contribute file with filename
    """
    script_id = 'ERP5Site_getTextFileWithFileName'
    filename = 'any_file.txt'
    document = self.contributeFileWithUrl(script_id, filename=filename)
    self.tic()
    self.assertEqual(document.getPortalType(), 'Text')
    self.assertEqual(document.getFilename(), filename)
    self.assertEqual(document.getContentType(), 'text/plain')
    self.assertTrue(document.hasData())

  def test_02_contributeTextFileWithExplicitExtensionfromUrl(self):
    """
      Contribute file without filename but explicit extension
      in URL
    """
    script_id = 'ERP5Site_getTextFile.txt'
    document = self.contributeFileWithUrl(script_id)
    self.tic()
    self.assertEqual(document.getPortalType(), 'Text')
    self.assertEqual(document.getFilename(), script_id)
    self.assertEqual(document.getContentType(), 'text/plain')
    self.assertTrue(document.hasData())

  def test_03_textFileWithExplicitExtensionWithoutContentTypefromUrl(self):
    """
      Contribute file with explicit extension without content-type
    """
    script_id = 'ERP5Site_getTextFileWithoutContentType.txt'
    document = self.contributeFileWithUrl(script_id)
    self.tic()
    self.assertEqual(document.getPortalType(), 'Text')
    self.assertEqual(document.getFilename(), script_id)
    self.assertEqual(document.getContentType(), 'text/plain')
    self.assertTrue(document.hasData())

  def test_04_contributeTextFileWithFilenameAndRedirectionfromUrl(self):
    """
      Contribute file with url which redirect to another location
    """
    script_id = 'ERP5Site_getTextFileWithFileNameAndRedirection'
    filename = 'any_file.txt'
    document = self.contributeFileWithUrl(script_id, filename=filename)
    self.tic()
    self.assertEqual(document.getPortalType(), 'Text')
    self.assertEqual(document.getFilename(), filename)
    self.assertEqual(document.getContentType(), 'text/plain')
    self.assertTrue(document.hasData())

  def test_05_contributeTextFileWithoutFilenameButHTMLContentType(self):
    """
      Contribute file with just explicit content-type
      And check that correct portal_type is used.
    """
    script_id = 'ERP5Site_getTextFileWithoutFileNameButHTMLContentType'
    document = self.contributeFileWithUrl(script_id)
    self.tic()
    self.assertEqual(document.getPortalType(), 'Web Page')
    self.assertEqual(document.getFilename(), script_id)
    self.assertEqual(document.getContentType(), 'text/html')
    self.assertTrue(document.hasData())

