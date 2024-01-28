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
from DateTime import DateTime

from erp5.component.test.testDms import TestDocumentMixin

try:
  import magic
except ImportError:
  magic = None

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

  def test_image_conversion(self):
    filename = 'TEST-en-002.doc'
    file_ = self.makeFileUpload(filename)
    document = self.portal.portal_contributions.newContent(file=file_)
    self.tic()
    format_ = 'png'

    self.assertFalse(document.hasConversion(format=format_))
    document.convert(format_)
    self.assertTrue(document.hasConversion(format=format_))

    self.assertFalse(document.hasConversion(format=format_, display='large'))
    document.convert(format_, display='large')
    self.assertTrue(document.hasConversion(format=format_, display='large'))

    self.assertFalse(document.hasConversion(format=format_,
                                           display='large',
                                           quality=40))
    document.convert(format_, display='large', quality=40)
    self.assertTrue(document.hasConversion(format=format_,
                                           display='large',
                                           quality=40))
    if magic is not None:
      mime_detector = magic.Magic(mime=True)
      self.assertEqual(mime_detector.from_buffer(document.getConversion(format=format_)[1]),
                        'image/png')
      self.assertEqual(mime_detector.from_buffer(document.getConversion(format=format_,
                                                                         display='large')[1]),
                        'image/png')
      self.assertEqual(mime_detector.from_buffer(document.getConversion(format=format_,
                                                                         display='large',
                                                                         quality=40)[1]),
                        'image/png')

  def test_01_PersistentCacheConversion(self):
    """
      Test Conversion Cache mechanism
    """
    filename = 'TEST-en-002.doc'
    file_ = self.makeFileUpload(filename)
    document = self.portal.portal_contributions.newContent(file=file_)
    self.tic()
    document_url = document.getRelativeUrl()
    document = self.portal.restrictedTraverse(document_url)
    format_list = [format_ for format_ in document.getTargetFormatList() if format_ not in self.failed_format_list]
    if not format_list:
      self.fail('Target format list is empty')
    #Test Conversion Cache
    for format_ in format_list:
      document.convert(format=format_)
      self.commit()
      self.assertTrue(document.hasConversion(format=format_), 'Cache Storage failed for %s' % (format_))
      self.assertEqual(DateTime().Date(), document.getConversionDate(format=format_).Date())
      self.assertTrue(document.getConversionMd5(format=format_))
      self.assertTrue(document.getConversionSize(format=format_))
    document.edit(title='Foo')
    self.commit()
    #Test Cache is cleared
    for format_ in format_list:
      self.assertFalse(document.hasConversion(format=format_), 'Cache Storage failed for %s' % (format_))
      self.assertRaises(KeyError, document.getConversionSize, format=format_)
    document.edit(title='Bar')
    self.tic()
    #Test Conversion Cache after editing
    for format_ in format_list:
      document.convert(format=format_)
      self.commit()
      self.assertTrue(document.hasConversion(format=format_), 'Cache Storage failed for %s' % (format_))
      self.assertTrue(document.getConversionSize(format=format_))

  def test_02_VolatileCacheConversionOfTempObject(self):
    filename = 'TEST-en-002.doc'
    file_ = self.makeFileUpload(filename)
    document = self.portal.portal_contributions.newContent(file=file_, temp_object=1)
    document.uploadFile()
    document.processFile()
    document.convertToBaseFormat()
    format_list = [format_ for format_ in document.getTargetFormatList() if format_ not in self.failed_format_list]
    if not format_list:
      self.fail('Target format list is empty')
    #Test Conversion Cache
    for format_ in format_list:
      document.convert(format=format_)
      self.commit()
      self.assertTrue(document.hasConversion(format=format_), 'Cache Storage failed for %s' % (format_))
      self.assertEqual(DateTime().Date(), document.getConversionDate(format=format_).Date())
      self.assertTrue(document.getConversionMd5(format=format_))
      self.assertTrue(document.getConversionSize(format=format_))
    document.edit(title='Foo')
    self.commit()
    #Test Cache is cleared
    for format_ in format_list:
      self.assertFalse(document.hasConversion(format=format_), 'Cache Storage failed for %s' % (format_))
      self.assertRaises(KeyError, document.getConversionSize, format=format_)
    document.edit(title='Bar')
    self.tic()
    #Test Conversion Cache after editing
    for format_ in format_list:
      document.convert(format=format_)
      self.commit()
      self.assertTrue(document.hasConversion(format=format_), 'Cache Storage failed for %s' % (format_))
      self.assertTrue(document.getConversionSize(format=format_))

  def test_03_CacheConversionOfTempObjectIsNotMixed(self):
    filename1 = 'TEST-en-002.doc'
    filename2 = 'TEST-en-002.odt'
    file1 = self.makeFileUpload(filename1)
    file2 = self.makeFileUpload(filename2)
    document1 = self.portal.portal_contributions.newContent(file=file1, temp_object=1)
    document1.uploadFile()
    document1.processFile()
    document1.convertToBaseFormat()
    document2 = self.portal.portal_contributions.newContent(file=file2, temp_object=1)
    document2.uploadFile()
    document2.processFile()
    document2.convertToBaseFormat()
    format_ = 'pdf'
    document1.convert(format=format_)
    document2.convert(format=format_)
    self.assertNotEqual(document1.getConversion(format=format_),
                        document2.getConversion(format=format_))
    self.tic()

  def test_04_PersistentCacheConversionWithFlare(self):
    default_pref = self.portal.portal_preferences.default_site_preference
    default_pref.setPreferredConversionCacheFactory('dms_cache_factory')
    #old preferred value is still cached
    self.portal.portal_caches.clearAllCache()
    self.tic()
    filename = 'TEST-en-002.doc'
    file_ = self.makeFileUpload(filename)
    document = self.portal.portal_contributions.newContent(file=file_)
    self.tic()
    document_url = document.getRelativeUrl()
    document = self.portal.restrictedTraverse(document_url)
    format_list = [format_ for format_ in document.getTargetFormatList()\
                                      if format_ not in self.failed_format_list]
    if not format_list:
      self.fail('Target format list is empty')
    #Test Conversion Cache
    for format_ in format_list:
      document.convert(format=format_)
      self.assertTrue(document.hasConversion(format=format_),
                                      'Cache Storage failed for %s' % (format_))
      self.assertTrue(document.getConversionSize(format=format_))
    document.edit(title='Foo')
    self.commit()
    #Test Cache is cleared
    for format_ in format_list:
      self.assertFalse(document.hasConversion(format=format_),
                                      'Cache Storage failed for %s' % (format_))
      self.assertRaises(KeyError, document.getConversionSize, format=format_)
    document.edit(title='Bar')
    self.tic()
    #Test Conversion Cache after editing
    for format_ in format_list:
      document.convert(format=format_)
      self.assertTrue(document.hasConversion(format=format_),
                                      'Cache Storage failed for %s' % (format_))
      self.assertTrue(document.getConversionSize(format=format_))

  def test_05_checksum_conversion(self):
    """
      Test Conversion Cache return expected value with checksum
    """
    filename = 'TEST-en-002.doc'
    file_ = self.makeFileUpload(filename)
    document = self.portal.portal_contributions.newContent(file=file_)
    self.tic()
    document_url = document.getRelativeUrl()
    document = self.portal.restrictedTraverse(document_url)
    kw = {'format': 'html'}
    #Generate one conversion
    document.convert(**kw)
    cache_id = document._getCacheKey(**kw)
    cache_factory = document._getCacheFactory()
    data_dict = cache_factory.get(cache_id)
    #get data from cache
    self.assertTrue(data_dict['content_md5'])
    self.assertTrue(data_dict['conversion_md5'])
    self.assertTrue(data_dict['mime'])
    self.assertTrue(data_dict['data'])
    self.assertTrue(data_dict['date'])
    self.assertTrue(data_dict['size'])
    #Change md5 manualy
    data_dict['content_md5'] = 'Anything which is not md5'
    cache_factory.set(cache_id, data_dict)
    self.commit()
    self.assertRaises(KeyError, document.getConversion, format='html')

  def test_06_check_md5_is_updated(self):
    """
    Check that md5 checksum is well updated when upload a file
    """
    filename = 'TEST-en-002.doc'
    file_ = self.makeFileUpload(filename)
    document = self.portal.portal_contributions.newContent(file=file_)
    self.tic()
    document_url = document.getRelativeUrl()
    document = self.portal.restrictedTraverse(document_url)
    md5sum = document.getContentMd5()
    self.assertTrue(md5sum)
    filename2 = 'TEST-en-002.odt'
    file2 = self.makeFileUpload(filename2)
    document.edit(file=file2)
    self.assertNotEqual(md5sum, document.getContentMd5())
    self.tic()

  def test_07_check_cache_key_is_escaped(self):
    """
    Check that key (based on path of document) support unauthorised chars
    """
    default_pref = self.portal.portal_preferences.default_site_preference
    default_pref.setPreferredConversionCacheFactory('dms_cache_factory')
    #old preferred value is still cached
    self.portal.portal_caches.clearAllCache()
    self.tic()
    filename = 'TEST-en-002.doc'
    file_ = self.makeFileUpload(filename)
    document_id = 'an id with spaces'
    portal_type = 'Text'
    module = self.portal.getDefaultModule(portal_type)
    document = module.newContent(id=document_id, file=file_,
                                 portal_type=portal_type)
    self.tic()
    document_url = document.getRelativeUrl()
    document = self.portal.restrictedTraverse(document_url)
    self.assertEqual(document.getId(), document_id)
    document.convert(format='txt')
    self.assertTrue(document.getConversion(format='txt'))

  def test_08_check_conversion_cache_with_portal_document_type_list(self):
    """Check cache conversion for all Portal Document Types
    """
    portal_type_list = list(self.portal.getPortalDocumentTypeList())

    if 'File' in portal_type_list:
      #File conversion is not implemented
      portal_type_list.remove('File')
    if 'Web Illustration' in portal_type_list:
      #Web Illustration conversion is not implemented
      portal_type_list.remove('Web Illustration')
    if 'Web Table' in portal_type_list:
      #Web Table conversion is not implemented
      portal_type_list.remove('Web Table')
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
      upload_file = self.makeFileUpload(data_mapping[portal_type])
      document = module.newContent(portal_type=portal_type)
      document.edit(file=upload_file)
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
