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
from testDms import TestDocumentMixin
from Products.ERP5Type.tests.utils import FileUpload
from Products.ERP5Type.tests.utils import DummyLocalizer
from AccessControl.SecurityManagement import newSecurityManager
from Products.ERP5Type.Cache import DEFAULT_CACHE_SCOPE
from zLOG import LOG
import os

try:
  import magic
except ImportError:
  magic = None

def makeFilePath(name):
  return os.path.join(os.path.dirname(__file__), 'test_document', name)

def makeFileUpload(name, as_name=None):
  if as_name is None:
    as_name = name
  path = makeFilePath(name)
  return FileUpload(path, as_name)


class TestDocumentConversionCache(TestDocumentMixin):
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
    return "OOo Conversion Cache"

  ## tests

  def test_image_conversion(self):
    filename = 'TEST-en-002.doc'
    file = makeFileUpload(filename)
    document = self.portal.portal_contributions.newContent(file=file)
    transaction.commit()
    self.tic()
    format = 'png'

    self.assertFalse(document.hasConversion(format=format))
    document.convert(format)
    self.assertTrue(document.hasConversion(format=format))

    self.assertFalse(document.hasConversion(format=format, display='large'))
    document.convert(format, display='large')
    self.assertTrue(document.hasConversion(format=format, display='large'))

    self.assertFalse(document.hasConversion(format=format,
                                           display='large',
                                           quality=40))
    document.convert(format, display='large', quality=40)
    self.assertTrue(document.hasConversion(format=format,
                                           display='large',
                                           quality=40))
    if magic is not None:
      mime_detector = magic.Magic(mime=True)
      self.assertEquals(mime_detector.from_buffer(document.getConversion(format=format)[1]),
                        'image/png')
      self.assertEquals(mime_detector.from_buffer(document.getConversion(format=format,
                                                                         display='large')[1]),
                        'image/png')
      self.assertEquals(mime_detector.from_buffer(document.getConversion(format=format,
                                                                         display='large',
                                                                         quality=40)[1]),
                        'image/png')

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
    document.edit(title='Foo')
    transaction.commit()
    #Test Cache is cleared
    for format in format_list:
      self.assertFalse(document.hasConversion(format=format), 'Cache Storage failed for %s' % (format))
      self.assertEquals(document.getConversionSize(format=format), 0)
    document.edit(title='Bar')
    transaction.commit()
    self.tic()
    #Test Conversion Cache after editing
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
    document.edit(title='Foo')
    transaction.commit()
    #Test Cache is cleared
    for format in format_list:
      self.assertFalse(document.hasConversion(format=format), 'Cache Storage failed for %s' % (format))
      self.assertEqual(document.getConversionSize(format=format), 0)
    document.edit(title='Bar')
    transaction.commit()
    self.tic()
    #Test Conversion Cache after editing
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
    transaction.commit()
    self.tic()

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
    format_list = [format for format in document.getTargetFormatList()\
                                      if format not in self.failed_format_list]
    if not format_list:
      self.fail('Target format list is empty')
    #Test Conversion Cache
    for format in format_list:
      document.convert(format=format)
      self.assertTrue(document.hasConversion(format=format),
                                      'Cache Storage failed for %s' % (format))
      self.assertTrue(document.getConversionSize(format=format))
    document.edit(title='Foo')
    transaction.commit()
    #Test Cache is cleared
    for format in format_list:
      self.assertFalse(document.hasConversion(format=format),
                                      'Cache Storage failed for %s' % (format))
      self.assertEqual(document.getConversionSize(format=format), 0)
    document.edit(title='Bar')
    transaction.commit()
    self.tic()
    #Test Conversion Cache after editing
    for format in format_list:
      document.convert(format=format)
      self.assertTrue(document.hasConversion(format=format),
                                      'Cache Storage failed for %s' % (format))
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
    cache_id = document._getCacheKey(**kw)
    cache_factory = document._getCacheFactory()
    for cache_plugin in cache_factory.getCachePluginList():
      cache_entry = cache_plugin.get(cache_id, DEFAULT_CACHE_SCOPE)
      data_dict = cache_entry.getValue()
      #get data from cache
      self.assertTrue(data_dict['content_md5'])
      self.assertTrue(data_dict['conversion_md5'])
      self.assertTrue(data_dict['mime'])
      self.assertTrue(data_dict['data'])
      self.assertTrue(data_dict['date'])
      self.assertTrue(data_dict['size'])
      #Change md5 manualy
      data_dict['content_md5'] = 'Anything which is not md5'
      cache_plugin.set(cache_id, DEFAULT_CACHE_SCOPE, data_dict, 100, 0)
    transaction.commit()
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
    self.tic()

  def test_07_check_cache_key_is_escaped(self):
    """
    Check that key (based on path of document) support unauthorised chars
    """
    print '\nCheck key (based on path) support unauthorised chars'
    default_pref = self.portal.portal_preferences.default_site_preference
    default_pref.setPreferredConversionCacheFactory('dms_cache_factory')
    #old preferred value is still cached
    self.portal.portal_caches.clearAllCache()
    transaction.commit()
    self.tic()
    filename = 'TEST-en-002.doc'
    file = makeFileUpload(filename)
    document_id = 'an id with spaces'
    portal_type = 'Text'
    module = self.portal.getDefaultModule(portal_type)
    document = module.newContent(id=document_id, file=file,
                                 portal_type=portal_type)
    transaction.commit()
    self.tic()
    document_url = document.getRelativeUrl()
    document = self.portal.restrictedTraverse(document_url)
    self.assertEquals(document.getId(), document_id)
    document.convert(format='txt')
    self.assertTrue(document.getConversion(format='txt'))

  def test_08_check_conversion_cache_with_portal_document_type_list(self):
    """Check cache conversion for all Portal Document Types
    """
    print '\nCheck cache conversion for all Portal Document Types'
    portal_type_list = list(self.portal.getPortalDocumentTypeList())

    if 'File' in portal_type_list:
      #File conversion is not implemented
      portal_type_list.remove('File')
    data_mapping = {'Drawing': 'TEST-en-002.sxd',
                    'Text': 'TEST-en-002.doc',
                    'Spreadsheet': 'TEST-en-002.sxc',
                    'Presentation': 'TEST-en-002.sxi',
                    'Web Page': 'TEST-en-002.html',
                    'Image': 'TEST-en-002.gif',
                    'File': 'TEST-en-002.rtf',
                    'PDF': 'TEST-en-002.pdf'}
    #Check that all portal_types are handled by test
    self.assertEqual(len(portal_type_list), len([pt for pt in portal_type_list if pt in data_mapping]))
    for portal_type in portal_type_list:
      module = self.portal.getDefaultModule(portal_type=portal_type)
      upload_file = makeFileUpload(data_mapping[portal_type])
      document = module.newContent(portal_type=portal_type)
      document.edit(file=upload_file)
      transaction.commit()
      self.tic()
      document.convert(format='txt')
      document.convert(format='html')
      self.assertTrue(document.getConversion(format='txt'))
      self.assertTrue(document.getConversion(format='html'))

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestDocumentConversionCache))
  return suite


# vim: syntax=python shiftwidth=2 
