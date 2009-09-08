# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009 Nexedi SA and Contributors. All Rights Reserved.
#          Nicolas Delaby <nicolas@nexedi.com>
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
import time

import transaction
from Testing import ZopeTestCase
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.tests.utils import FileUpload
from Products.ERP5Type.tests.utils import DummyLocalizer
from AccessControl.SecurityManagement import newSecurityManager
from Products.ERP5Type.Cache import DEFAULT_CACHE_SCOPE
from zLOG import LOG
import os

# Define the conversion server host
conversion_server_host = ('127.0.0.1', 8008)

TEST_FILES_HOME = os.path.join(os.path.dirname(__file__), 'test_document')
FILE_NAME_REGULAR_EXPRESSION = "(?P<reference>[A-Z]{3,10})-(?P<language>[a-z]{2})-(?P<version>[0-9]{3})"
REFERENCE_REGULAR_EXPRESSION = "(?P<reference>[A-Z]{3,10})(-(?P<language>[a-z]{2}))?(-(?P<version>[0-9]{3}))?"


def makeFilePath(name):
  return os.getenv('INSTANCE_HOME') + '/../Products/ERP5OOo/tests/test_document/' + name

def makeFileUpload(name, as_name=None):
  if as_name is None:
    as_name = name
  path = makeFilePath(name)
  return FileUpload(path, as_name)


