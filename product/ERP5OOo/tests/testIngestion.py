# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010 Nexedi SA and Contributors. All Rights Reserved.
#                    Bartek Gorny <bg@erp5.pl>
#                    Jean-Paul Smets <jp@nexedi.com>
#                    Ivan Tyagov <ivan@nexedi.com>
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

import io
import unittest
import os
from cgi import FieldStorage
from lxml import etree
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl import Unauthorized
from DateTime import DateTime
from Products.ERP5Type.Utils import convertToUpperCase
from Products.ERP5Type.tests.ERP5TypeTestCase import (
  ERP5TypeTestCase, _getConversionServerUrlList)
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.ERP5Type.tests.Sequence import SequenceList
from Products.ERP5Type.tests.utils import FileUpload, removeZODBPythonScript, \
  createZODBPythonScript
from Products.ERP5OOo.OOoUtils import OOoBuilder
from Products.CMFCore.utils import getToolByName
from zExceptions import BadRequest
from zExceptions import Redirect
import ZPublisher.HTTPRequest
from unittest import expectedFailure
import six.moves.http_client
import six.moves.urllib.parse, six.moves.urllib.request

import base64
import mock

# test files' home
TEST_FILES_HOME = os.path.join(os.path.dirname(__file__), 'test_document')
FILENAME_REGULAR_EXPRESSION = "(?P<reference>[A-Z&é@{]{3,7})-(?P<language>[a-z]{2})-(?P<version>[0-9]{3})"
REFERENCE_REGULAR_EXPRESSION = "(?P<reference>[A-Z&é@{]{3,7})(-(?P<language>[a-z]{2}))?(-(?P<version>[0-9]{3}))?"


def makeFilePath(name):
  return os.path.join(TEST_FILES_HOME, name)

def makeFileUpload(name, as_name=None):
  if as_name is None:
    as_name = name
  path = makeFilePath(name)
  return FileUpload(path, as_name)


class IngestionTestCase(ERP5TypeTestCase):
  def getBusinessTemplateList(self):
    """
      Return the list of required business templates.
    """
    return ('erp5_core_proxy_field_legacy', 'erp5_base',
            'erp5_ingestion', 'erp5_ingestion_mysql_innodb_catalog',
            'erp5_web', 'erp5_crm', 'erp5_dms')

  def afterSetUp(self):
    self.setSystemPreference()

  def setSystemPreference(self):
    default_pref = self.getDefaultSystemPreference()
    default_pref.setPreferredRedirectToDocument(False)
    default_pref.setPreferredDocumentFilenameRegularExpression(FILENAME_REGULAR_EXPRESSION)
    default_pref.setPreferredDocumentReferenceRegularExpression(REFERENCE_REGULAR_EXPRESSION)

  def beforeTearDown(self):
    # cleanup modules
    module_id_list = """web_page_module
    document_module
    image_module
    external_source_module
    """.split()
    for module_id in module_id_list:
      module = self.portal[module_id]
      module.manage_delObjects([id for id in module.objectIds()])
    self.tic()
    activity_tool = self.portal.portal_activities
    activity_status = {m.processing_node < -1
                       for m in activity_tool.getMessageList()}
    if True in activity_status:
      activity_tool.manageClearActivities()
    else:
      assert not activity_status
    self.portal.portal_caches.clearAllCache()
    # Cleanup portal_skins
    script_id_list = ('ContributionTool_isURLIngestionPermitted',
                      'Document_getPropertyDictFromContent',
                      'Document_getPropertyDictFromInput',
                      'Document_getPropertyDictFromFilename',
                      'Document_getPropertyDictFromUserLogin',
                      'Document_finishIngestion',
                      'PDF_finishIngestion',
                      'Document_getPreferredDocumentMetadataDiscoveryOrderList',
                      'Text_getPropertyDictFromContent',
                      'Text_getPropertyDictFromInput',
                      'Text_getPropertyDictFromFilename',
                      'Text_getPropertyDictFromUserLogin',
                      'Text_finishIngestion',
                      'Text_getPreferredDocumentMetadataDiscoveryOrderList',)
    skin_tool = self.portal.portal_skins
    for script_id in script_id_list:
      if script_id in skin_tool.custom.objectIds():
        skin_tool.custom._delObject(script_id)
    self.commit()


