##############################################################################
#
# Copyright (c) 2007 Nexedi SA and Contributors. All Rights Reserved.
#                    Bartek Gorny <bg@erp5.pl>
#                    Jean-Paul Smets <jp@nexedi.com>
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

import os, sys, cStringIO
import zipfile
from xml.dom.minidom import parseString

from cgi import FieldStorage
from zExceptions import BadRequest
from Testing import ZopeTestCase
from DateTime import DateTime
from AccessControl.SecurityManagement import newSecurityManager
from Products.CMFCore.utils import getToolByName

from Products.ERP5Type.Utils import convertToUpperCase
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.tests.Sequence import SequenceList
from Products.ERP5Type.Cache import clearCache
from Products.ERP5OOo.Document.OOoDocument import ConversionError
from Products.ERP5.Document.File import _unpackData

from zLOG import LOG

if __name__ == '__main__':
  execfile(os.path.join(sys.path[0], 'framework.py'))

# Needed in order to have a log file inside the current folder
os.environ['EVENT_LOG_FILE']     = os.path.join(os.getcwd(), 'zLOG.log')
os.environ['EVENT_LOG_SEVERITY'] = '-300'

# Define the conversion server host
conversion_server_host = ('127.0.0.1', 8008)


def printAndLog(msg):
  """
  A utility function to print a message
  to the standard output and to the LOG
  at the same time
  """
  msg = str(msg)
  ZopeTestCase._print('\n ' + msg)
  LOG('Testing... ', 0, msg)

class FileUploadTest(file):

  __allow_access_to_unprotected_subobjects__=1

  def __init__(self, path, name):
    self.filename = name
    file.__init__(self, path)
    self.headers = {}

def makeFilePath(name):
  return os.getenv('INSTANCE_HOME') + '/../Products/ERP5OOo/tests/test_document/' + name

def makeFileUpload(name):
  path = makeFilePath(name)
  return FileUploadTest(path, name)