class TestDocumentConversionCache(ERP5TypeTestCase, ZopeTestCase.Functional):
  """
    Test basic document - related operations
  """
  failed_format_list = (#'fodt',
                        #'bib',
                        #'writer.xhtml',
                        #'pdb',
                        #'psw',
                        #'tex',
                        #'wiki.txt',
                        #'uot',
                        #'2003.doc.xml',
                        #'docbook.xml',
                       )

  def getTitle(self):
    return "DMS"

  ## setup

  def afterSetUp(self):
    self.setSystemPreference()
    # set a dummy localizer (because normally it is cookie based)
    self.portal.Localizer = DummyLocalizer()
    # make sure every body can traverse document module
    self.portal.document_module.manage_permission('View', ['Anonymous'], 1)
    self.portal.document_module.manage_permission(
                           'Access contents information', ['Anonymous'], 1)

  def setSystemPreference(self):
    default_pref = self.portal.portal_preferences.default_site_preference
    default_pref.setPreferredOoodocServerAddress(conversion_server_host[0])
    default_pref.setPreferredOoodocServerPortNumber(conversion_server_host[1])
    default_pref.setPreferredDocumentFileNameRegularExpression(FILE_NAME_REGULAR_EXPRESSION)
    default_pref.setPreferredDocumentReferenceRegularExpression(REFERENCE_REGULAR_EXPRESSION)
    default_pref.setPreferredConversionCacheFactory('document_cache_factory')
    if default_pref.getPreferenceState() != 'global':
      default_pref.enable()

  def getDocumentModule(self):
    return getattr(self.getPortal(),'document_module')

  def getBusinessTemplateList(self):
    return ('erp5_base',
            'erp5_ingestion', 'erp5_ingestion_mysql_innodb_catalog',
            'erp5_web', 'erp5_dms')

  def getNeededCategoryList(self):
    return ()

  def beforeTearDown(self):
    """
      Do some stuff after each test:
      - clear document module
    """
    self.clearDocumentModule()

  def clearDocumentModule(self):
    """
      Remove everything after each run
    """
    transaction.abort()
    self.tic()
    doc_module = self.getDocumentModule()
    ids = [i for i in doc_module.objectIds()]
    doc_module.manage_delObjects(ids)
    transaction.commit()
    self.tic()

  def clearCache(self):
    self.portal.portal_caches.clearAllCache()

  ## tests

  def test_01_HasEverything(self):
    """
      Standard test to make sure we have everything we need - all the tools etc
    """
    print '\nTest Has Everything '
    self.assertNotEqual(self.getCategoryTool(), None)
    self.assertNotEqual(self.getSimulationTool(), None)
    self.assertNotEqual(self.getTypeTool(), None)
    self.assertNotEqual(self.getSQLConnection(), None)
    self.assertNotEqual(self.getCatalogTool(), None)
    self.assertNotEqual(self.getWorkflowTool(), None)

  def test_01_PersistentCacheConversion(self):
    """
      Test Conversion Cache mechanism
    """
    print '\nPersistent Cache Conversion'

    filename = 'TEST-en-002.doc'
    file = makeFileUpload(filename)
    document = self.portal.portal_contributions.newContent(file=file)
    transaction.commit()
    self.tic()
    document_url = document.getRelativeUrl()
    document = self.portal.restrictedTraverse(document_url)
    format_list = [format for format in document.getTargetFormatList() if format not in self.failed_format_list]
    if not format_list:
      self.fail('Target format list is empty')
    #Test Conversion Cache
    for format in format_list:
      document.convert(format=format)
      transaction.commit()
      self.assertTrue(document.hasConversion(format=format), 'Cache Storage failed for %s' % (format))
      self.assertTrue(document.getConversionSize(format=format))
    document.clearConversionCache()
    transaction.commit()
    #Test Cache is cleared
    for format in format_list:
      self.assertFalse(document.hasConversion(format=format), 'Cache Storage failed for %s' % (format))
      self.assertEqual(document.getConversionSize(format=format), 0)
    document.clearConversionCache()
    transaction.commit()
    #Test Conversion Cache after clearConversionCache
    for format in format_list:
      document.convert(format=format)
      transaction.commit()
      self.assertTrue(document.hasConversion(format=format), 'Cache Storage failed for %s' % (format))
      self.assertTrue(document.getConversionSize(format=format))

  def test_02_VolatileCacheConversionOfTempObject(self):
    """
      Test Conversion Cache mechanism
    """
    print '\nVolatile Cache Conversion of temp objects'

    filename = 'TEST-en-002.doc'
    file = makeFileUpload(filename)
    document = self.portal.portal_contributions.newContent(file=file, temp_object=1)
    document.uploadFile()
    document.processFile()
    document.convertToBaseFormat()
    format_list = [format for format in document.getTargetFormatList() if format not in self.failed_format_list]
    if not format_list:
      self.fail('Target format list is empty')
    #Test Conversion Cache
    for format in format_list:
      document.convert(format=format)
      transaction.commit()
      self.assertTrue(document.hasConversion(format=format), 'Cache Storage failed for %s' % (format))
      self.assertTrue(document.getConversionSize(format=format))
    document.clearConversionCache()
    transaction.commit()
    #Test Cache is cleared
    for format in format_list:
      self.assertFalse(document.hasConversion(format=format), 'Cache Storage failed for %s' % (format))
      self.assertEqual(document.getConversionSize(format=format), 0)
    document.clearConversionCache()
    transaction.commit()
    #Test Conversion Cache after clearConversionCache
    for format in format_list:
      document.convert(format=format)
      transaction.commit()
      self.assertTrue(document.hasConversion(format=format), 'Cache Storage failed for %s' % (format))
      self.assertTrue(document.getConversionSize(format=format))

  def test_03_CacheConversionOfTempObjectIsNotMixed(self):
    """
      Test Conversion Cache mechanism
    """
    print '\nCache Conversion of temp objects is not mixed'

    filename1 = 'TEST-en-002.doc'
    filename2 = 'TEST-en-002.odt'
    file1 = makeFileUpload(filename1)
    file2 = makeFileUpload(filename2)
    document1 = self.portal.portal_contributions.newContent(file=file1, temp_object=1)
    document1.uploadFile()
    document1.processFile()
    document1.convertToBaseFormat()
    document2 = self.portal.portal_contributions.newContent(file=file2, temp_object=1)
    document2.uploadFile()
    document2.processFile()
    document2.convertToBaseFormat()
    format = 'pdf'
    document1.convert(format=format)
    document2.convert(format=format)
    self.assertNotEqual(document1.getConversion(format=format),
                        document2.getConversion(format=format))

  def test_04_PersistentCacheConversionWithFlare(self):
    """
      Test Conversion Cache mechanism
    """
    print '\nPersistent Cache Conversion with Flare'
    default_pref = self.portal.portal_preferences.default_site_preference
    default_pref.setPreferredConversionCacheFactory('dms_cache_factory')
    #old preferred value is still cached
    self.portal.portal_caches.clearAllCache()
    transaction.commit()
    self.tic()
    filename = 'TEST-en-002.doc'
    file = makeFileUpload(filename)
    document = self.portal.portal_contributions.newContent(file=file)
    transaction.commit()
    self.tic()
    document_url = document.getRelativeUrl()
    document = self.portal.restrictedTraverse(document_url)
    format_list = [format for format in document.getTargetFormatList() if format not in self.failed_format_list]
    if not format_list:
      self.fail('Target format list is empty')
    #Test Conversion Cache
    for format in format_list:
      document.convert(format=format)
      self.assertTrue(document.hasConversion(format=format), 'Cache Storage failed for %s' % (format))
      self.assertTrue(document.getConversionSize(format=format))
    document.clearConversionCache()
    transaction.commit()
    #Test Cache is cleared
    for format in format_list:
      self.assertFalse(document.hasConversion(format=format), 'Cache Storage failed for %s' % (format))
      self.assertEqual(document.getConversionSize(format=format), 0)
    document.clearConversionCache()
    transaction.commit()
    #Test Conversion Cache after clearConversionCache
    for format in format_list:
      document.convert(format=format)
      self.assertTrue(document.hasConversion(format=format), 'Cache Storage failed for %s' % (format))
      self.assertTrue(document.getConversionSize(format=format))

  def test_05_checksum_conversion(self):
    """
      Test Conversion Cache return expected value with checksum
    """
    print '\nCheck checksum in Conversion'
    filename = 'TEST-en-002.doc'
    file = makeFileUpload(filename)
    document = self.portal.portal_contributions.newContent(file=file)
    transaction.commit()
    self.tic()
    document_url = document.getRelativeUrl()
    document = self.portal.restrictedTraverse(document_url)
    kw = {'format': 'html'}
    #Generate one conversion
    document.convert(**kw)
    cache_id = document.generateCacheId(**kw)
    cache_factory = document._getCacheFactory()
    for cache_plugin in cache_factory.getCachePluginList():
      cache_entry = cache_plugin.get(document.getPath(), DEFAULT_CACHE_SCOPE)
      value = cache_entry.getValue()
      md5sum, mime, data = value.get(cache_id)
      #get data from cache
      self.assertTrue(md5sum)
      self.assertTrue(mime)
      self.assertTrue(data)
      #Change md5 manually
      value.update({cache_id: ('Anything which is not md5', mime, data)})
      cache_plugin.set(document.getPath(), DEFAULT_CACHE_SCOPE, value, 0, 0)
    self.assertRaises(KeyError, document.getConversion, format='html')

  def test_06_check_md5_is_updated(self):
    """
    Check that md5 checksum is well updated when upload a file
    """
    print '\nCheck checksum is updated'
    filename = 'TEST-en-002.doc'
    file = makeFileUpload(filename)
    document = self.portal.portal_contributions.newContent(file=file)
    transaction.commit()
    self.tic()
    document_url = document.getRelativeUrl()
    document = self.portal.restrictedTraverse(document_url)
    md5sum = document.getContentMd5()
    self.assertTrue(md5sum)
    filename2 = 'TEST-en-002.odt'
    file2 = makeFileUpload(filename2)
    document.edit(file=file2)
    self.assertNotEqual(md5sum, document.getContentMd5())

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestDocumentConversionCache))
  return suite


# vim: syntax=python shiftwidth=2 