class TestIngestion(IngestionTestCase):
  """
    ERP5 Document Management System - test file ingestion mechanism
  """

  ##################################
  ##  ZopeTestCase Skeleton
  ##################################
  def afterSetUp(self):
    """
      Initialize the ERP5 site.
    """
    self.login()
    self.datetime = DateTime()
    self.portal = self.getPortal()
    self.portal_categories = self.getCategoryTool()
    self.portal_catalog = self.getCatalogTool()
    self.createDefaultCategoryList()
    self.setSimulatedNotificationScript()
    createZODBPythonScript(
      self.portal.portal_skins.custom,
      "ContributionTool_isURLIngestionPermitted",
      "url",
      "return True",
    )
    super(TestIngestion, self).afterSetUp()

  def setSimulatedNotificationScript(self, sequence=None, sequence_list=None, **kw):
    """
      Create simulated (empty) email notification script
    """
    context = self.portal.portal_skins.custom
    script_id = 'Document_notifyByEmail'
    if not hasattr(context, script_id):

      createZODBPythonScript(context, script_id,
                            'email_to, event, doc, **kw', 'return')

  def createDefaultCategoryList(self):
    """
      Create some categories for testing. DMS security
      is based on group, site, function, publication_section
      and projects.

      NOTE (XXX): some parts of this method could be either
      moved to Category Tool or to ERP5 Test Case.
    """
    self.category_list = [
                         # Role categories
                          {'path' : 'role/internal'
                           ,'title': 'Internal'
                           }
                          ,{'path' : 'function/musician/wind/saxophone'
                           ,'title': 'Saxophone'
                           }
                          ,{'path' : 'group/medium'
                           ,'title': 'Medium'
                           }
                          ,{'path' : 'site/arctic/spitsbergen'
                           ,'title': 'Spitsbergen'
                           }
                          ,{'path' : 'group/anybody'
                           ,'title': 'Anybody'
                           }
                          ,{'path' : 'group/anybody/a1'
                           ,'title': 'Anybody 1'
                           }
                          ,{'path' : 'group/anybody/a2'
                           ,'title': 'Anybody 2'
                           }
                          ,{'path' : 'publication_section/cop'
                           ,'title': 'COPs'
                           }
                          ,{'path' : 'publication_section/cop/one'
                           ,'title': 'COP one'
                           }
                         ]

    # Create categories
    # Note : this code was taken from the CategoryTool_importCategoryFile python
    #        script (packaged in erp5_core).
    for category in self.category_list:
      keys = category.keys()
      if 'path' in keys:
        base_path_obj = self.portal_categories
        is_base_category = True
        for category_id in category['path'].split('/'):
          # The current category is not existing
          if category_id not in base_path_obj.contentIds():
            # Create the category
            if is_base_category:
              category_type = 'Base Category'
            else:
              category_type = 'Category'
            base_path_obj.newContent( portal_type       = category_type
                                    , id                = category_id
                                    )
          base_path_obj = base_path_obj[category_id]
          is_base_category = False
        new_category = base_path_obj

        # Set the category properties
        for key in keys:
          if key != 'path':
            method_id = "set" + convertToUpperCase(key)
            value = category[key]
            if value not in ('', None):
              if hasattr(new_category, method_id):
                method = getattr(new_category, method_id)
                method(value.encode('UTF-8'))
    self.tic()

  def getCategoryList(self, base_category=None):
    """
      Get a list of categories with same base categories.
    """
    categories = []
    if base_category is not None:
      for category in self.category_list:
        if category["path"].split('/')[0] == base_category:
          categories.append(category)
    return categories

  def newEmptyDocument(self, portal_type):
    """
      Create an empty document of given portal type
      and given ID.

    """
    document_module = self.portal.getDefaultModule(portal_type)
    return document_module.newContent(portal_type=portal_type)

  def ingestFormatList(self, document, format_list):
    """
      Upload in document document_id all test files which match
      any of the formats in format_list.

      portal_type can be specified to force the use of
      the default module for a given portal type instead
      of the document module.

      For every file, this checks is the word "magic"
      is present in both SearchableText and asText.
    """
    for revision, format in enumerate(format_list):
      filename = 'TEST-en-002.%s' %format
      f = makeFileUpload(filename)
      document.edit(file=f)
      self.tic()
      self.assertTrue(document.hasFile())
      if document.isSupportBaseDataConversion():
        # this is how we know if it was ok or not
        self.assertEqual(document.getExternalProcessingState(), 'converted')
        self.assertIn('magic', document.SearchableText())
        self.assertIn('magic', str(document.asText()))
      else:
        # check if SearchableText() does not raise any exception
        document.SearchableText()

  def checkDocumentExportList(self, document, format, asserted_target_list):
    """
      Upload document ID document_id with
      a test file of given format and assert that the document
      can be converted to any of the formats in asserted_target_list
    """
    filename = 'TEST-en-002.' + format
    f = makeFileUpload(filename)
    document.edit(file=f)
    self.tic()
    # We call clear cache to be sure that the target list is updated
    self.getPortal().portal_caches.clearCache()
    target_list = document.getTargetFormatList()
    for target in asserted_target_list:
      self.assertTrue(target in target_list, 'target:%r not in %r' % (target,
                                                                 target_list,))

  def contributeFileList(self, with_portal_type=False):
    """
      Tries to a create new content through portal_contributions
      for every possible file type. If with_portal_type is set
      to true, portal_type is specified when calling newContent
      on portal_contributions.
      http://framework.openoffice.org/documentation/mimetypes/mimetypes.html
    """
    created_documents = []
    extension_to_type = (('ppt', 'Presentation')
                        ,('doc', 'Text')
                        ,('sxc', 'Spreadsheet')
                        ,('pdf', 'PDF')
                        ,('jpg', 'Image')
                        ,('py', 'File')
                        )
    counter = 1
    old_portal_type = ''
    for extension, portal_type in extension_to_type:
      filename = 'TEST-en-002.%s' %extension
      file = makeFileUpload(filename)
      # if we change portal type we must change version because
      # mergeRevision would fail
      if portal_type != old_portal_type:
        counter += 1
        old_portal_type = portal_type
      file.filename = 'TEST-en-00%d.%s' % (counter, extension)
      if with_portal_type:
        document = self.portal.portal_contributions.newContent(portal_type=portal_type, file=file)
      else:
        document = self.portal.portal_contributions.newContent(file=file)
      created_documents.append(document)
    self.tic()
    # inspect created objects
    count = 0
    for extension, portal_type in extension_to_type:
      document = created_documents[count]
      count+=1
      self.assertEqual(document.getPortalType(), portal_type)
      self.assertEqual(document.getReference(), 'TEST')
      if document.isSupportBaseDataConversion():
        # We check if conversion has succeeded by looking
        # at the external_processing workflow
        self.assertEqual(document.getExternalProcessingState(), 'converted')
        self.assertIn('magic', document.SearchableText())

  def newPythonScript(self, script_id, argument_list, code):
    """
      Creates a new python script with given argument_list
      and source code.
    """
    context = self.portal.portal_skins.custom
    if context._getOb(script_id, None) is not None:
      context._delObject(script_id)
    createZODBPythonScript(context, script_id, argument_list, code)

  def setDiscoveryOrder(self, order):
    """
      Creates a script to define the metadata discovery order
      for Text documents.
    """
    script_code = "return %s" % str(order)
    self.newPythonScript('Text_getPreferredDocumentMetadataDiscoveryOrderList',
                         '', script_code)

  def discoverMetadata(self, document):
    """
      Sets input parameters and on the document ID document_id
      and discover metadata. For reindexing
    """
    input_parameter_dict = dict(reference='INPUT',
                                language='in',
                                version='004',
                                short_title='from_input',
                                contributor='person_module/james')
    # pass to discovery filename and user_login
    document.discoverMetadata(filename=document.getFilename(),
                              user_login='john_doe',
                              input_parameter_dict=input_parameter_dict)
    self.tic()

  def checkMetadataOrder(self, document, expected_metadata):
    """
    Asserts that metadata of document ID document_id
    is the same as expected_metadata
    """
    for k, v in expected_metadata.items():
      self.assertEqual(document.getProperty(k), v)

  def receiveEmail(self, data,
                   portal_type='Document Ingestion Message',
                   container_path='document_ingestion_module',
                   filename='email.emx'):
    return self.portal.portal_contributions.newContent(data=data,
                                                       portal_type=portal_type,
                                                       container_path=container_path,
                                                       filename=filename)

  ##################################
  ##  Basic steps
  ##################################
  def stepCreatePerson(self, sequence=None, sequence_list=None, **kw):
    """
      Create a person with ID "john" if it does not exists already
    """
    portal_type = 'Person'
    person_id = 'john'
    reference = 'john_doe'
    person_module = self.portal.person_module
    if getattr(person_module, person_id, None) is not None:
      return
    person = person_module.newContent(portal_type='Person',
                                      id=person_id,
                                      reference=reference,
                                      first_name='John',
                                      last_name='Doe',
                                      default_email_text='john@doe.com')
    self.tic()

  def stepCreateTextDocument(self, sequence=None, sequence_list=None, **kw):
    """
      Create an empty Text document with ID 'one'
      This document will be used in most tests.
    """
    document = self.newEmptyDocument('Text')
    sequence.edit(document_path=document.getPath())

  def stepCreateSpreadsheetDocument(self, sequence=None, sequence_list=None, **kw):
    """
      Create an empty Spreadsheet document with ID 'two'
      This document will be used in most tests.
    """
    document = self.newEmptyDocument('Spreadsheet')
    sequence.edit(document_path=document.getPath())

  def stepCreatePresentationDocument(self, sequence=None, sequence_list=None, **kw):
    """
      Create an empty Presentation document with ID 'three'
      This document will be used in most tests.
    """
    document = self.newEmptyDocument('Presentation')
    sequence.edit(document_path=document.getPath())

  def stepCreateDrawingDocument(self, sequence=None, sequence_list=None, **kw):
    """
      Create an empty Drawing document with ID 'four'
      This document will be used in most tests.
    """
    document = self.newEmptyDocument('Presentation')
    sequence.edit(document_path=document.getPath())

  def stepCreatePDFDocument(self, sequence=None, sequence_list=None, **kw):
    """
      Create an empty PDF document with ID 'five'
      This document will be used in most tests.
    """
    document = self.newEmptyDocument('PDF')
    sequence.edit(document_path=document.getPath())

  def stepCreateImageDocument(self, sequence=None, sequence_list=None, **kw):
    """
      Create an empty Image document with ID 'six'
      This document will be used in most tests.
    """
    document = self.newEmptyDocument('Image')
    sequence.edit(document_path=document.getPath())

  def stepCreateFileDocument(self, sequence=None, sequence_list=None, **kw):
    """
      Create an empty File document with ID 'file'
      This document will be used in most tests.
    """
    document = self.newEmptyDocument('File')
    sequence.edit(document_path=document.getPath())

  def stepCheckEmptyState(self, sequence=None, sequence_list=None, **kw):
    """
      Check if the document is in "empty" processing state
      (ie. no file upload has been done yet)
    """
    document = self.portal.restrictedTraverse(sequence.get('document_path'))
    return self.assertEqual(document.getExternalProcessingState(), 'empty')

  def stepCheckUploadedState(self, sequence=None, sequence_list=None, **kw):
    """
      Check if the document is in "uploaded" processing state
      (ie. a file upload has been done)
    """
    document = self.portal.restrictedTraverse(sequence.get('document_path'))
    return self.assertEqual(document.getExternalProcessingState(), 'uploaded')

  def stepCheckConvertingState(self, sequence=None, sequence_list=None, **kw):
    """
      Check if the document is in "converting" processing state
      (ie. a file upload has been done and the document is converting)
    """
    document = self.portal.restrictedTraverse(sequence.get('document_path'))
    return self.assertEqual(document.getExternalProcessingState(), 'converting')

  def stepCheckConvertedState(self, sequence=None, sequence_list=None, **kw):
    """
      Check if the document is in "converted" processing state
      (ie. a file conversion has been done and the document has
      been converted)
    """
    document = self.portal.restrictedTraverse(sequence.get('document_path'))
    return self.assertEqual(document.getExternalProcessingState(), 'converted')

  def stepStraightUpload(self, sequence=None, sequence_list=None, **kw):
    """
      Upload a file directly from the form
      check if it has the data and filename
    """
    filename = 'TEST-en-002.doc'
    document = self.portal.restrictedTraverse(sequence.get('document_path'))
    # First revision is 1 (like web pages)
    self.assertEqual(document.getRevision(), '1')
    f = makeFileUpload(filename)
    document.edit(file=f)
    self.assertTrue(document.hasFile())
    self.assertEqual(document.getFilename(), filename)
    # Revision is 1 after upload (revisions are strings)
    self.assertEqual(document.getRevision(), '2')
    document.reindexObject()
    self.commit()

  def stepUploadFromViewForm(self, sequence=None, sequence_list=None, **kw):
    """
      Upload a file from view form and make sure this increases the revision
    """
    document = self.portal.restrictedTraverse(sequence.get('document_path'))
    f = makeFileUpload('TEST-en-002.doc')
    revision = document.getRevision()
    document.edit(file=f)
    self.assertEqual(document.getRevision(), str(int(revision) + 1))
    document.reindexObject()
    self.commit()

  def stepUploadTextFromContributionTool(self, sequence=None, sequence_list=None, **kw):
    """
      Upload a file from contribution.
    """
    f = makeFileUpload('TEST-en-002.doc')
    document = self.portal.portal_contributions.newContent(file=f)
    sequence.edit(document_path=document.getPath())
    self.commit()

  def stepReuploadTextFromContributionTool(self, sequence=None, sequence_list=None, **kw):
    """
      Upload a file from contribution form and make sure this update existing
      document and don't make a new document.
    """
    document = self.portal.restrictedTraverse(sequence.get('document_path'))
    revision = document.getRevision()
    number_of_document = len(self.portal.document_module.objectIds())
    self.assertNotIn('This document is modified.', document.asText())

    f = makeFileUpload('TEST-en-002-modified.doc')
    f.filename = 'TEST-en-002.doc'

    self.portal.portal_contributions.newContent(file=f)
    self.tic()
    self.assertEqual(document.getRevision(), str(int(revision) + 1))
    self.assertIn('This document is modified.', document.asText())
    self.assertEqual(len(self.portal.document_module.objectIds()),
                      number_of_document)
    document.reindexObject()
    self.commit()

  def stepUploadAnotherTextFromContributionTool(self, sequence=None, sequence_list=None, **kw):
    """
      Upload another file from contribution.
    """
    f = makeFileUpload('ANOTHE-en-001.doc')
    document = self.portal.portal_contributions.newContent(id='two', file=f)
    sequence.edit(document_path=document.getPath())
    self.tic()
    self.assertIn('This is a another very interesting document.', document.asText())
    self.assertEqual(document.getReference(), 'ANOTHE')
    self.assertEqual(document.getVersion(), '001')
    self.assertEqual(document.getLanguage(), 'en')

  def stepDiscoverFromFilename(self, sequence=None, sequence_list=None, **kw):
    """
      Upload a file using contribution tool. This should trigger metadata
      discovery and we should have basic coordinates immediately,
      from first stage.
    """
    document = self.portal.restrictedTraverse(sequence.get('document_path'))
    filename = 'TEST-en-002.doc'
    # First make sure the regular expressions work
    property_dict = document.getPropertyDictFromFilename(filename)
    self.assertEqual(property_dict['reference'], 'TEST')
    self.assertEqual(property_dict['language'], 'en')
    self.assertEqual(property_dict['version'], '002')
    # Then make sure content discover works
    # XXX - This part must be extended
    property_dict = document.getPropertyDictFromContent()
    self.assertEqual(property_dict['title'], 'title')
    self.assertEqual(property_dict['description'], 'comments')
    self.assertEqual(property_dict['subject_list'], ['keywords'])
    # Then make sure metadata discovery works
    f = makeFileUpload(filename)
    document.edit(file=f)
    self.assertEqual(document.getReference(), 'TEST')
    self.assertEqual(document.getLanguage(), 'en')
    self.assertEqual(document.getVersion(), '002')
    self.assertEqual(document.getFilename(), filename)

  def stepCheckConvertedContent(self, sequence=None, sequence_list=None, **kw):
    """
      Check that the input file was successfully converted
      and that its SearchableText and asText contain
      the word "magic"
    """
    self.tic()
    document = self.portal.restrictedTraverse(sequence.get('document_path'))
    self.assertTrue(document.hasBaseData())
    self.assertIn('magic', document.SearchableText())
    self.assertIn('magic', str(document.asText()))

  def stepSetSimulatedDiscoveryScript(self, sequence=None, sequence_list=None, **kw):
    """
      Create Text_getPropertyDictFrom[source] scripts
      to simulate custom site's configuration
    """
    self.newPythonScript('Text_getPropertyDictFromUserLogin',
                         'user_name=None', "return {'contributor':'person_module/john'}")
    self.newPythonScript('Text_getPropertyDictFromContent', '',
                         "return {'short_title':'short', 'title':'title', 'contributor':'person_module/john',}")

  def stepTestMetadataSetting(self, sequence=None, sequence_list=None, **kw):
    """
      Upload with custom getPropertyDict methods
      check that all metadata are correct
    """
    f = makeFileUpload('TEST-en-002.doc')
    document = self.portal.portal_contributions.newContent(file=f)
    self.tic()
    # Then make sure content discover works
    property_dict = document.getPropertyDictFromUserLogin()
    self.assertEqual(property_dict['contributor'], 'person_module/john')
    # reference from filename (the rest was checked some other place)
    self.assertEqual(document.getReference(), 'TEST')
    # short_title from content
    self.assertEqual(document.getShortTitle(), 'short')
    # title from metadata inside the document
    self.assertEqual(document.getTitle(),  'title')
    # contributors from user
    self.assertEqual(document.getContributor(), 'person_module/john')

  def stepEditMetadata(self, sequence=None, sequence_list=None, **kw):
    """
      we change metadata in a document which has ODF
    """
    document = self.portal.restrictedTraverse(sequence.get('document_path'))
    kw = dict(title='another title',
              subject_list=['another', 'subject'],
              description='another description')
    document.edit(**kw)
    self.tic()

  def stepCheckChangedMetadata(self, sequence=None, sequence_list=None, **kw):
    """
      then we download it and check if it is changed
    """
    # XXX actually this is an example of how it should be
    # implemented in OOoDocument class - we don't really
    # need oood for getting/setting metadata...
    document = self.portal.restrictedTraverse(sequence.get('document_path'))
    newcontent = document.getBaseData()
    builder = OOoBuilder(newcontent)
    xml_tree = etree.fromstring(builder.extract('meta.xml'))
    title = xml_tree.find('*/{%s}title' % xml_tree.nsmap['dc']).text
    self.assertEqual(title, 'another title')
    subject = [x.text for x in xml_tree.findall('*/{%s}keyword' % xml_tree.nsmap['meta'])]
    self.assertEqual(subject, [u'another', u'subject'])
    description = xml_tree.find('*/{%s}description' % xml_tree.nsmap['dc']).text
    self.assertEqual(description, u'another description')

  def stepIngestTextFormats(self, sequence=None, sequence_list=None, **kw):
    """
      ingest all supported text formats
      make sure they are converted
    """
    format_list = ['rtf', 'doc', 'txt', 'sxw']
    document = self.portal.restrictedTraverse(sequence.get('document_path'))
    self.ingestFormatList(document, format_list)

  def stepIngestSpreadsheetFormats(self, sequence=None, sequence_list=None,
                                   **kw):
    """
      ingest all supported spreadsheet formats
      make sure they are converted
    """
    format_list = ['xls', 'sxc']
    document = self.portal.restrictedTraverse(sequence.get('document_path'))
    self.ingestFormatList(document, format_list)

  def stepIngestPresentationFormats(self, sequence=None, sequence_list=None,
                                    **kw):
    """
      ingest all supported presentation formats
      make sure they are converted
    """
    format_list = ['ppt', 'sxi']
    document = self.portal.restrictedTraverse(sequence.get('document_path'))
    self.ingestFormatList(document, format_list)

  def stepIngestPDFFormats(self, sequence=None, sequence_list=None, **kw):
    """
      ingest all supported PDF formats
      make sure they are converted
    """
    format_list = ['pdf']
    document = self.portal.restrictedTraverse(sequence.get('document_path'))
    self.ingestFormatList(document, format_list)

  def stepIngestDrawingFormats(self, sequence=None, sequence_list=None, **kw):
    """
      ingest all supported presentation formats
      make sure they are converted
    """
    format_list = ['sxd',]
    document = self.portal.restrictedTraverse(sequence.get('document_path'))
    self.ingestFormatList(document, format_list)

  def stepIngestPDFFormats(self, sequence=None, sequence_list=None, **kw):
    """
      ingest all supported pdf formats
      make sure they are converted
    """
    format_list = ['pdf']
    document = self.portal.restrictedTraverse(sequence.get('document_path'))
    self.ingestFormatList(document, format_list)

  def stepIngestImageFormats(self, sequence=None, sequence_list=None, **kw):
    """
      ingest all supported image formats
    """
    format_list = ['jpg', 'gif', 'bmp', 'png']
    document = self.portal.restrictedTraverse(sequence.get('document_path'))
    self.ingestFormatList(document, format_list)

  def stepIngestFileFormats(self, sequence=None, sequence_list=None, **kw):
    """
      ingest all supported file formats
    """
    format_list = ['txt', 'rss', 'xml',]
    document = self.portal.restrictedTraverse(sequence.get('document_path'))
    self.ingestFormatList(document, format_list)

  def stepCheckTextDocumentExportList(self, sequence=None, sequence_list=None,
                                      **kw):
    document = self.portal.restrictedTraverse(sequence.get('document_path'))
    self.checkDocumentExportList(document, 'doc',
                                 ['pdf', 'doc', 'rtf', 'txt', 'odt'])
    # legacy format will be replaced
    expectedFailure(self.checkDocumentExportList)(document, 'doc',
                                                 ['writer.html'])

  def stepCheckSpreadsheetDocumentExportList(self, sequence=None,
                                             sequence_list=None, **kw):
    document = self.portal.restrictedTraverse(sequence.get('document_path'))
    self.checkDocumentExportList(document, 'xls', ['csv', 'xls', 'ods', 'pdf'])
    # legacy format will be replaced
    expectedFailure(self.checkDocumentExportList)(document, 'xls',
                                 ['calc.html', 'calc.pdf'])

  def stepCheckPresentationDocumentExportList(self, sequence=None,
                                              sequence_list=None, **kw):
    document = self.portal.restrictedTraverse(sequence.get('document_path'))
    self.checkDocumentExportList(document, 'ppt', ['ppt', 'odp', 'pdf'])
    # legacy format will be replaced
    expectedFailure(self.checkDocumentExportList)(document,
                                                 'ppt', ['impr.pdf'])

  def stepCheckDrawingDocumentExportList(self, sequence=None,
                                         sequence_list=None, **kw):
    document = self.portal.restrictedTraverse(sequence.get('document_path'))
    self.checkDocumentExportList(document, 'sxd', ['jpg', 'svg', 'pdf', 'odg'])
    # legacy format will be replaced
    expectedFailure(self.checkDocumentExportList)(document,
                                                 'sxd', ['draw.pdf'])

  def stepExportPDF(self, sequence=None, sequence_list=None, **kw):
    """
      Try to export PDF to text and HTML
    """
    document = self.portal.restrictedTraverse(sequence.get('document_path'))
    f = makeFileUpload('TEST-en-002.pdf')
    document.edit(file=f)
    mime, text = document.convert('text')
    self.assertIn('magic', text)
    self.assertTrue(mime == 'text/plain')
    mime, html = document.convert('html')
    self.assertIn('magic', html)
    self.assertTrue(mime == 'text/html')

  def stepExportImage(self, sequence=None, sequence_list=None, **kw):
    """
      Check we are able to resize images
    """
    image = self.portal.restrictedTraverse(sequence.get('document_path'))
    f = makeFileUpload('TEST-en-002.jpg')
    image.edit(file=f)
    self.tic()
    mime, data = image.convert(None)
    self.assertEqual(mime, 'image/jpeg')
    mime, small_data = image.convert(None, display='small')
    mime, large_data = image.convert(None, display='xlarge')
    # Check we are able to resize the image.
    self.assertTrue(len(small_data) < len(large_data))

  def stepCleanUp(self, sequence=None, sequence_list=None, **kw):
    """
        Clean up DMS system from old content.
    """
    portal = self.getPortal()
    for module in (portal.document_module, portal.image_module, portal.document_ingestion_module):
      module.manage_delObjects(list(module.objectIds()))

  def stepContributeFileListWithType(self, sequence=None, sequence_list=None, **kw):
    """
      Contribute all kinds of files giving portal type explicitly
      TODO: test situation whereby portal_type given explicitly is wrong
    """
    self.contributeFileList(with_portal_type=True)

  def stepContributeFileListWithNoType(self, sequence=None, sequence_list=None,
                                       **kw):
    """
      Contribute all kinds of files
      let the system figure out portal type by itself
    """
    self.contributeFileList(with_portal_type=False)

  def stepSetSimulatedDiscoveryScriptForOrdering(self, sequence=None,
                                                 sequence_list=None, **kw):
    """
      set scripts which are supposed to overwrite each other's metadata
      desing is the following:
                    File Name     User    Content        Input
      reference     TEST          USER    CONT           INPUT
      language      en            us                     in
      version       002                   003            004
      contributor                 john    jack           james
      short_title                         from_content   from_input
    """
    input_dict = dict(reference='INPUT',
                 language='in',
                 version='004',
                 short_title='from_input',
                 contributor='person_module/james')
    self.newPythonScript('Text_getPropertyDictFromInput',
                         'inputed_kw', "return %r" % (input_dict,))
    self.newPythonScript('Text_getPropertyDictFromUserLogin', 'user_name=None',
                         "return {'reference':'USER', 'language':'us',"\
                         " 'contributor':'person_module/john'}")
    self.newPythonScript('Text_getPropertyDictFromContent', '',
                         "return {'reference':'CONT', 'version':'003',"\
                         " 'contributor':'person_module/jack',"\
                         " 'short_title':'from_content'}")

  def stepCheckMetadataSettingOrderFICU(self, sequence=None,
                                        sequence_list=None, **kw):
    """
     This is the default
    """
    expected_metadata = dict(reference='TEST', language='en', version='002',
                             short_title='from_input',
                             contributor='person_module/james')
    self.setDiscoveryOrder(['filename', 'input', 'content', 'user_login'])
    document = self.portal.restrictedTraverse(sequence.get('document_path'))
    self.discoverMetadata(document)
    self.checkMetadataOrder(document, expected_metadata)

  def stepCheckMetadataSettingOrderCUFI(self, sequence=None,
                                        sequence_list=None, **kw):
    """
     Content - User - Filename - Input
    """
    expected_metadata = dict(reference='CONT', language='us', version='003',
                             short_title='from_content',
                             contributor='person_module/jack')
    self.setDiscoveryOrder(['content', 'user_login', 'filename', 'input'])
    document = self.portal.restrictedTraverse(sequence.get('document_path'))
    self.discoverMetadata(document)
    self.checkMetadataOrder(document, expected_metadata)

  def stepCheckMetadataSettingOrderUIFC(self, sequence=None,
                                        sequence_list=None, **kw):
    """
     User - Input - Filename - Content
    """
    expected_metadata = dict(reference='USER', language='us', version='004',
                             short_title='from_input',
                             contributor='person_module/john')
    self.setDiscoveryOrder(['user_login', 'input', 'filename', 'content'])
    document = self.portal.restrictedTraverse(sequence.get('document_path'))
    self.discoverMetadata(document)
    self.checkMetadataOrder(document, expected_metadata)

  def stepCheckMetadataSettingOrderICUF(self, sequence=None,
                                        sequence_list=None, **kw):
    """
     Input - Content - User - Filename
    """
    expected_metadata = dict(reference='INPUT', language='in', version='004',
                             short_title='from_input',
                             contributor='person_module/james')
    self.setDiscoveryOrder(['input', 'content', 'user_login', 'filename'])
    document = self.portal.restrictedTraverse(sequence.get('document_path'))
    self.discoverMetadata(document)
    self.checkMetadataOrder(document, expected_metadata)

  def stepCheckMetadataSettingOrderUFCI(self, sequence=None,
                                        sequence_list=None, **kw):
    """
     User - Filename - Content - Input
    """
    expected_metadata = dict(reference='USER', language='us', version='002',
                             short_title='from_content',
                             contributor='person_module/john')
    self.setDiscoveryOrder(['user_login', 'filename', 'content', 'input'])
    document = self.portal.restrictedTraverse(sequence.get('document_path'))
    self.discoverMetadata(document)
    self.checkMetadataOrder(document, expected_metadata)

  def stepReceiveEmail(self, sequence=None, sequence_list=None, **kw):
    """
      Email was sent in by someone to ERP5.
    """
    f = open(makeFilePath('email_from.txt'))
    document = self.receiveEmail(f.read())
    self.tic()

  def stepReceiveMultipleAttachmentsEmail(self, sequence=None,
                                          sequence_list=None, **kw):
    """
      Email was sent in by someone to ERP5.
    """
    f = open(makeFilePath('email_multiple_attachments.eml'))
    document = self.receiveEmail(f.read())
    self.tic()

  def stepVerifyEmailedMultipleDocumentsInitialContribution(self, sequence=None, sequence_list=None, **kw):
    """
      Verify contributed for initial time multiple document per email.
    """
    attachment_list, ingested_document = self.verifyEmailedMultipleDocuments()
    self.assertEqual('1', ingested_document.getRevision())

  def stepVerifyEmailedMultipleDocumentsMultipleContribution(self, sequence=None, sequence_list=None, **kw):
    """
      Verify contributed for initial time multiple document per email.
    """
    attachment_list, ingested_document = self.verifyEmailedMultipleDocuments()
    self.assertTrue(ingested_document.getRevision() > '1')

  def stepVerifyEmailedDocumentInitialContribution(self, sequence=None, sequence_list=None, **kw):
    """
      Verify contributed for initial time document per email.
    """
    attachment_list, ingested_document = self.verifyEmailedDocument()
    self.assertEqual('1', ingested_document.getRevision())

  def stepVerifyEmailedDocumentMultipleContribution(self, sequence=None, sequence_list=None, **kw):
    """
      Verify contributed for multiple times document per email.
    """
    attachment_list, ingested_document = self.verifyEmailedDocument()
    self.assertTrue(ingested_document.getRevision() > '1')

  def playSequence(self, step_list):
    sequence_list = SequenceList()
    sequence_string = ' '.join(step_list)
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def verifyEmailedMultipleDocuments(self):
    """
      Basic checks for verifying a mailed-in multiple documents.
    """
    # First, check document ingestion message
    ingestion_message = self.portal_catalog.getResultValue(
                                 portal_type='Document Ingestion Message',
                                 title='Multiple Attachments',
                                 source_title='John Doe')
    self.assertTrue(ingestion_message is not None)
    # Second, check attachments to ingested message
    attachment_list = ingestion_message.getAggregateValueList()
    self.assertEqual(len(attachment_list), 5)
    extension_reference_portal_type_map = {'DOC': 'Text',
                                           'JPG': 'Image',
                                           'ODT': 'Text',
                                           'PDF': 'PDF',
                                           'PPT': 'Presentation'}
    for sub_reference, portal_type in extension_reference_portal_type_map.items():
      ingested_document = self.portal_catalog.getResultValue(
                               portal_type=portal_type,
                               reference='TEST%s' %sub_reference,
                               language='en',
                               version='002')
      self.assertNotEqual(None, ingested_document)
      if ingested_document.isSupportBaseDataConversion():
        self.assertEqual('converted', ingested_document.getExternalProcessingState())
      # check aggregate between 'Document Ingestion Message' and ingested document
      self.assertIn(ingested_document, attachment_list)
    return attachment_list, ingested_document

  def verifyEmailedDocument(self):
    """
      Basic checks for verifying a mailed-in document
    """
    # First, check document ingestion message
    ingestion_message = self.portal_catalog.getResultValue(
                                 portal_type='Document Ingestion Message',
                                 title='A Test Mail',
                                 source_title='John Doe')
    self.assertTrue(ingestion_message is not None)

    # Second, check attachments to ingested message
    attachment_list = ingestion_message.getAggregateValueList()
    self.assertEqual(len(attachment_list), 1)

    # Third, check document is ingested properly
    ingested_document = self.portal_catalog.getResultValue(
                               portal_type='Text',
                               reference='MAIL',
                               language='en',
                               version='002')
    self.assertEqual('MAIL-en-002.doc', ingested_document.getFilename())
    self.assertEqual('converted', ingested_document.getExternalProcessingState())
    self.assertIn('magic', ingested_document.asText())

    # check aggregate between 'Document Ingestion Message' and ingested document
    self.assertEqual(attachment_list[0], ingested_document)
    return attachment_list, ingested_document

  ##################################
  ##  Tests
  ##################################

  def test_01_PreferenceSetup(self):
    """
      Make sure that preferences are set up properly and accessible
    """
    preference_tool = self.portal.portal_preferences
    self.assertEqual(preference_tool.getPreferredDocumentConversionServerUrlList(),
                     _getConversionServerUrlList())
    self.assertEqual(preference_tool.getPreferredDocumentFilenameRegularExpression(), FILENAME_REGULAR_EXPRESSION)
    self.assertEqual(preference_tool.getPreferredDocumentReferenceRegularExpression(), REFERENCE_REGULAR_EXPRESSION)

  def test_02_FileExtensionRegistry(self):
    """
      check if we successfully imported registry
      and that it has all the entries we need
    """
    reg = self.portal.portal_contribution_registry
    correct_type_mapping = {
            'doc' : 'Text',
            'txt' : 'Text',
            'odt' : 'Text',
            'sxw' : 'Text',
            'rtf' : 'Text',
            'gif' : 'Image',
            'jpg' : 'Image',
            'png' : 'Image',
            'bmp' : 'Image',
            'pdf' : 'PDF',
            'xls' : 'Spreadsheet',
            'ods' : 'Spreadsheet',
            'ppt' : 'Presentation',
            'odp' : 'Presentation',
            'sxi' : 'Presentation',
            'sxd' : 'Drawing',
            'xxx' : 'File',
          }
    for type, portal_type in correct_type_mapping.items():
      filename = 'aaa.' + type
      self.assertEqual(reg.findPortalTypeName(filename=filename),
                        portal_type)

  def test_03_TextDoc(self):
    """
      Test basic behaviour of a document:
      - create empty document
      - upload a file directly
      - upload a file using upload dialog
      - make sure revision was increased
      - check that it was properly converted
      - check if coordinates were extracted from file name
    """
    step_list = ['stepCleanUp'
                 ,'stepCreateTextDocument'
                 ,'stepCheckEmptyState'
                 ,'stepStraightUpload'
                 ,'stepCheckConvertingState'
                 ,'stepTic'
                 ,'stepCheckConvertedState'
                 ,'stepUploadFromViewForm'
                 ,'stepCheckConvertingState'
                 ,'stepTic'
                 ,'stepCheckConvertedState'
                ]
    self.playSequence(step_list)

  def test_04_MetadataExtraction(self):
    """
      Test metadata extraction from various sources:
      - from file name (doublecheck)
      - from user (by overwriting type-based method
                   and simulating the result)
      - from content (by overwriting type-based method
                      and simulating the result)
      - from file metadata

      NOTE: metadata of document (title, subject, description)
      are no longer retrieved and set upon conversion
    """
    step_list = [ 'stepCleanUp'
                 ,'stepUploadTextFromContributionTool'
                 ,'stepSetSimulatedDiscoveryScript'
                 ,'stepTic'
                 ,'stepTestMetadataSetting'
                ]
    self.playSequence(step_list)

  def test_041_MetadataEditing(self):
    """
      Check metadata in the object and in the ODF document
      Edit metadata on the object
      Download ODF, make sure it is changed
    """
    step_list = [ 'stepCleanUp'
                 ,'stepCreateTextDocument'
                 ,'stepUploadFromViewForm'
                 ,'stepCheckConvertingState'
                 ,'stepTic'
                 ,'stepCheckConvertedState'
                 ,'stepEditMetadata'
                 ,'stepCheckChangedMetadata'
                ]
    self.playSequence(step_list)

  #    Ingest various formats (xls, doc, sxi, ppt etc)
  #    Verify that they are successfully converted
  #    - have ODF data and contain magic word in SearchableText
  #    - or have text data and contain magic word in SearchableText
  #      TODO:
  #    - or were not moved in processing_status_workflow if the don't
  #      implement _convertToBase (e.g. Image)
  #    Verify that you can not upload file of the wrong format.

  def test_05_FormatIngestionText(self):
    step_list = ['stepCleanUp'
                 ,'stepCreateTextDocument'
                 ,'stepIngestTextFormats'
                ]
    self.playSequence(step_list)

  def test_05_FormatIngestionSpreadSheet(self):
    step_list = ['stepCleanUp'
                 ,'stepCreateSpreadsheetDocument'
                 ,'stepIngestSpreadsheetFormats'
                ]
    self.playSequence(step_list)

  def test_05_FormatIngestionPresentation(self):
    step_list = ['stepCleanUp'
                 ,'stepCreatePresentationDocument'
                 ,'stepIngestPresentationFormats'
                ]
    self.playSequence(step_list)

  def test_05_FormatIngestionDrawing(self):
    step_list = ['stepCleanUp'
                 ,'stepCreateDrawingDocument'
                 ,'stepIngestDrawingFormats'
                ]
    self.playSequence(step_list)

  def test_05_FormatIngestionPDF(self):
    step_list = ['stepCleanUp'
                 ,'stepCreatePDFDocument'
                 ,'stepIngestPDFFormats'
                ]
    self.playSequence(step_list)

  def test_05_FormatIngestionImage(self):
    step_list = ['stepCleanUp'
                 ,'stepCreateImageDocument'
                 ,'stepIngestImageFormats'
                ]
    self.playSequence(step_list)

  def test_05_FormatIngestionFile(self):
    step_list = ['stepCleanUp'
                 ,'stepCreateFileDocument'
                 ,'stepIngestFileFormats'
                ]
    self.playSequence(step_list)

  # Test generation of files in all possible formats
  # which means check if they have correct lists of available formats for export
  # actual generation is tested in oood tests
  # PDF and Image should be tested here
  def test_06_FormatGenerationText(self):
    step_list = [ 'stepCleanUp'
                 ,'stepCreateTextDocument'
                 ,'stepCheckTextDocumentExportList'
                ]
    self.playSequence(step_list)

  def test_06_FormatGenerationSpreadsheet(self):
    step_list = [ 'stepCleanUp'
                 ,'stepCreateSpreadsheetDocument'
                 ,'stepCheckSpreadsheetDocumentExportList'
                ]
    self.playSequence(step_list)

  def test_06_FormatGenerationPresentation(self):
    step_list = [ 'stepCleanUp'
                 ,'stepCreatePresentationDocument'
                 ,'stepCheckPresentationDocumentExportList'
                ]
    self.playSequence(step_list)

  def test_06_FormatGenerationDrawing(self):
    step_list = [ 'stepCleanUp'
                 ,'stepCreateDrawingDocument'
                 ,'stepCheckDrawingDocumentExportList'
                ]
    self.playSequence(step_list)

  def test_06_FormatGenerationPdf(self):
    step_list = [ 'stepCleanUp'
                 ,'stepCreatePDFDocument'
                 ,'stepExportPDF'
                 ,'stepTic'
                ]
    self.playSequence(step_list)

  def test_06_FormatGenerationImage(self):
    step_list = [ 'stepCleanUp'
                 ,'stepCreateImageDocument'
                 ,'stepExportImage'
                ]
    self.playSequence(step_list)

  def test_08_Cache(self):
    """
      I don't know how to verify how cache works
    """

  def test_09_Contribute(self):
    """
      Create content through portal_contributions
      - use newContent to ingest various types
        also to test content_type_registry setup
      - verify that
        - appropriate portal_types were created
        - the files were converted
        - metadata was read
    """
    step_list = [ 'stepCleanUp'
                 ,'stepContributeFileListWithNoType'
                 ,'stepCleanUp'
                 ,'stepContributeFileListWithType'
                ]
    self.playSequence(step_list)

  def test_10_MetadataSettingPreferenceOrder(self):
    """
      Set some metadata discovery scripts
      Contribute a document, let it get metadata using default setup
      (default is FUC)

      check that the right ones are there
      change preference order, check again
    """
    step_list = [ 'stepCleanUp'
                 ,'stepCreateTextDocument'
                 ,'stepStraightUpload'
                 ,'stepCheckConvertingState'
                 ,'stepTic'
                 ,'stepCheckConvertedState'
                 ,'stepSetSimulatedDiscoveryScriptForOrdering'
                 ,'stepCheckMetadataSettingOrderFICU'
                 ,'stepCreateTextDocument'
                 ,'stepStraightUpload'
                 ,'stepCheckConvertingState'
                 ,'stepTic'
                 ,'stepCheckConvertedState'
                 ,'stepSetSimulatedDiscoveryScriptForOrdering'
                 ,'stepCheckMetadataSettingOrderCUFI'
                 ,'stepCreateTextDocument'
                 ,'stepStraightUpload'
                 ,'stepCheckConvertingState'
                 ,'stepTic'
                 ,'stepCheckConvertedState'
                 ,'stepSetSimulatedDiscoveryScriptForOrdering'
                 ,'stepCheckMetadataSettingOrderUIFC'
                 ,'stepCreateTextDocument'
                 ,'stepStraightUpload'
                 ,'stepCheckConvertingState'
                 ,'stepTic'
                 ,'stepCheckConvertedState'
                 ,'stepSetSimulatedDiscoveryScriptForOrdering'
                 ,'stepCheckMetadataSettingOrderICUF'
                 ,'stepCreateTextDocument'
                 ,'stepStraightUpload'
                 ,'stepCheckConvertingState'
                 ,'stepTic'
                 ,'stepCheckConvertedState'
                 ,'stepSetSimulatedDiscoveryScriptForOrdering'
                 ,'stepCheckMetadataSettingOrderUFCI'
                ]
    self.playSequence(step_list)

  def test_11_EmailIngestion(self):
    """
      Simulate email piped to ERP5 by an MTA by uploading test email from file
      Check that document objects are created and appropriate data are set
      (owner, and anything discovered from user and mail body)
    """
    step_list = [ 'stepCleanUp'
                 # unknown sender
                 ,'stepReceiveEmail'
                 # create sender as Person object in ERP5
                 ,'stepCreatePerson'
                 # now a known sender
                 ,'stepReceiveEmail'
                 ,'stepVerifyEmailedDocumentInitialContribution'
                 # send one more time
                 ,'stepReceiveEmail'
                 ,'stepVerifyEmailedDocumentMultipleContribution'
                 # send email with multiple attachments
                 ,'stepReceiveMultipleAttachmentsEmail'
                 ,'stepVerifyEmailedMultipleDocumentsInitialContribution'
                 # send email with multiple attachments one more time
                 ,'stepReceiveMultipleAttachmentsEmail'
                 ,'stepVerifyEmailedMultipleDocumentsMultipleContribution'
                ]
    self.playSequence(step_list)

  def test_12_UploadTextFromContributionTool(self):
    """
      Make sure that when upload file from contribution tool, it creates a new
      document in document module. when reupload same filename file, then it
      does not create a new document and update existing document.
    """
    step_list = [ 'stepCleanUp'
                 ,'stepUploadTextFromContributionTool'
                 ,'stepCheckConvertingState'
                 ,'stepTic'
                 ,'stepCheckConvertedState'
                 ,'stepDiscoverFromFilename'
                 ,'stepTic'
                 ,'stepReuploadTextFromContributionTool'
                 ,'stepUploadAnotherTextFromContributionTool'
                ]
    self.playSequence(step_list)

  def stepUploadTextFromContributionToolWithNonASCIIFilename(self,
                                 sequence=None, sequence_list=None, **kw):
    """
      Upload a file from contribution.
    """
    f = makeFileUpload('TEST-en-002.doc', 'T&é@{T-en-002.doc')
    document = self.portal.portal_contributions.newContent(file=f)
    sequence.edit(document_path=document.getPath())
    self.commit()

  def stepDiscoverFromFilenameWithNonASCIIFilename(self,
                                 sequence=None, sequence_list=None, **kw):
    """
      Upload a file using contribution tool. This should trigger metadata
      discovery and we should have basic coordinates immediately,
      from first stage.
    """
    context = self.portal.restrictedTraverse(sequence.get('document_path'))
    filename = 'T&é@{T-en-002.doc'
    # First make sure the regular expressions work
    property_dict = context.getPropertyDictFromFilename(filename)
    self.assertEqual(property_dict['reference'], 'T&é@{T')
    self.assertEqual(property_dict['language'], 'en')
    self.assertEqual(property_dict['version'], '002')
    # Then make sure content discover works
    # XXX - This part must be extended
    property_dict = context.getPropertyDictFromContent()
    self.assertEqual(property_dict['title'], 'title')
    self.assertEqual(property_dict['description'], 'comments')
    self.assertEqual(property_dict['subject_list'], ['keywords'])
    # Then make sure metadata discovery works
    self.assertEqual(context.getReference(), 'T&é@{T')
    self.assertEqual(context.getLanguage(), 'en')
    self.assertEqual(context.getVersion(), '002')
    self.assertEqual(context.getFilename(), filename)

  def test_13_UploadTextFromContributionToolWithNonASCIIFilename(self):
    """
      Make sure that when upload file from contribution tool, it creates a new
      document in document module. when reupload same filename file, then it
      does not create a new document and update existing document.
    """
    step_list = [ 'stepCleanUp'
                 ,'stepUploadTextFromContributionToolWithNonASCIIFilename'
                 ,'stepTic'
                 ,'stepDiscoverFromFilenameWithNonASCIIFilename'
                ]
    self.playSequence(step_list)

  def test_14_ContributionToolIndexation(self):
    """
    Check that contribution tool is correctly indexed after business template
    installation.
    Check that contribution tool is correctly indexed by ERP5Site_reindexAll.
    """
    portal = self.portal

    contribution_tool = getToolByName(portal, 'portal_contributions')
    self.assertEqual(1,
        len(portal.portal_catalog(path=contribution_tool.getPath())))

    # Clear catalog
    portal_catalog = self.getCatalogTool()
    portal_catalog.manage_catalogClear()
    # Reindex all
    portal.ERP5Site_reindexAll()
    self.tic()
    self.assertEqual(1,
        len(portal.portal_catalog(path=contribution_tool.getPath())))

  def test_15_TestFilenameDiscovery(self):
    """Test that filename is well set in filename
    - filename can we discovery from file
    - filename can be pass as argument by the user
    """
    portal = self.portal
    contribution_tool = getToolByName(portal, 'portal_contributions')
    file_object = makeFileUpload('TEST-en-002.doc')
    document = contribution_tool.newContent(file=file_object)
    self.assertEqual(document.getFilename(), 'TEST-en-002.doc')
    my_filename = 'Something.doc'
    document = contribution_tool.newContent(file=file_object,
                                            filename=my_filename)
    self.tic()
    self.assertEqual(document.getFilename(), my_filename)

  def test_16_TestMetadataDiscoveryFromUserLogin(self):
    """
      Test that  user_login is used to discover meta data (group, function, etc.. from Assignment)
    """
    portal = self.portal
    contribution_tool = getToolByName(portal, 'portal_contributions')
    # create an user to simulate upload from him
    user = self.createUser(reference='contributor1')
    assignment = self.createUserAssignment(user, \
                                           dict(group='anybody',
                                                function='musician/wind/saxophone',
                                                site='arctic/spitsbergen'))
    portal.document_module.manage_setLocalRoles(user.Person_getUserId(), ['Assignor',])
    self.tic()
    file_object = makeFileUpload('TEST-en-002.doc')
    document = contribution_tool.newContent(file=file_object)
    document.discoverMetadata(document.getFilename(), user.Person_getUserId())
    self.tic()
    self.assertEqual(document.getFilename(), 'TEST-en-002.doc')
    self.assertEqual('anybody', document.getGroup())
    self.assertEqual(None, document.getFunction())
    self.assertEqual(None, document.getSite())

  def test_TestMetadataDiscoveryFromUserLoginHigherGroup(self):
    portal = self.portal
    contribution_tool = getToolByName(portal, 'portal_contributions')

    user = self.createUser(reference='contributor3')
    self.createUserAssignment(user, dict(group='anybody/a1',))
    self.createUserAssignment(user, dict(group='anybody/a2',))
    self.createUserAssignment(user, dict(group='anybody',))

    other_user = self.createUser(reference='contributor2')
    self.createUserAssignment(other_user, dict(group='anybody/a1',))
    self.createUserAssignment(other_user, dict(group='anybody/a2',))

    portal.document_module.manage_setLocalRoles(other_user.Person_getUserId(), ['Assignor',])
    self.tic()
    file_object = makeFileUpload('TEST-en-002.doc')
    document = contribution_tool.newContent(file=file_object)

    # We only consider the higher group of assignments
    document.discoverMetadata(document.getFilename(), user.Person_getUserId())
    self.tic()
    self.assertEqual(document.getFilename(), 'TEST-en-002.doc')
    self.assertEqual(['anybody'], document.getGroupList())

    document.discoverMetadata(document.getFilename(), other_user.Person_getUserId())
    self.assertEqual(sorted(document.getGroupList()), ['anybody/a1', 'anybody/a2'])

  def test_IngestionConfigurationByTypeBasedMethod_usecase1(self):
    """How to configure meta data discovery so that each time a file
    with same URL is uploaded, a new document is created with same reference
    but increased version ?
    """
    input_script_id = 'Document_getPropertyDictFromContent'
    python_code = """from Products.CMFCore.utils import getToolByName
portal = context.getPortalObject()
information = context.getContentInformation()

result = {}
property_id_list = context.propertyIds()
for k, v in information.items():
  key = k.lower()
  if v:
    if isinstance(v, unicode):
      v = v.encode('utf-8')
    if key in property_id_list:
      if key == 'reference':
        pass # XXX - We can not trust reference on getContentInformation
      else:
        result[key] = v
    elif key == 'author':
      p = context.portal_catalog.getResultValue(title=v, portal_type='Person')
      if p is not None:
        result['contributor'] = p.getRelativeUrl()
    elif key == 'keywords':
      result['subject_list'] = v.split()

reference = context.asNormalisedURL()

result['reference'] = reference
id_group = ('dms_version_generator', reference)
result['version'] = '%.5d' % (portal.portal_ids.generateNewId(id_group=id_group, default=1))
return result
"""
    self.newPythonScript(input_script_id, '', python_code)
    document_to_ingest = self.portal.portal_contributions.newContent(
                                                          portal_type='File',
                                                          filename='toto.txt',
                                                          data='Hello World!')
    document_to_ingest.publish()
    self.tic()
    url = document_to_ingest.absolute_url() + '/getData'
    first_doc = self.portal.portal_contributions.newContent(url=url)
    self.tic()
    self.assertEqual(first_doc.getPortalType(), 'Text')
    self.assertEqual(first_doc.getContentType(), 'text/plain')
    self.assertEqual(first_doc.getReference(), first_doc.asNormalisedURL())
    self.assertEqual(first_doc.getVersion(), '00001')
    self.assertEqual(first_doc.asURL(), url)
    second_doc = self.portal.portal_contributions.newContent(url=url)
    self.tic()
    self.assertEqual(second_doc.getPortalType(), 'Text')
    self.assertEqual(second_doc.getContentType(), 'text/plain')
    self.assertEqual(second_doc.getReference(), second_doc.asNormalisedURL())
    self.assertEqual(second_doc.getVersion(), '00002')
    self.assertEqual(second_doc.asURL(), url)

    document_to_ingest2 = self.portal.portal_contributions.newContent(
                                                          portal_type='File',
                                                          filename='toto.txt',
                                                          data='Hello World!')
    document_to_ingest2.publish()
    self.tic()
    url2 = document_to_ingest2.absolute_url() + '/getData'
    first_doc = self.portal.portal_contributions.newContent(url=url2)
    self.tic()
    self.assertEqual(first_doc.getPortalType(), 'Text')
    self.assertEqual(first_doc.getContentType(), 'text/plain')
    self.assertEqual(first_doc.getReference(), first_doc.asNormalisedURL())
    self.assertEqual(first_doc.getVersion(), '00001')
    self.assertEqual(first_doc.asURL(), url2)
    second_doc = self.portal.portal_contributions.newContent(url=url2)
    self.tic()
    self.assertEqual(second_doc.getPortalType(), 'Text')
    self.assertEqual(second_doc.getContentType(), 'text/plain')
    self.assertEqual(second_doc.getReference(), second_doc.asNormalisedURL())
    self.assertEqual(second_doc.getVersion(), '00002')
    self.assertEqual(second_doc.asURL(), url2)

  def test_IngestionConfigurationByTypeBasedMethod_usecase2(self):
    """How to configure meta data discovery so that each time a file
    with same URL  is uploaded, a new document is created
    with same reference but same version ?
    """
    input_script_id = 'Document_getPropertyDictFromContent'
    python_code = """from Products.CMFCore.utils import getToolByName
portal = context.getPortalObject()
information = context.getContentInformation()

result = {}
property_id_list = context.propertyIds()
for k, v in information.items():
  key = k.lower()
  if v:
    if isinstance(v, unicode):
      v = v.encode('utf-8')
    if key in property_id_list:
      if key == 'reference':
        pass # XXX - We can not trust reference on getContentInformation
      else:
        result[key] = v
    elif key == 'author':
      p = context.portal_catalog.getResultValue(title=v, portal_type='Person')
      if p is not None:
        result['contributor'] = p.getRelativeUrl()
    elif key == 'keywords':
      result['subject_list'] = v.split()

reference = context.asNormalisedURL()
result['reference'] = reference
return result
"""
    self.newPythonScript(input_script_id, '', python_code)
    document_to_ingest = self.portal.portal_contributions.newContent(
                                                          portal_type='File',
                                                          filename='toto.txt',
                                                          data='Hello World!')
    document_to_ingest.publish()
    self.tic()
    url = document_to_ingest.absolute_url() + '/getData'
    first_doc = self.portal.portal_contributions.newContent(url=url)
    self.tic()
    self.assertEqual(first_doc.getPortalType(), 'Text')
    self.assertEqual(first_doc.getContentType(), 'text/plain')
    self.assertEqual(first_doc.getReference(), first_doc.asNormalisedURL())
    self.assertEqual(first_doc.getVersion(), '001')
    self.assertEqual(first_doc.asURL(), url)
    second_doc = self.portal.portal_contributions.newContent(url=url)
    self.tic()
    self.assertEqual(second_doc.getPortalType(), 'Text')
    self.assertEqual(second_doc.getContentType(), 'text/plain')
    self.assertEqual(second_doc.getReference(), second_doc.asNormalisedURL())
    self.assertEqual(second_doc.getVersion(), '001')
    self.assertEqual(second_doc.asURL(), url)

    document_to_ingest2 = self.portal.portal_contributions.newContent(
                                                          portal_type='File',
                                                          filename='toto.txt',
                                                          data='Hello World!')
    document_to_ingest2.publish()
    self.tic()
    url2 = document_to_ingest2.absolute_url() + '/getData'
    first_doc = self.portal.portal_contributions.newContent(url=url2)
    self.tic()
    self.assertEqual(first_doc.getPortalType(), 'Text')
    self.assertEqual(first_doc.getContentType(), 'text/plain')
    self.assertEqual(first_doc.getReference(), first_doc.asNormalisedURL())
    self.assertEqual(first_doc.getVersion(), '001')
    self.assertEqual(first_doc.asURL(), url2)
    second_doc = self.portal.portal_contributions.newContent(url=url2)
    self.tic()
    self.assertEqual(second_doc.getPortalType(), 'Text')
    self.assertEqual(second_doc.getContentType(), 'text/plain')
    self.assertEqual(second_doc.getReference(), second_doc.asNormalisedURL())
    self.assertEqual(second_doc.getVersion(), '001')
    self.assertEqual(second_doc.asURL(), url2)

  def test_IngestionConfigurationByTypeBasedMethod_usecase3(self):
    """How to discover metadata so that each new document
    has a new reference which is generated automatically
    as an increase sequence of numbers ?
    """
    input_script_id = 'Document_finishIngestion'
    python_code = """from Products.CMFCore.utils import getToolByName
portal = context.getPortalObject()
portal_ids = getToolByName(portal, 'portal_ids')
id_group = 'dms_reference_generator3'
reference = 'I CHOOSED THIS REFERENCE %s' % portal.portal_ids.generateNewId(id_group=id_group)
context.setReference(reference)
"""
    self.newPythonScript(input_script_id, '', python_code)
    document_to_ingest = self.portal.portal_contributions.newContent(
                                                          portal_type='File',
                                                          filename='toto.txt',
                                                          data='Hello World!')
    document_to_ingest.publish()
    self.tic()
    url = document_to_ingest.absolute_url() + '/getData'
    first_doc = self.portal.portal_contributions.newContent(url=url)
    self.tic()
    self.assertEqual(first_doc.getPortalType(), 'Text')
    self.assertEqual(first_doc.getContentType(), 'text/plain')
    self.assertEqual(first_doc.getReference(), 'I CHOOSED THIS REFERENCE 1')
    self.assertEqual(first_doc.getVersion(), '001')
    self.assertEqual(first_doc.asURL(), url)
    second_doc = self.portal.portal_contributions.newContent(url=url)
    self.tic()
    self.assertEqual(second_doc.getPortalType(), 'Text')
    self.assertEqual(second_doc.getContentType(), 'text/plain')
    self.assertEqual(second_doc.getReference(), 'I CHOOSED THIS REFERENCE 2')
    self.assertEqual(second_doc.getVersion(), '001')
    self.assertEqual(second_doc.asURL(), url)

    document_to_ingest2 = self.portal.portal_contributions.newContent(
                                                          portal_type='File',
                                                          filename='toto.txt',
                                                          data='Hello World!')
    document_to_ingest2.publish()
    self.tic()
    self.assertEqual(document_to_ingest2.getReference(),
                      'I CHOOSED THIS REFERENCE 3')

    url2 = document_to_ingest2.absolute_url() + '/getData'
    first_doc = self.portal.portal_contributions.newContent(url=url2)
    self.tic()
    self.assertEqual(first_doc.getPortalType(), 'Text')
    self.assertEqual(first_doc.getContentType(), 'text/plain')
    self.assertEqual(first_doc.getReference(), 'I CHOOSED THIS REFERENCE 4')
    self.assertEqual(first_doc.getVersion(), '001')
    self.assertEqual(first_doc.asURL(), url2)
    second_doc = self.portal.portal_contributions.newContent(url=url2)
    self.tic()
    self.assertEqual(second_doc.getPortalType(), 'Text')
    self.assertEqual(second_doc.getContentType(), 'text/plain')
    self.assertEqual(second_doc.getReference(), 'I CHOOSED THIS REFERENCE 5')
    self.assertEqual(second_doc.getVersion(), '001')
    self.assertEqual(second_doc.asURL(), url2)

  def test_IngestionConfigurationByTypeBasedMethod_usecase4(self):
    """How to configure meta data discovery so that each time a file
    with same URL is uploaded, a new document is created
    with same reference (generated automatically as an
    increase sequence of numbers) but increased version ?
    """
    input_script_id = 'Document_getPropertyDictFromContent'
    python_code = """from Products.CMFCore.utils import getToolByName
portal = context.getPortalObject()
information = context.getContentInformation()

result = {}
property_id_list = context.propertyIds()
for k, v in information.items():
  key = k.lower()
  if v:
    if isinstance(v, unicode):
      v = v.encode('utf-8')
    if key in property_id_list:
      if key == 'reference':
        pass # XXX - We can not trust reference on getContentInformation
      else:
        result[key] = v
    elif key == 'author':
      p = context.portal_catalog.getResultValue(title=v, portal_type='Person')
      if p is not None:
        result['contributor'] = p.getRelativeUrl()
    elif key == 'keywords':
      result['subject_list'] = v.split()

url = context.asNormalisedURL()
portal_url_registry = getToolByName(context.getPortalObject(),
                                    'portal_url_registry')
try:
  reference = portal_url_registry.getReferenceFromURL(url)
except KeyError:
  id_group = 'dms_reference_generator4'
  reference = 'I CHOOSED THIS REFERENCE %s' % portal.portal_ids.generateNewId(id_group=id_group)
result['reference'] = reference
id_group = ('dms_version_generator', reference)
result['version'] = '%.5d' % (portal.portal_ids.generateNewId(id_group=id_group, default=1))
return result
"""
    self.newPythonScript(input_script_id, '', python_code)
    document_to_ingest = self.portal.portal_contributions.newContent(
                                                          portal_type='File',
                                                          filename='toto.txt',
                                                          data='Hello World!')
    document_to_ingest.publish()
    self.tic()
    url = document_to_ingest.absolute_url() + '/getData'
    first_doc = self.portal.portal_contributions.newContent(url=url)
    self.tic()
    self.assertEqual(first_doc.getPortalType(), 'Text')
    self.assertEqual(first_doc.getContentType(), 'text/plain')
    self.assertEqual(first_doc.getReference(), 'I CHOOSED THIS REFERENCE 1')
    self.assertEqual(first_doc.getVersion(), '00001')
    self.assertEqual(first_doc.asURL(), url)
    second_doc = self.portal.portal_contributions.newContent(url=url)
    self.tic()
    self.assertEqual(second_doc.getPortalType(), 'Text')
    self.assertEqual(second_doc.getContentType(), 'text/plain')
    self.assertEqual(second_doc.getReference(), 'I CHOOSED THIS REFERENCE 1')
    self.assertEqual(second_doc.getVersion(), '00002')
    self.assertEqual(second_doc.asURL(), url)

    document_to_ingest2 = self.portal.portal_contributions.newContent(
                                                          portal_type='File',
                                                          filename='toto.txt',
                                                          data='Hello World!')
    document_to_ingest2.publish()
    self.tic()
    self.assertEqual(document_to_ingest2.getReference(),
                      'I CHOOSED THIS REFERENCE 2')

    url2 = document_to_ingest2.absolute_url() + '/getData'
    first_doc = self.portal.portal_contributions.newContent(url=url2)
    self.tic()
    self.assertEqual(first_doc.getPortalType(), 'Text')
    self.assertEqual(first_doc.getContentType(), 'text/plain')
    self.assertEqual(first_doc.getReference(), 'I CHOOSED THIS REFERENCE 3')
    self.assertEqual(first_doc.getVersion(), '00001')
    self.assertEqual(first_doc.asURL(), url2)
    second_doc = self.portal.portal_contributions.newContent(url=url2)
    self.tic()
    self.assertEqual(second_doc.getPortalType(), 'Text')
    self.assertEqual(second_doc.getContentType(), 'text/plain')
    self.assertEqual(second_doc.getReference(), 'I CHOOSED THIS REFERENCE 3')
    self.assertEqual(second_doc.getVersion(), '00002')
    self.assertEqual(second_doc.asURL(), url2)

  def test_IngestionConfigurationByTypeBasedMethod_usecase5(self):
    """How to configure meta data discovery so that each time a file
    with same URL is uploaded, a new document is created
    with same reference (generated automatically as
    an increase sequence of numbers) but same version?
    """
    input_script_id = 'Document_getPropertyDictFromContent'
    python_code = """from Products.CMFCore.utils import getToolByName
portal = context.getPortalObject()
information = context.getContentInformation()

result = {}
property_id_list = context.propertyIds()
for k, v in information.items():
  key = k.lower()
  if v:
    if isinstance(v, unicode):
      v = v.encode('utf-8')
    if key in property_id_list:
      if key == 'reference':
        pass # XXX - We can not trust reference on getContentInformation
      else:
        result[key] = v
    elif key == 'author':
      p = context.portal_catalog.getResultValue(title=v, portal_type='Person')
      if p is not None:
        result['contributor'] = p.getRelativeUrl()
    elif key == 'keywords':
      result['subject_list'] = v.split()

url = context.asNormalisedURL()
portal_url_registry = getToolByName(context.getPortalObject(),
                                    'portal_url_registry')
try:
  reference = portal_url_registry.getReferenceFromURL(url)
except KeyError:
  id_group = 'dms_reference_generator5'
  reference = 'I CHOOSED THIS REFERENCE %s' % portal.portal_ids.generateNewId(id_group=id_group)
result['reference'] = reference
return result
"""
    self.newPythonScript(input_script_id, '', python_code)
    document_to_ingest = self.portal.portal_contributions.newContent(
                                                          portal_type='File',
                                                          filename='toto.txt',
                                                          data='Hello World!')
    document_to_ingest.publish()
    self.tic()

    url = document_to_ingest.absolute_url() + '/getData'
    first_doc = self.portal.portal_contributions.newContent(url=url)
    self.tic()
    self.assertEqual(first_doc.getPortalType(), 'Text')
    self.assertEqual(first_doc.getContentType(), 'text/plain')
    self.assertEqual(first_doc.getReference(), 'I CHOOSED THIS REFERENCE 1')
    self.assertEqual(first_doc.getVersion(), '001')
    self.assertEqual(first_doc.asURL(), url)
    second_doc = self.portal.portal_contributions.newContent(url=url)
    self.tic()
    self.assertEqual(second_doc.getPortalType(), 'Text')
    self.assertEqual(second_doc.getContentType(), 'text/plain')
    self.assertEqual(second_doc.getReference(), 'I CHOOSED THIS REFERENCE 1')
    self.assertEqual(second_doc.getVersion(), '001')
    self.assertEqual(second_doc.asURL(), url)

    document_to_ingest2 = self.portal.portal_contributions.newContent(
                                                          portal_type='File',
                                                          filename='toto.txt',
                                                          data='Hello World!')
    document_to_ingest2.publish()
    self.tic()
    self.assertEqual(document_to_ingest2.getReference(),
                      'I CHOOSED THIS REFERENCE 2')

    url2 = document_to_ingest2.absolute_url() + '/getData'
    first_doc = self.portal.portal_contributions.newContent(url=url2)
    self.tic()
    self.assertEqual(first_doc.getPortalType(), 'Text')
    self.assertEqual(first_doc.getContentType(), 'text/plain')
    self.assertEqual(first_doc.getReference(), 'I CHOOSED THIS REFERENCE 3')
    self.assertEqual(first_doc.getVersion(), '001')
    self.assertEqual(first_doc.asURL(), url2)
    second_doc = self.portal.portal_contributions.newContent(url=url2)
    self.tic()
    self.assertEqual(second_doc.getPortalType(), 'Text')
    self.assertEqual(second_doc.getContentType(), 'text/plain')
    self.assertEqual(second_doc.getReference(), 'I CHOOSED THIS REFERENCE 3')
    self.assertEqual(second_doc.getVersion(), '001')
    self.assertEqual(second_doc.asURL(), url2)

  def test_IngestionConfigurationByTypeBasedMethod_usecase6(self):
    """How to configure meta data discovery so that a Spreadsheet
    as a application/octet-stream without explicit extension, become
    a Spreadsheet ?
    """
    path = makeFilePath('import_region_category.ods')
    data = open(path, 'r').read()

    document = self.portal.portal_contributions.newContent(filename='toto',
                                                  data=data,
                                                  reference='Custom.Reference')
    self.tic()# Discover metadata will delete first ingested document
    # then reingest new one with appropriate portal_type
    result_list = self.portal.portal_catalog(reference='Custom.Reference')
    self.assertEqual(len(result_list), 1)
    self.assertEqual(result_list[0].getPortalType(), 'Spreadsheet')

  def test_IngestionConfigurationByTypeBasedMethod_usecase7(self):
    """How to reingest a published document, by a user action ?
    If after a while the user decide to change the portal_type of a
    published document , File => Text ?
    """
    module = self.portal.document_module
    document = module.newContent(portal_type='File',
                                 property_which_doesnot_exists='Foo',
                                 data='Hello World!',
                                 filename='toto.txt')
    document.publish()
    self.tic()
    document.edit(title='One title', reference='EFAA')
    self.tic()
    # Now change it to a Text portal_type
    new_doc = document.migratePortalType('Text')
    self.tic()
    self.assertEqual(new_doc.getPortalType(), 'Text')
    self.assertEqual(new_doc.getProperty('property_which_doesnot_exists'),
                                          'Foo')
    self.assertEqual(new_doc.getTitle(), 'One title')
    self.assertEqual(new_doc.getReference(), 'EFAA')
    self.assertEqual(new_doc.getValidationState(), 'published')
    self.assertEqual(new_doc.getData(), 'Hello World!')

    # Migrate a document with url property
    url = new_doc.absolute_url() + '/getData'
    document = self.portal.portal_contributions.newContent(url=url)
    document.submit()
    self.tic()
    self.assertEqual(document.getPortalType(), 'Text')
    # Change it to File
    new_doc = document.migratePortalType('File')
    self.assertEqual(new_doc.getPortalType(), 'File')
    self.assertEqual(new_doc.asURL(), url)
    self.assertEqual(new_doc.getData(), 'Hello World!')
    self.assertEqual(new_doc.getValidationState(), 'submitted')

  def test_ContributionTool_isURLIngestionPermitted(self):
    # default behavior when no type based method is to refuse ingestion
    with mock.patch.object(
        self.portal.portal_contributions.__class__,
        '_getTypeBasedMethod',
        return_value=None,
      ):
      with self.assertRaisesRegex(Unauthorized, "URL ingestion not allowed"):
        self.portal.portal_contributions.newContent(url='https://www.erp5.com')

    # and it can be customized by script
    self.portal.portal_skins.custom.ContributionTool_isURLIngestionPermitted.ZPythonScript_edit(
      'url', 'return url == "https://www.erp5.com"',
    )
    self.portal.portal_contributions.newContent(url="https://www.erp5.com")
    self.tic()
    for url in (
        "https://www.erp5.com/", # with trailing slash
        "https://www.erp5.com/path",
        "https://www.erp5.com/?query",
        "https://www.nexedi.com/",
        "file:///tmp",
        "/tmp",
      ):
      with self.assertRaisesRegex(Unauthorized, "URL ingestion not allowed"):
        self.portal.portal_contributions.newContent(url=url)
    self.tic()

  def test_User_Portal_Type_parameter_is_honoured(self):
    """Check that given portal_type is always honoured
    """
    path = makeFilePath('import_region_category.xls')
    data = open(path, 'r').read()

    document = self.portal.portal_contributions.newContent(
                                      filename='import_region_category.xls',
                                      data=data,
                                      content_type='application/vnd.ms-excel',
                                      reference='I.want.a.pdf',
                                      portal_type='PDF')
    self.tic()# Discover metadata will try change the portal_type
    # but user decision take precedence: PDF must be created
    result_list = self.portal.portal_catalog(reference='I.want.a.pdf')
    self.assertEqual(len(result_list), 1)
    self.assertEqual(result_list[0].getPortalType(), 'PDF')

  def test_User_ID_parameter_is_honoured(self):
    """Check that given id is always honoured
    """
    path = makeFilePath('import_region_category.xls')
    data = open(path, 'r').read()

    document = self.portal.portal_contributions.newContent(
                                      id='this_id',
                                      filename='import_region_category.xls',
                                      data=data,
                                      content_type='application/vnd.ms-excel',
                                      reference='I.want.a.pdf',
                                      portal_type='PDF')
    self.tic()
    result_list = self.portal.portal_catalog(reference='I.want.a.pdf',
                                             id='this_id')
    self.assertEqual(len(result_list), 1)
    self.assertRaises(BadRequest,
                      self.portal.portal_contributions.newContent,
                      id='this_id',
                      filename='import_region_category.xls',
                      data=data,
                      content_type='application/vnd.ms-excel',
                      reference='I.want.a.pdf',
                      portal_type='PDF')

  def test_newContent_trough_http(self):
    filename = 'import_region_category.xls'
    path = makeFilePath(filename)
    data = open(path, 'r').read()
    reference = 'ITISAREFERENCE'

    portal_url = self.portal.absolute_url()
    url_split = six.moves.urllib.parse.urlsplit(portal_url)
    url_dict = dict(protocol=url_split[0],
                    hostname=url_split[1])
    uri = '%(protocol)s://%(hostname)s' % url_dict

    push_url = '%s%s/newContent' % (uri, self.portal.portal_contributions.getPath(),)
    request = six.moves.urllib.request.Request(push_url, six.moves.urllib.parse.urlencode(
                                        {'data': data,
                                        'filename': filename,
                                        'reference': reference,
                                        'disable_cookie_login__': 1,
                                        }), headers={
       'Authorization': 'Basic %s' %
         base64.b64encode('ERP5TypeTestCase:')
      })
    # disable_cookie_login__ is required to force zope to raise Unauthorized (401)
    # then HTTPDigestAuthHandler can perform HTTP Authentication
    response = six.moves.urllib.request.urlopen(request)
    self.assertEqual(response.getcode(), six.moves.http_client.OK)
    self.tic()
    document = self.portal.portal_catalog.getResultValue(portal_type='Spreadsheet',
                                                         reference=reference)
    self.assertTrue(document is not None)
    self.assertEqual(document.getData(), data)

  def test_publication_state_in_Base_viewNewFileDialog(self):
    """
      Checks that with type based method returning 'published',
      we can upload with Base_viewNewFileDialog and declare the document as 'published'
    """
    person = self.portal.person_module.newContent(portal_type="Person")
    method_id = "Person_getPreferredAttachedDocumentPublicationState"
    skin_folder = self.portal.portal_skins.custom

    if not getattr(skin_folder, method_id, False):
      createZODBPythonScript(skin_folder, method_id, "", "return")
    skin_folder[method_id].ZPythonScript_edit('', 'return ""')
    self.tic()

    item_list = person.Base_viewNewFileDialog.your_publication_state.get_value("items")
    self.assertEqual(
      item_list,
      [('', ''), ('Draft', 'draft'), ('Shared', 'shared'), ('Released', 'released')])

    skin_folder[method_id].ZPythonScript_edit('', 'return None')
    self.tic()
    item_list = person.Base_viewNewFileDialog.your_publication_state.get_value("items")
    self.assertEqual(
      item_list,
      [('', ''), ('Draft', 'draft'), ('Shared', 'shared'), ('Released', 'released')])

    skin_folder[method_id].ZPythonScript_edit('', 'return "published"')
    self.tic()
    item_list = person.Base_viewNewFileDialog.your_publication_state.get_value("items")
    self.assertEqual(
      item_list, [
        ('', ''), ('Draft', 'draft'), ('Shared', 'shared'),
        ('Released', 'released'), ('Published', 'published')
      ])
    # clean up and check if we don't have the script and published state in the list
    removeZODBPythonScript(skin_folder, method_id)
    self.tic()
    self.assertEqual(
      person.getTypeBasedMethod('getPreferredAttachedDocumentPublicationSection').getId(),
      "Base_getPreferredAttachedDocumentPublicationSection"
    )
    self.portal.changeSkin(None)
    item_list = person.Base_viewNewFileDialog.your_publication_state.get_value("items")
    self.assertEqual(
      item_list,
      [('', ''), ('Draft', 'draft'), ('Shared', 'shared'), ('Released', 'released')])