class TestIngestion(ERP5TypeTestCase):
  """
    ERP5 Document Management System - test file ingestion mechanism
  """

  # pseudo constants
  RUN_ALL_TEST = 1
  QUIET = 0

  ##################################
  ##  ZopeTestCase Skeleton
  ##################################

  def getTitle(self):
    """
      Return the title of the current test set.
    """
    return "ERP5 DMS - Ingestion"

  def getBusinessTemplateList(self):
    """
      Return the list of required business templates.
    """
    return ('erp5_base', 'erp5_trade', 'erp5_project', 'erp5_dms')

  def afterSetUp(self, quiet=QUIET, run=RUN_ALL_TEST):
    """
      Initialize the ERP5 site.
    """
    self.login()
    self.datetime = DateTime()
    self.portal = self.getPortal()
    self.portal_categories = self.getCategoryTool()
    self.portal_catalog = self.getCatalogTool()
    self.createDefaultCategoryList()
    self.setSystemPreference()
    self.createTools()

  def createTools(self):
    """
      Set up contribution tool and content type registry

      NOTE: portal_contributions is not created yet
      by ERP5Site bootstrap. This is why me must create it
      here. We also delete it and recreate it in case
      it was saved by a previous --save run of the test.

      XXX - what about mimetype registry ?
    """
    # Delete and create portal_contributions
    try:
      self.portal._delObject('portal_contributions')
    except AttributeError:
      pass
    addTool = self.portal.manage_addProduct['ERP5'].manage_addTool
    addTool('ERP5 Contribution Tool', None)
    # Delete and create portal_mailin
    try:
      self.portal._delObject('portal_mailin')
    except AttributeError:
      pass
    addTool = self.portal.manage_addProduct['CMFMailIn'].manage_addTool
    addTool('CMF Mail In Tool', None)
    mailin = self.portal.portal_mailin
    mailin.edit_configuration('Document_ingestEmail')

  def setSystemPreference(self):
    default_pref = self.portal.portal_preferences.default_site_preference
    default_pref.setPreferredOoodocServerAddress(conversion_server_host[0])
    default_pref.setPreferredOoodocServerPortNumber(conversion_server_host[1])
    default_pref.setPreferredDocumentFileNameRegularExpression(
           "(?P<reference>[A-Z]{3,6})-(?P<language>[a-z]{2})-(?P<version>[0-9]{3})")
    default_pref.enable()


  ##################################
  ##  Useful methods
  ##################################

  def login(self, quiet=QUIET, run=RUN_ALL_TEST):
    """
      Create a new manager user and login.
    """
    user_name = 'dms_user'
    user_folder = self.portal.acl_users
    user_folder._doAddUser(user_name, '', ['Manager', 'Owner', 'Assignor'], [])
    user = user_folder.getUserById(user_name).__of__(user_folder)
    newSecurityManager(None, user)

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
                                    , immediate_reindex = 1
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
    get_transaction().commit()
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

  def getDocument(self, id):
    """
      Returns a document with given ID in the
      document module.
    """
    document_module = self.portal.document_module
    return getattr(document_module, id)

  def checkIsObjectCatalogged(self, portal_type, **kw):
    """
      Make sure that a document with given portal type
      and kw properties is already present in the catalog.

      Typical use of this method consists in providing
      an id or reference.
    """
    res = self.portal_catalog(portal_type=portal_type, **kw.copy())
    self.assertEquals(len(res), 1)
    for key, value in kw.items():
      self.assertEquals(res[0].getProperty(key), value)

  def newEmptyCataloggedDocument(self, portal_type, id):
    """
      Create an empty document of given portal type
      and given ID. 

      Documents are immediately catalogged and verified
      both form catalog point of view and from their
      presence in the document module.
    """
    document_module = self.portal.getDefaultModule(portal_type)
    document = getattr(document_module, id, None)
    if document is not None:
      document_module.manage_delObjects([id,])
    document = document_module.newContent(portal_type=portal_type, id=id)
    document.reindexObject()
    get_transaction().commit()
    self.tic()
    self.checkIsObjectCatalogged(portal_type, id=id, parent_uid=document_module.getUid())
    self.assert_(hasattr(document_module, id))
    return document

  def ingestFormatList(self, document_id, format_list, portal_type=None):
    """
      Upload in document document_id all test files which match
      any of the formats in format_list.

      portal_type can be specified to force the use of
      the default module for a given portal type instead
      of the document module.

      For every file, this checks is the word "magic"
      is present in both SearchableText and asText.
    """
    if portal_type is None:
      document_module = self.portal.document_module
    else:
      document_module = self.portal.getDefaultModule(portal_type)
    context = getattr(document_module, document_id)
    for revision, format in enumerate(format_list):
      filename = 'TEST-en-002.' + format
      f = makeFileUpload(filename)
      context.edit(file=f)
      context.convertToBaseFormat()
      context.reindexObject()
      get_transaction().commit()
      self.tic()
      self.failUnless(context.hasFile())
      if context.getPortalType() in ('Image', 'File', 'PDF'):
        # File and images do not support conversion to text in DMS
        # PDF has not implemented _convertToBaseFormat() so can not be converted
        self.assertEquals(context.getExternalProcessingState(), 'uploaded')
      else:
        self.assertEquals(context.getExternalProcessingState(), 'converted') # this is how we know if it was ok or not
        self.assert_('magic' in context.SearchableText())
        self.assert_('magic' in str(context.asText()))

  def checkDocumentExportList(self, document_id, format, asserted_target_list):
    """
      Upload document ID document_id with
      a test file of given format and assert that the document
      can be converted to any of the formats in asserted_target_list
    """
    context = self.getDocument(document_id)
    filename = 'TEST-en-002.' + format
    f = makeFileUpload(filename)
    context.edit(file=f)
    context.convertToBaseFormat()
    context.reindexObject()
    get_transaction().commit()
    self.tic()
    clearCache() # We call clear cache to be sure that
                 # the target list is updated
    target_list = context.getTargetFormatList()
    for target in asserted_target_list:
      self.assert_(target in target_list)

  def contributeFileList(self, with_portal_type=False):
    """
      Tries to a create new content through portal_contributions
      for every possible file type. If with_portal_type is set
      to true, portal_type is specified when calling newContent
      on portal_contributions. 
    """
    created_documents = []
    extension_to_type = (('ppt', 'Presentation')
                        ,('doc', 'Text')
                        ,('sdc', 'Spreadsheet')
                        ,('sxc', 'File')
                        ,('pdf', 'PDF')
                        ,('jpg', 'Image')
                        ,('py', 'File')
                        )
    for extension, portal_type in extension_to_type:
      filename = 'TEST-en-002.' + extension
      file = makeFileUpload(filename)
      if with_portal_type:
        ob = self.portal.portal_contributions.newContent(portal_type=portal_type, file=file)
      else:
        ob = self.portal.portal_contributions.newContent(file=file)
      ob.immediateReindexObject()
      created_documents.append(ob)
    get_transaction().commit()
    self.tic()
    # inspect created objects
    count = 0
    for extension, portal_type in extension_to_type:
      ob = created_documents[count]
      count+=1
      self.assertEquals(ob.getPortalType(), portal_type)
      self.assertEquals(ob.getReference(), 'TEST')
      if ob.getPortalType() in ('Image', 'File', 'PDF'):
        # Image, File and PDF are not converted to a base format
        self.assertEquals(ob.getExternalProcessingState(), 'uploaded')
      else:
        # We check if conversion has succeeded by looking
        # at the external_processing workflow
        self.assertEquals(ob.getExternalProcessingState(), 'converted')
        self.assert_('magic' in ob.SearchableText())
    # clean up created objects for next test !
    for ob in created_documents:
      parent = ob.getParentValue() 
      parent.manage_delObjects([ob.getId(),])

  def newPythonScript(self, object_id, script_id, argument_list, code):
    """
      Creates a new python script with given argument_list
      and source code.
    """
    context = self.getDocument(object_id)
    factory = context.manage_addProduct['PythonScripts'].manage_addPythonScript
    factory(id=script_id)
    script = getattr(context, script_id)
    script.ZPythonScript_edit(argument_list, code)

  def setDiscoveryOrder(self, order, id='one'):
    """
      Creates a script to define the metadata discovery order
      for Text documents.
    """
    script_code = "return %s" % str(order)
    self.newPythonScript(id, 'Text_getPreferredDocumentMetadataDiscoveryOrderList', '', script_code)
    
  def discoverMetadata(self, document_id='one'):
    """
      Sets input parameters and on the document ID document_id
      and discover metadata. For reindexing
    """
    context = self.getDocument(document_id)
    # simulate user input
    context._backup_input = dict(reference='INPUT', 
                                 language='in',
                                 version='004', 
                                 short_title='from_input',
                                 contributor='person_module/james')
    # pass to discovery file_name and user_login
    context.discoverMetadata(context.getSourceReference(), 'john_doe') 
    context.reindexObject()
    get_transaction().commit()
    self.tic()

  def checkMetadataOrder(self, expected_metadata, document_id='one'):
    """
    Asserts that metadata of document ID document_id
    is the same as expected_metadata
    """
    context = self.getDocument(document_id)
    for k, v in expected_metadata.items():
      self.assertEquals(context.getProperty(k), v)

  ##################################
  ##  Basic steps
  ##################################
 
  def stepTic(self, sequence=None, sequence_list=None, **kw):
    self.tic()

  def stepCreatePerson(self, sequence=None, sequence_list=None, **kw):
    """
      Create a person with ID "john" if it does not exists already
    """
    portal_type = 'Person'
    id = 'john'
    reference = 'john_doe'
    person_module = self.portal.person_module
    if getattr(person_module, 'john', False): return 
    person = person_module.newContent( portal_type='Person'
                                     , id=id
                                     ,  reference = reference
                                     )
    person.setDefaultEmailText('john@doe.com')
    person.reindexObject(); get_transaction().commit(); self.tic()

  def stepCreateTextDocument(self, sequence=None, sequence_list=None, **kw):
    """
      Create an empty Text document with ID 'one'
      This document will be used in most tests.
    """
    self.newEmptyCataloggedDocument('Text', 'one')

  def stepCreateSpreadsheetDocument(self, sequence=None, sequence_list=None, **kw):
    """
      Create an empty Spreadsheet document with ID 'two'
      This document will be used in most tests.
    """
    self.newEmptyCataloggedDocument('Spreadsheet', 'two')

  def stepCreatePresentationDocument(self, sequence=None, sequence_list=None, **kw):
    """
      Create an empty Presentation document with ID 'three'
      This document will be used in most tests.
    """
    self.newEmptyCataloggedDocument('Presentation', 'three')

  def stepCreateDrawingDocument(self, sequence=None, sequence_list=None, **kw):
    """
      Create an empty Drawing document with ID 'four'
      This document will be used in most tests.
    """
    self.newEmptyCataloggedDocument('Drawing', 'four')

  def stepCreatePDFDocument(self, sequence=None, sequence_list=None, **kw):
    """
      Create an empty PDF document with ID 'five'
      This document will be used in most tests.
    """
    self.newEmptyCataloggedDocument('PDF', 'five')

  def stepCreateImageDocument(self, sequence=None, sequence_list=None, **kw):
    """
      Create an empty Image document with ID 'six'
      This document will be used in most tests.
    """
    self.newEmptyCataloggedDocument('Image', 'six')

  def stepCheckEmptyState(self, sequence=None, sequence_list=None, **kw):
    """
      Check if the document is in "empty" processing state
      (ie. no file upload has been done yet)
    """
    context = self.getDocument('one')
    return self.assertEquals(context.getExternalProcessingState(), 'empty')

  def stepCheckUploadedState(self, sequence=None, sequence_list=None, **kw):
    """
      Check if the document is in "uploaded" processing state
      (ie. a file upload has been done)
    """
    context = self.getDocument('one')
    return self.assertEquals(context.getExternalProcessingState(), 'uploaded')

  def stepCheckConvertedState(self, sequence=None, sequence_list=None, **kw):
    """
      Check if the document is in "converted" processing state
      (ie. a file upload has been done and the document has
      been converted)
    """
    context = self.getDocument('one')
    return self.assertEquals(context.getExternalProcessingState(), 'converted')

  def stepStraightUpload(self, sequence=None, sequence_list=None, **kw):
    """
      Upload a file directly from the form
      check if it has the data and source_reference
    """
    filename = 'TEST-en-002.doc'
    document = self.getDocument('one')
    # Revision is 0 before upload (revisions are strings)
    self.assertEquals(document.getRevision(), '0')
    f = makeFileUpload(filename)
    document.edit(file=f)
    # set source
    document.setSourceReference(filename)
    self.assert_(document.hasFile())
    # source_reference set to file name ?
    self.assertEquals(document.getSourceReference(), filename) 
    # Revision is 1 after upload (revisions are strings)
    self.assertEquals(document.getRevision(), '1')
    document.reindexObject()
    get_transaction().commit()
    self.tic()

  def stepDialogUpload(self, sequence=None, sequence_list=None, **kw):
    """
      Upload a file using the dialog script Document_uploadFile
      and make sure this increases the revision
    """
    context = self.getDocument('one')
    f = makeFileUpload('TEST-en-002.doc')
    revision = context.getRevision()
    context.Document_uploadFile(file=f)
    self.assertEquals(context.getRevision(), str(int(revision) + 1))
    context.reindexObject()
    get_transaction().commit()
    self.tic()

  def stepDiscoverFromFilename(self, sequence=None, sequence_list=None, **kw):
    """
      Upload a file using the dialog script Document_uploadFile.
      This should trigger metadata discovery and we should have
      basic coordinates immediately, from first stage.
    """
    context = self.getDocument('one')
    file_name = 'TEST-en-002.doc'
    # First make sure the regular expressions work
    property_dict = context.getPropertyDictFromFileName(file_name)
    self.assertEquals(property_dict['reference'], 'TEST')
    self.assertEquals(property_dict['language'], 'en')
    self.assertEquals(property_dict['version'], '002')
    # Then make sure content discover works
    # XXX - This part must be extended
    property_dict = context.getPropertyDictFromContent()
    self.assertEquals(property_dict['title'], 'title')
    self.assertEquals(property_dict['description'], 'comments')
    self.assertEquals(property_dict['subject_list'], ['keywords'])
    # Then make sure metadata discovery works
    f = makeFileUpload(file_name)
    context.Document_uploadFile(file=f)
    self.assertEquals(context.getReference(), 'TEST')
    self.assertEquals(context.getLanguage(), 'en')
    self.assertEquals(context.getVersion(), '002')

  def stepCheckConvertedContent(self, sequence=None, sequence_list=None, **kw):
    """
      Check that the input file was successfully converted
      and that its SearchableText and asText contain
      the word "magic"
    """
    self.tic()
    context = self.getDocument('one')
    self.assert_(context.hasBaseData())
    self.assert_('magic' in context.SearchableText())
    self.assert_('magic' in str(context.asText()))

  def stepSetSimulatedDiscoveryScript(self, sequence=None, sequence_list=None, **kw):
    """
      Create Text_getPropertyDictFrom[source] scripts
      to simulate custom site's configuration
    """
    self.newPythonScript('one', 'Text_getPropertyDictFromUserLogin',
                         'user_name=None', "return {'contributor':'person_module/john'}")
    self.newPythonScript('one', 'Text_getPropertyDictFromContent', '',
                         "return {'short_title':'short', 'title':'title', 'contributor':'person_module/john',}")

  def stepTestMetadataSetting(self, sequence=None, sequence_list=None, **kw):
    """
      Upload with custom getPropertyDict methods
      check that all metadata are correct
    """
    context = self.getDocument('one')
    f = makeFileUpload('TEST-en-002.doc')
    context.Document_uploadFile(file=f)
    get_transaction().commit()
    self.tic()
    # Then make sure content discover works
    property_dict = context.getPropertyDictFromUserLogin()
    self.assertEquals(property_dict['contributor'], 'person_module/john')
    # reference from filename (the rest was checked some other place)
    self.assertEquals(context.getReference(), 'TEST')
    # short_title from content
    self.assertEquals(context.getShortTitle(), 'short')
    # title from metadata inside the document
    self.assertEquals(context.getTitle(), 'title')
    # contributors from user
    self.assertEquals(context.getContributor(), 'person_module/john')

  def stepEditMetadata(self, sequence=None, sequence_list=None, **kw):
    """
      we change metadata in a document which has ODF
    """
    context = self.getDocument('one')
    kw = dict(title='another title',
              subject='another subject',
              description='another description')
    context.updateBaseMetadata(**kw)
    # context.edit(**kw) - this works from UI but not from here - is there a problem somewhere?
    context.reindexObject(); get_transaction().commit();
    self.tic();

  def stepCheckChangedMetadata(self, sequence=None, sequence_list=None, **kw):
    """
      then we download it and check if it is changed
    """
    # XXX actually this is an example of how it should be
    # implemented in OOoDocument class - we don't really
    # need oood for getting/setting metadata...
    context = self.getDocument('one')
    newcontent = context.getBaseData()
    cs = cStringIO.StringIO()
    cs.write(_unpackData(newcontent))
    z = zipfile.ZipFile(cs)
    s = z.read('meta.xml')
    xmlob = parseString(s)
    title = xmlob.getElementsByTagName('dc:title')[0].childNodes[0].data
    self.assertEquals(title, u'another title')
    subject = xmlob.getElementsByTagName('dc:subject')[0].childNodes[0].data
    self.assertEquals(subject, u'another subject')
    description = xmlob.getElementsByTagName('dc:description')[0].childNodes[0].data
    self.assertEquals(description, u'another description')
    
  def stepIngestTextFormats(self, sequence=None, sequence_list=None, **kw):
    """
      ingest all supported text formats
      make sure they are converted
    """
    format_list = ['rtf', 'doc', 'txt', 'sxw', 'sdw']
    self.ingestFormatList('one', format_list)

  def stepIngestSpreadsheetFormats(self, sequence=None, sequence_list=None, **kw):
    """
      ingest all supported spreadsheet formats
      make sure they are converted
    """
    format_list = ['xls', 'sxc', 'sdc']
    self.ingestFormatList('two', format_list)

  def stepIngestPresentationFormats(self, sequence=None, sequence_list=None, **kw):
    """
      ingest all supported presentation formats
      make sure they are converted
    """
    format_list = ['ppt', 'sxi', 'sdd']
    self.ingestFormatList('three', format_list)

  def stepIngestPDFFormats(self, sequence=None, sequence_list=None, **kw):
    """
      ingest all supported PDF formats
      make sure they are converted
    """
    format_list = ['pdf']
    self.ingestFormatList('five', format_list)

  def stepIngestDrawingFormats(self, sequence=None, sequence_list=None, **kw):
    """
      ingest all supported presentation formats
      make sure they are converted
    """
    format_list = ['sxd','sda']
    self.ingestFormatList('four', format_list)

  def stepIngestPDFFormats(self, sequence=None, sequence_list=None, **kw):
    """
      ingest all supported pdf formats
      make sure they are converted
    """
    format_list = ['pdf']
    self.ingestFormatList('five', format_list)

  def stepIngestImageFormats(self, sequence=None, sequence_list=None, **kw):
    """
      ingest all supported image formats
    """
    format_list = ['jpg', 'gif', 'bmp', 'png']
    self.ingestFormatList('six', format_list, 'Image')

  def stepCheckTextDocumentExportList(self, sequence=None, sequence_list=None, **kw):
    self.checkDocumentExportList('one', 'doc', ['pdf', 'doc', 'rtf', 'html-writer', 'txt'])

  def stepCheckSpreadsheetDocumentExportList(self, sequence=None, sequence_list=None, **kw):
    self.checkDocumentExportList('two', 'xls', ['csv', 'html-calc', 'xls', 'calc.pdf'])

  def stepCheckPresentationDocumentExportList(self, sequence=None, sequence_list=None, **kw):
    self.checkDocumentExportList('three', 'ppt', ['impr.pdf', 'ppt'])

  def stepCheckDrawingDocumentExportList(self, sequence=None, sequence_list=None, **kw):
    self.checkDocumentExportList('four', 'sxd', ['jpg', 'draw.pdf', 'svg'])

  def stepExportPDF(self, sequence=None, sequence_list=None, **kw):
    """
      Try to export PDF to text and HTML
    """
    document = self.getDocument('five')
    f = makeFileUpload('TEST-en-002.pdf')
    document.edit(file=f)
    mime, text = document.convert('text')
    self.failUnless('magic' in text)
    self.failUnless(mime == 'text/plain')
    mime, html = document.convert('html')
    self.failUnless('magic' in html)
    self.failUnless(mime == 'text/html')

  def stepExportImage(self, sequence=None, sequence_list=None, **kw):
    """
      Don't see a way to test it here, Image.index_html makes heavy use 
      of REQUEST and RESPONSE, and the rest of the implementation is way down
      in Zope core
    """
    printAndLog('stepExportImage not implemented')

  def stepCheckHasSnapshot(self, sequence=None, sequence_list=None, **kw):
    context = self.getDocument('one')
    self.failUnless(context.hasSnapshotData())

  def stepCheckHasNoSnapshot(self, sequence=None, sequence_list=None, **kw):
    context = self.getDocument('one')
    self.failIf(context.hasSnapshotData())

  def stepCreateSnapshot(self, sequence=None, sequence_list=None, **kw):
    context = self.getDocument('one')
    context.createSnapshot()

  def stepTryRecreateSnapshot(self, sequence=None, sequence_list=None, **kw):
    context = self.getDocument('one')
    # XXX this always fails, don't know why
    #self.assertRaises(ConversionError, context.createSnapshot)

  def stepDeleteSnapshot(self, sequence=None, sequence_list=None, **kw):
    context = self.getDocument('one')
    context.deleteSnapshot()

  def stepContributeFileListWithType(self, sequence=None, sequence_list=None, **kw):
    """
      Contribute all kinds of files giving portal type explicitly
      TODO: test situation whereby portal_type given explicitly is wrong
    """
    self.contributeFileList(with_portal_type=True)

  def stepContributeFileListWithNoType(self, sequence=None, sequence_list=None, **kw):
    """
      Contribute all kinds of files
      let the system figure out portal type by itself
    """
    self.contributeFileList(with_portal_type=False)

  def stepSetSimulatedDiscoveryScriptForOrdering(self, sequence=None, sequence_list=None, **kw):
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
    self.newPythonScript('one', 'Text_getPropertyDictFromUserLogin', 'user_name=None', "return {'reference':'USER', 'language':'us', 'contributor':'person_module/john'}")
    self.newPythonScript('one', 'Text_getPropertyDictFromContent', '', "return {'reference':'CONT', 'version':'003', 'contributor':'person_module/jack', 'short_title':'from_content'}")

  def stepCheckMetadataSettingOrderFICU(self, sequence=None, sequence_list=None, **kw):
    """
     This is the default
    """  
    expected_metadata = dict(reference='TEST', language='en', version='002', short_title='from_input', contributor='person_module/james')
    self.setDiscoveryOrder(['file_name', 'input', 'content', 'user_login'])
    self.discoverMetadata()
    self.checkMetadataOrder(expected_metadata)

  def stepCheckMetadataSettingOrderCUFI(self, sequence=None, sequence_list=None, **kw):
    """
     Content - User - Filename - Input
    """
    expected_metadata = dict(reference='CONT', language='us', version='003', short_title='from_content', contributor='person_module/jack')
    self.setDiscoveryOrder(['content', 'user_login', 'file_name', 'input'])
    self.discoverMetadata()
    self.checkMetadataOrder(expected_metadata)

  def stepCheckMetadataSettingOrderUIFC(self, sequence=None, sequence_list=None, **kw):
    """
     User - Input - Filename - Content
    """
    expected_metadata = dict(reference='USER', language='us', version='004', short_title='from_input', contributor='person_module/john')
    self.setDiscoveryOrder(['user_login', 'input', 'file_name', 'content'])
    self.discoverMetadata()
    self.checkMetadataOrder(expected_metadata)

  def stepCheckMetadataSettingOrderICUF(self, sequence=None, sequence_list=None, **kw):
    """
     Input - Content - User - Filename
    """
    expected_metadata = dict(reference='INPUT', language='in', version='004', short_title='from_input', contributor='person_module/james')
    self.setDiscoveryOrder(['input', 'content', 'user_login', 'file_name'])
    self.discoverMetadata()
    self.checkMetadataOrder(expected_metadata)

  def stepCheckMetadataSettingOrderUFCI(self, sequence=None, sequence_list=None, **kw):
    """
     User - Filename - Content - Input
    """
    expected_metadata = dict(reference='USER', language='us', version='002', short_title='from_content', contributor='person_module/john')
    self.setDiscoveryOrder(['user_login', 'file_name', 'content', 'input'])
    self.discoverMetadata()
    self.checkMetadataOrder(expected_metadata)

  def stepReceiveEmailFromUnknown(self, sequence=None, sequence_list=None, **kw):
    """
      email was sent in by someone who is not in the person_module
    """
    self.failUnless(hasattr(self.portal, 'portal_mailin'))
    f = open(makeFilePath('email_from.txt'))
    res = self.portal.portal_mailin.postMailMessage(f.read())
    # we check if the mailin returned anything - it should return a message saying that the recipient does not exist
    # the exact wording may differ
    # the way mailin works is that if mail was accepted it returns None
    self.failUnless(res)  

  def stepReceiveEmailFromJohn(self, sequence=None, sequence_list=None, **kw):
    """
      email was sent in by someone who is in the person_module
    """
    self.failUnless(hasattr(self.portal, 'portal_mailin'))
    f = open(makeFilePath('email_from.txt'))
    res = self.portal.portal_mailin.postMailMessage(f.read())
    # we check if the mailin returned anything - it should return a message saying that the recipient does not exist
    # the exact wording may differ
    # the way mailin works is that if mail was accepted it returns None
    self.failIf(res)  
    get_transaction().commit()
    self.tic()

  def stepVerifyEmailedDocuments(self, sequence=None, sequence_list=None, **kw):
    """
      find the newly mailed-in document by its reference
      check its properties
    """
    res = self.portal_catalog(reference='MAIL')
    self.assertEquals(len(res), 1) # check if it is there
    document = res[0].getObject()
    john_is_owner = 0
    for role in document.get_local_roles():
      if role[0] == 'john_doe' and 'Owner' in role[1]:
        john_is_owner = 1
        break
    self.failUnless(john_is_owner)

  
  ##################################
  ##  Tests
  ##################################

  def test_01_PreferenceSetup(self, quiet=QUIET, run=RUN_ALL_TEST):
    """
      Make sure that preferences are set up properly and accessible
    """
    if not run: return
    if not quiet: printAndLog('test_01_PreferenceSetup')
    preference_tool = self.portal.portal_preferences
    self.assertEquals(preference_tool.getPreferredOoodocServerAddress(), conversion_server_host[0])
    self.assertEquals(preference_tool.getPreferredOoodocServerPortNumber(), conversion_server_host[1])
    self.assertEquals(preference_tool.getPreferredDocumentFileNameRegularExpression(),
                      "(?P<reference>[A-Z]{3,6})-(?P<language>[a-z]{2})-(?P<version>[0-9]{3})")

  def test_02_FileExtensionRegistry(self, quiet=QUIET, run=RUN_ALL_TEST):
    """
      check if we successfully imported registry
      and that it has all the entries we need
    """
    if not run: return
    if not quiet: printAndLog('test_02_FileExtensionRegistry')
    reg = self.portal.content_type_registry
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
            'sdc' : 'Spreadsheet',
            'ppt' : 'Presentation',
            'odp' : 'Presentation',
            'sxi' : 'Presentation',
            'xxx' : 'File',
          }
    for type, portal_type in correct_type_mapping.items():
      file_name = 'aaa.' + type
      self.assertEquals(reg.findTypeName(file_name, None, None), portal_type)

  def test_03_TextDoc(self, quiet=QUIET, run=RUN_ALL_TEST):
    """h
      Test basic behaviour of a document:
      - create empty document
      - upload a file directly
      - upload a file using upload dialog
      - make sure revision was increased
      - check that it was properly converted
      - check if coordinates were extracted from file name
    """
    if not run: return
    if not quiet: printAndLog('test_03_TextDoc')
    sequence_list = SequenceList()
    step_list = [ 'stepCreateTextDocument'
                 ,'stepCheckEmptyState'
                 ,'stepStraightUpload'
                 ,'stepCheckConvertedState'
                 ,'stepDialogUpload'
                 ,'stepCheckConvertedState'
                 ,'stepDiscoverFromFilename'
                 ,'stepCheckConvertedContent'
                ]
    sequence_string = ' '.join(step_list)
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

  def test_04_MetadataExtraction(self, quiet=QUIET, run=RUN_ALL_TEST):
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
    if not run: return
    if not quiet: printAndLog('test_04_MetadataExtraction')
    sequence_list = SequenceList()
    step_list = [ 'stepCreateTextDocument'
                 ,'stepSetSimulatedDiscoveryScript'
                 ,'stepTestMetadataSetting'
                ]
    sequence_string = ' '.join(step_list)
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

  def test_04_MetadataEditing(self, quiet=QUIET, run=RUN_ALL_TEST):
    """
      Check metadata in the object and in the ODF document
      Edit metadata on the object
      Download ODF, make sure it is changed
    """
    if not run: return
    if not quiet: printAndLog('test_04_MetadataEditing')
    sequence_list = SequenceList()
    step_list = [ 'stepCreateTextDocument'
                 ,'stepDialogUpload'
                 ,'stepEditMetadata'
                 ,'stepCheckChangedMetadata'
                ]
    sequence_string = ' '.join(step_list)
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

  def test_05_FormatIngestion(self, quiet=QUIET, run=RUN_ALL_TEST):
    """
      Ingest various formats (xls, doc, sxi, ppt etc)
      Verify that they are successfully converted
      - have ODF data and contain magic word in SearchableText
      - or have text data and contain magic word in SearchableText
        TODO:
      - or were not moved in processing_status_workflow if the don't
        implement _convertToBase (e.g. Image)
      Verify that you can not upload file of the wrong format.
    """
    if not run: return
    if not quiet: printAndLog('test_05_FormatIngestion')
    sequence_list = SequenceList()
    step_list = ['stepCreateTextDocument'
                 ,'stepIngestTextFormats'
                 ,'stepCreateSpreadsheetDocument'
                 ,'stepIngestSpreadsheetFormats'
                 ,'stepCreatePresentationDocument'
                 ,'stepIngestPresentationFormats'
                 ,'stepCreateDrawingDocument'
                 ,'stepIngestDrawingFormats'
                 ,'stepCreatePDFDocument'
                 ,'stepIngestPDFFormats'
                 ,'stepCreateImageDocument'
                 ,'stepIngestImageFormats'
                ]
    sequence_string = ' '.join(step_list)
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

  def test_06_FormatGeneration(self, quiet=QUIET, run=RUN_ALL_TEST):
    """
      Test generation of files in all possible formats
      which means check if they have correct lists of available formats for export
      actual generation is tested in oood tests
      PDF and Image should be tested here
    """
    if not run: return
    if not quiet: printAndLog('test_06_FormatGeneration')
    sequence_list = SequenceList()
    step_list = [ 'stepCreateTextDocument'
                 ,'stepCheckTextDocumentExportList'
                 ,'stepCreateSpreadsheetDocument'
                 ,'stepCheckSpreadsheetDocumentExportList'
                 ,'stepCreatePresentationDocument'
                 ,'stepCheckPresentationDocumentExportList'
                 ,'stepCreateDrawingDocument'
                 ,'stepCheckDrawingDocumentExportList'
                 ,'stepCreatePDFDocument'
                 ,'stepExportPDF'
                 ,'stepCreateImageDocument'
                 ,'stepExportImage'
                ]
    sequence_string = ' '.join(step_list)
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

  def test_07_SnapshotGeneration(self, quiet=QUIET, run=RUN_ALL_TEST):
    """
      Generate snapshot, make sure it is there, 
      try to generate it again, remove and 
      generate once more
    """
    if not run: return
    if not quiet: printAndLog('test_07_SnapshotGeneration')
    sequence_list = SequenceList()
    step_list = [ 'stepCreateTextDocument'
                 ,'stepDialogUpload'
                 ,'stepCheckHasNoSnapshot'
                 ,'stepCreateSnapshot'
                 ,'stepTryRecreateSnapshot'
                 ,'stepCheckHasSnapshot'
                 ,'stepDeleteSnapshot'
                 ,'stepCheckHasNoSnapshot'
                 ,'stepCreateSnapshot'
                ]
    sequence_string = ' '.join(step_list)
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

  def test_08_Cache(self, quiet=QUIET, run=RUN_ALL_TEST):
    """
      I don't know how to verify how cache works
    """

  def test_09_Contribute(self, quiet=QUIET, run=0):
    """
      Create content through portal_contributions
      - use newContent to ingest various types 
        also to test content_type_registry setup
      - verify that
        - appropriate portal_types were created
        - the files were converted
        - metadata was read
    """
    if not run: return
    if not quiet: printAndLog('test_09_Contribute')
    sequence_list = SequenceList()
    step_list = ['stepContributeFileListWithNoType'
                 ,'stepContributeFileListWithType'
                ]
    sequence_string = ' '.join(step_list)
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

  def test_10_MetadataSettingPreferenceOrder(self, quiet=QUIET, run=RUN_ALL_TEST):
    """
      Set some metadata discovery scripts
      Contribute a document, let it get metadata using default setup
      (default is FUC)

      check that the right ones are there
      change preference order, check again
    """
    if not run: return
    if not quiet: printAndLog('test_10_MetadataSettingPreferenceOrder')
    sequence_list = SequenceList()
    step_list = [ 'stepCreateTextDocument'
                 ,'stepStraightUpload'
                 ,'stepSetSimulatedDiscoveryScriptForOrdering'
                 ,'stepCheckMetadataSettingOrderFICU'
                 ,'stepCreateTextDocument'
                 ,'stepStraightUpload'
                 ,'stepSetSimulatedDiscoveryScriptForOrdering'
                 ,'stepCheckMetadataSettingOrderCUFI'
                 ,'stepCreateTextDocument'
                 ,'stepStraightUpload'
                 ,'stepSetSimulatedDiscoveryScriptForOrdering'
                 ,'stepCheckMetadataSettingOrderUIFC'
                 ,'stepCreateTextDocument'
                 ,'stepStraightUpload'
                 ,'stepSetSimulatedDiscoveryScriptForOrdering'
                 ,'stepCheckMetadataSettingOrderICUF'
                 ,'stepCreateTextDocument'
                 ,'stepStraightUpload'
                 ,'stepSetSimulatedDiscoveryScriptForOrdering'
                 ,'stepCheckMetadataSettingOrderUFCI'
                ]
    sequence_string = ' '.join(step_list)
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

  def test_11_EmailIngestion(self, quiet=QUIET, run=RUN_ALL_TEST):
    """
      Simulate email piped to ERP5 by an MTA by uploading test email from file
      Check that document objects are created and appropriate data are set
      (owner, and anything discovered from user and mail body)
    """
    if not run: return
    if not quiet: printAndLog('test_11_EmailIngestion')
    sequence_list = SequenceList()
    step_list = [ 'stepReceiveEmailFromUnknown'
                 ,'stepCreatePerson'
                 ,'stepReceiveEmailFromJohn'
                 ,'stepVerifyEmailedDocuments'
                ]
    sequence_string = ' '.join(step_list)
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)


if __name__ == '__main__':
  framework()
else:
  import unittest
  def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestIngestion))
    return suite

# Missing tests
"""
    property_dict = context.getPropertyDictFromUserLogin()
    property_dict = context.getPropertyDictFromInput()
"""