class Base_contributeMixin:
  """Tests for Base_contribute script.
  """
  def test_Base_contribute(self):
    """
      Test contributing a file and attaching it to context.
    """
    person = self.portal.person_module.newContent(portal_type='Person')
    contributed_document = person.Base_contribute(
                                     portal_type=None,
                                     title=None,
                                     reference=None,
                                     short_title=None,
                                     language=None,
                                     version=None,
                                     description=None,
                                     attach_document_to_context=True,
                                     file=makeFileUpload('TEST-en-002.odt'))
    self.assertEqual('Text', contributed_document.getPortalType())
    self.tic()
    document_list = person.getFollowUpRelatedValueList()
    self.assertEqual(1, len(document_list))
    document = document_list[0]
    self.assertEqual('converted', document.getExternalProcessingState())
    self.assertEqual('Text', document.getPortalType())
    self.assertEqual('title', document.getTitle())
    self.assertEqual(contributed_document, document)

  def test_Base_contribute_empty(self):
    """
      Test contributing an empty file and attaching it to context.
    """
    person = self.portal.person_module.newContent(portal_type='Person')
    empty_file_upload = ZPublisher.HTTPRequest.FileUpload(FieldStorage(
                            fp=io.BytesIO(),
                            environ=dict(REQUEST_METHOD='PUT'),
                            headers={"content-disposition":
                              "attachment; filename=empty;"}))

    contributed_document = person.Base_contribute(
                                    portal_type=None,
                                    title=None,
                                    reference=None,
                                    short_title=None,
                                    language=None,
                                    version=None,
                                    description=None,
                                    attach_document_to_context=True,
                                    file=empty_file_upload)
    self.tic()
    document_list = person.getFollowUpRelatedValueList()
    self.assertEqual(1, len(document_list))
    document = document_list[0]
    self.assertEqual('File', document.getPortalType())
    self.assertEqual(contributed_document, document)

  def test_Base_contribute_forced_type(self):
    """Test contributing while forcing the portal type.
    """
    person = self.portal.person_module.newContent(portal_type='Person')
    contributed_document = person.Base_contribute(
                                     portal_type='PDF',
                                     file=makeFileUpload('TEST-en-002.odt'))
    self.assertEqual('PDF', contributed_document.getPortalType())

  def test_Base_contribute_input_parameter_dict(self):
    """Test contributing while entering input parameters.
    """
    person = self.portal.person_module.newContent(portal_type='Person')
    contributed_document = person.Base_contribute(
                                     title='user supplied title',
                                     file=makeFileUpload('TEST-en-002.pdf'))
    self.tic()
    self.assertEqual('user supplied title', contributed_document.getTitle())

  def test_Base_contribute_publication_state(self):
    """Test contributing and choosing the publication state
    """
    person = self.portal.person_module.newContent(portal_type='Person')
    contributed_document = person.Base_contribute(
          publication_state=None,
          # we use as_name, to prevent regular expression from detecting a
          # reference during ingestion, so that we can upload multiple documents
          # in one test.
          file=makeFileUpload('TEST-en-002.pdf', as_name='doc.pdf'))
    self.tic()
    self.assertEqual(contributed_document.getValidationState(), 'draft')
    contributed_document.setReference(None)
    self.tic()

    contributed_document = person.Base_contribute(
          publication_state='shared',
          synchronous_metadata_discovery=False,
          file=makeFileUpload('TEST-en-002.pdf', as_name='doc.pdf'))
    self.tic()
    self.assertEqual(contributed_document.getValidationState(), 'shared')
    contributed_document.setReference(None)
    self.tic()

    contributed_document = person.Base_contribute(
          publication_state='shared',
          synchronous_metadata_discovery=True,
          file=makeFileUpload('TEST-en-002.pdf', as_name='doc.pdf'))
    self.tic()
    self.assertEqual(contributed_document.getValidationState(), 'shared')
    contributed_document.setReference(None)
    self.tic()

    contributed_document = person.Base_contribute(
          publication_state='released',
          synchronous_metadata_discovery=False,
          file=makeFileUpload('TEST-en-002.pdf', as_name='doc.pdf'))
    self.tic()
    self.assertEqual(contributed_document.getValidationState(), 'released')
    contributed_document.setReference(None)
    self.tic()

    contributed_document = person.Base_contribute(
          publication_state='released',
          synchronous_metadata_discovery=True,
          file=makeFileUpload('TEST-en-002.pdf', as_name='doc.pdf'))
    self.tic()
    self.assertEqual(contributed_document.getValidationState(), 'released')
    contributed_document.setReference(None)
    self.tic()

    contributed_document = person.Base_contribute(
      synchronous_metadata_discovery=False,
      publication_state='published',
      file=makeFileUpload('TEST-en-002.pdf', as_name='doc.pdf'))
    self.tic()
    self.assertEqual(contributed_document.getValidationState(), 'published')
    contributed_document.setReference(None)
    self.tic()

    contributed_document = person.Base_contribute(
      synchronous_metadata_discovery=True,
      publication_state='published',
      file=makeFileUpload('TEST-en-002.pdf', as_name='doc.pdf'))
    self.tic()
    self.assertEqual(contributed_document.getValidationState(), 'published')

  def test_Base_contribute_publication_state_vs_finishIngestion_script(self):
    """Contribute dialog allow choosing a publication state, but there's
    also a "finishIngestion" type based script that can be configured to
    force change the state. If user selects a publication_state, the state is
    changed before the finishIngestion can operate.
    """
    createZODBPythonScript(
        self.portal.portal_skins.custom,
        'PDF_finishIngestion',
        '',
        'if context.getValidationState() == "draft":\n'
        '  context.publish()')
    person = self.portal.person_module.newContent(portal_type='Person')
    contributed_document = person.Base_contribute(
          publication_state='shared',
          synchronous_metadata_discovery=True,
          file=makeFileUpload('TEST-en-002.pdf', as_name='doc.pdf'))
    self.tic()
    self.assertEqual(contributed_document.getValidationState(), 'shared')
    contributed_document.setReference(None)
    self.tic()

    contributed_document = person.Base_contribute(
          publication_state='shared',
          synchronous_metadata_discovery=False,
          file=makeFileUpload('TEST-en-002.pdf', as_name='doc.pdf'))
    self.tic()
    self.assertEqual(contributed_document.getValidationState(), 'shared')
    contributed_document.setReference(None)

    contributed_document = person.Base_contribute(
          publication_state=None,
          file=makeFileUpload('TEST-en-002.pdf', as_name='doc.pdf'))
    self.tic()
    self.assertEqual(contributed_document.getValidationState(), 'published')


class TestBase_contribute(IngestionTestCase, Base_contributeMixin):
  """Base_contribute tests as Manager (ie. without security restrictions)
  """


class TestBase_contributeWithSecurity(IngestionTestCase, Base_contributeMixin):
  """Base_contribute tests with security.
  """
  def login(self, *args, **kw):
    uf = self.portal.acl_users
    uf._doAddUser(self.id(), self.newPassword(), ['Associate', 'Assignor', 'Author'], [])
    user = uf.getUserById(self.id()).__of__(uf)
    newSecurityManager(None, user)

  def test_Base_contribute_mergeRevision(self):
    person = self.portal.person_module.newContent(portal_type='Person')
    ret = person.Base_contribute(
      redirect_to_context=True,
      synchronous_metadata_discovery=True,
      file=makeFileUpload('TEST-en-002.pdf'))
    self.assertIn(
      ('portal_status_message', 'PDF created successfully.'),
      urlparse.parse_qsl(urlparse.urlparse(ret).query))

    document, = self.portal.document_module.contentValues()
    self.assertEqual(
      (document.getReference(), document.getLanguage(), document.getVersion()),
      ('TEST', 'en', '002'))
    self.assertEqual(document.getValidationState(), 'draft')

    document.setData(b'')
    self.tic()

    # when updating, the message is different
    ret = person.Base_contribute(
      redirect_to_context=True,
      synchronous_metadata_discovery=True,
      file=makeFileUpload('TEST-en-002.pdf'))
    self.assertIn(
      ('portal_status_message', 'PDF updated successfully.'),
      urlparse.parse_qsl(urlparse.urlparse(ret).query))

    document, = self.portal.document_module.contentValues()
    self.assertEqual(
      (document.getReference(), document.getLanguage(), document.getVersion()),
      ('TEST', 'en', '002'))
    self.assertEqual(document.getValidationState(), 'draft')

    self.assertIn(b'%PDF', document.getData())

    # change to a state where user can not edit the document
    document.setData(b'')
    document.share()
    self.tic()

    for synchronous_metadata_discovery in True, False:
      with self.assertRaises(Redirect) as ctx:
        person.Base_contribute(
          redirect_to_context=True,
          synchronous_metadata_discovery=synchronous_metadata_discovery,
          file=makeFileUpload('TEST-en-002.pdf'))
      self.assertIn(
        ('portal_status_message',
        'You are not allowed to update the existing document which has the same coordinates.'),
        urlparse.parse_qsl(urlparse.urlparse(str(ctx.exception)).query))
      self.assertIn(
        ('portal_status_level', 'error'),
        urlparse.parse_qsl(urlparse.urlparse(str(ctx.exception)).query))

      # document is not updated
      self.assertEqual(document.getData(), b'')

      # when using the script directly it's an error
      with self.assertRaisesRegex(
          Unauthorized,
          "You are not allowed to update the existing document which has the same coordinates"):
        person.Base_contribute(
          synchronous_metadata_discovery=synchronous_metadata_discovery,
          file=makeFileUpload('TEST-en-002.pdf'))
      self.assertEqual(document.getData(), b'')

  def test_Base_contribute_publication_state_unauthorized(self):
    # When user is not allowed to publish a document, they can not use publication_state="published"
    # option of Base_contribute
    user_id = self.id() + '-author'
    uf = self.portal.acl_users
    uf._doAddUser(user_id, self.newPassword(), ['Author'], [])
    user = uf.getUserById(user_id).__of__(uf)
    newSecurityManager(None, user)

    person = self.portal.person_module.newContent(portal_type='Person')
    # with redirect_to_context option (like in the UI Dialog), we have a nice
    # status message
    with self.assertRaises(Redirect) as ctx:
      person.Base_contribute(
        publication_state='published',
        redirect_to_context=True,
        synchronous_metadata_discovery=True,
        file=makeFileUpload('TEST-en-002.pdf'))
    self.assertIn(
      ('portal_status_message', 'You are not allowed to contribute document in that state.'),
      urlparse.parse_qsl(urlparse.urlparse(str(ctx.exception)).query))
    self.assertIn(
      ('portal_status_level', 'error'),
      urlparse.parse_qsl(urlparse.urlparse(str(ctx.exception)).query))

    # when using the script directly it's an error
    with self.assertRaisesRegex(
        WorkflowException,
        "Transition document_publication_workflow/publish unsupported"):
      person.Base_contribute(
        publication_state='published',
        synchronous_metadata_discovery=True,
        file=makeFileUpload('TEST-en-002.pdf'))

    # when using asynchronous metadata discovery, an error occurs in activity,
    # but not document is published
    person.Base_contribute(
      publication_state='published',
      redirect_to_context=True,
      synchronous_metadata_discovery=False,
      file=makeFileUpload('TEST-en-002.pdf'))
    with self.assertRaisesRegex(
        Exception,
        "Transition document_publication_workflow/publish unsupported"):
      self.tic()

    self.assertEqual(
      {doc.getValidationState() for doc in self.portal.document_module.contentValues()},
      set(['draft']))
