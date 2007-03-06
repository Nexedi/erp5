##############################################################################
#
# Copyright (c) 2005 Nexedi SARL and Contributors. All Rights Reserved.
#                    Kevin Deldycke <kevin_AT_nexedi_DOT_com>
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


import os
import cStringIO
from xml.dom.minidom import parseString
import zipfile
from cgi import FieldStorage
from zLOG import LOG
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


if __name__ == '__main__':
  execfile(os.path.join(sys.path[0], 'framework.py'))

# Needed in order to have a log file inside the current folder
os.environ['EVENT_LOG_FILE']     = os.path.join(os.getcwd(), 'zLOG.log')
os.environ['EVENT_LOG_SEVERITY'] = '-300'

ooodoc_coordinates = ('127.0.0.1', 8008)

testrun = ()

def shout(msg):
  msg = str(msg)
  ZopeTestCase._print('\n ' + msg)
  LOG('Testing... ', 0, msg)

def unpackData(data):
  """
  Unpack Pdata into string
  """
  if isinstance(data, str):
    return data
  else:
    data_list = []
    while data is not None:
      data_list.append(data.data)
      data = data.next
    return ''.join(data_list)

class FileUploadTest(file):

  __allow_access_to_unprotected_subobjects__=1

  def __init__(self, path, name):
    self.filename = name
    file.__init__(self, path)

def makeFileUpload(name):
  path = os.getenv('INSTANCE_HOME') + '/../Products/ERP5OOo/tests/' + name
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
    return "ERP5 DMS - ingestion"

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
    self.datetime          = DateTime()
    self.portal            = self.getPortal()
    self.portal_categories = self.getCategoryTool()
    self.portal_catalog    = self.getCatalogTool()
    self.createCategories()
    self.createPreferences()
    self.createTools()

  def createTools(self):
    """
      Set up contribution tool and content type registry
    """
    # XXX portal_contributions is not created in bootstrap
    # so we have to create it here
    try:
      self.portal._delObject('portal_contributions')
    except AttributeError:
      pass
    addTool = self.portal.manage_addProduct['ERP5'].manage_addTool
    addTool('ERP5 Contribution Tool', None)
    # XXX  content_type_registry is not services by business templating mechanism
    # so it has to be exported and placed in ../../../unit_test/import/ director
    # we import it here
    try:
      self.portal._delObject('content_type_registry')
    except AttributeError:
      pass
    self.portal.manage_importObject(file='content_type_registry.zexp')

  def createPreferences(self):
    default_pref = self.portal.portal_preferences.default_site_preference
    default_pref.setPreferredOoodocServerAddress(ooodoc_coordinates[0])
    default_pref.setPreferredOoodocServerPortNumber(ooodoc_coordinates[1])
    default_pref.setPreferredDocumentFileNameRegularExpression("(?P<reference>[A-Z]{3,6})-(?P<language>[a-z]{2})-(?P<version>[0-9]{3})")
    default_pref.enable()


  ##################################
  ##  Useful methods
  ##################################

  def login(self, quiet=QUIET, run=RUN_ALL_TEST):
    """
      Create a new manager user and login.
    """
    user_name = 'bartek'
    user_folder = self.portal.acl_users
    user_folder._doAddUser(user_name, '', ['Manager', 'Owner', 'Assignor'], [])
    user = user_folder.getUserById(user_name).__of__(user_folder)
    newSecurityManager(None, user)

  def createCategories(self):
    """
      Create some categories for testing.
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

  def getCategoryList(self, base_category=None):
    """
      Get a list of categories with same base categories.
    """
    categories = []
    if base_category != None:
      for category in self.category_list:
        if category["path"].split('/')[0] == base_category:
          categories.append(category)
    return categories

  def checkObjectCatalogged(self, portal_type, reference):
    """
      make sure this object is already in the catalog
    """
    res = self.portal_catalog(portal_type=portal_type, reference=reference)
    self.assertEquals(len(res), 1)
    self.assertEquals(res[0].getReference(), reference)

  def createDocument(self, portal_type, id):
    """
      create an empty document of given portal type
      it has id as given and reference like document_[id]
      immediately catalogged and verified in two ways
    """
    dm = self.portal.getDefaultModule(portal_type)
    doc = getattr(dm, id, None)
    if doc is not None:
      dm.manage_delObjects([id,])
    reference =  'document_' + id
    doc = dm.newContent(portal_type=portal_type, id=id, reference=reference)
    #doctext._getServerCoordinate = getOoodCoordinate()
    doc.reindexObject(); get_transaction().commit(); self.tic()
    self.checkObjectCatalogged(portal_type, reference)
    self.assert_(hasattr(dm, id))

  def ingestFormats(self, doc_id, formats_from, portal_type=None):
    """
      method for bulk ingesting files of various formats
      we take them one by one based on naming convention
      ingest, convert
      check that a magic word is in every of them
      (unless it is Image or File)
    """
    if portal_type is None:
      dm = self.portal.document_module
    else:
      dm = self.portal.getDefaultModule(portal_type)
    context = getattr(dm, doc_id)
    for rev, format in enumerate(formats_from):
      filename = 'TEST-en-002.' + format
      f = makeFileUpload(filename)
      context.edit(file=f)
      context.convertToBase()
      context.reindexObject(); get_transaction().commit(); self.tic()
      self.failUnless(context.hasFile())
      if context.getPortalType() in ('Image', 'File'): # these are not subject to conversion
        self.assertEquals(context.getExternalProcessingState(), 'uploaded')
      else:
        self.assertEquals(context.getExternalProcessingState(), 'converted') # this is how we know if it was ok or not
        self.assert_('magic' in context.SearchableText())

  def checkDocumentExportList(self, doc_id, format, targets):
    """
      given the docs id
      make sure targets are in
      the objects target format list
    """
    dm = self.portal.document_module
    context = getattr(dm, doc_id)
    filename = 'TEST-en-002.' + format
    f = makeFileUpload(filename)
    context.edit(file=f)
    context.convertToBase()
    context.reindexObject(); get_transaction().commit(); self.tic()
    clearCache()
    target_list = [x[1] for x in context.getTargetFormatItemList()]
    for target in targets:
      self.assert_(target in target_list)

  def contributeFiles(self, with_portal_type=False):
    ext2type = (
      ('ppt' , 'Presentation')
      ,('doc' , 'Text')
      ,('sdc' , 'Spreadsheet')
      ,('sxc' , 'Drawing')
      ,('pdf' , 'PDF')
      ,('jpg' , 'Image')
      ,('py'  , 'File')
      )
    for ext, typ in ext2type:
      shout(ext)
      filename = 'TEST-en-002.' + ext
      file = makeFileUpload(filename)
      if with_portal_type:
        ob = self.portal.portal_contributions.newContent(portal_type=typ, file=file)
      else:
        ob = self.portal.portal_contributions.newContent(file=file)
      self.assertEquals(ob.getPortalType(), typ)
      self.assertEquals(ob.getReference(), 'TEST')
      ob.reindexObject(); get_transaction().commit(); self.tic()
      if ob.getPortalType() in ('Image', 'File'): # these are not subject to conversion
        self.assertEquals(ob.getExternalProcessingState(), 'uploaded')
      else:
        self.assertEquals(ob.getExternalProcessingState(), 'converted') # this is how we know if it was ok or not
        self.assert_('magic' in ob.SearchableText())
    

  ##################################
  ##  Basic steps
  ##################################

  def stepCheckPreferences(self, sequence=None, sequence_list=None, **kw):
    """
      make sure preferences are set up properly and accessible
    """
    self.assertEquals(self.portal.portal_preferences.getPreferredOoodocServerAddress(), ooodoc_coordinates[0])
    self.assertEquals(self.portal.portal_preferences.getPreferredOoodocServerPortNumber(), ooodoc_coordinates[1])
    self.assertEquals(self.portal.portal_preferences.default_site_preference.getPreferredDocumentFileNameRegularExpression(), "(?P<reference>[A-Z]{3,6})-(?P<language>[a-z]{2})-(?P<version>[0-9]{3})")

  def stepCheckContentTypeRegistry(self, sequence=None, sequence_list=None, **kw):
    """
      check if we successfully imported registry
      and that it has all the entries we need
    """
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

  def stepCreatePerson(self, sequence=None, sequence_list=None, **kw):
    """
      Create a person (if not exists).
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
    person.reindexObject(); get_transaction().commit(); self.tic()

  def stepCreateTextDocument(self, sequence=None, sequence_list=None, **kw):
    """
      create an empty Text document 'one'
      for further testing
      (first delete if exists)
    """
    self.createDocument('Text', 'one')

  def stepCreateSpreadsheetDocument(self, sequence=None, sequence_list=None, **kw):
    """
      create an empty Spreadsheet document 'two'
      for further testing
      (first delete if exists)
    """
    self.createDocument('Spreadsheet', 'two')

  def stepCreatePresentationDocument(self, sequence=None, sequence_list=None, **kw):
    """
      create an empty Presentation document 'three'
      for further testing
      (first delete if exists)
    """
    self.createDocument('Presentation', 'three')

  def stepCreateDrawingDocument(self, sequence=None, sequence_list=None, **kw):
    """
      create an empty Drawing document 'four'
      for further testing
      (first delete if exists)
    """
    self.createDocument('Drawing', 'four')

  def stepCreatePDFDocument(self, sequence=None, sequence_list=None, **kw):
    """
      create an empty PDF document 'five'
      for further testing
      (first delete if exists)
    """
    self.createDocument('PDF', 'five')

  def stepCreateImageDocument(self, sequence=None, sequence_list=None, **kw):
    """
      create an empty Image document 'six'
      for further testing
      (first delete if exists)
    """
    self.createDocument('Image', 'six')

  def stepCheckEmptyState(self, sequence=None, sequence_list=None, **kw):
    """
      check if the document is in "empty" processing state
    """
    dm = self.portal.document_module
    context = getattr(dm, 'one', None)
    return self.assertEquals(context.getExternalProcessingState(), 'empty')

  def stepCheckUploadedState(self, sequence=None, sequence_list=None, **kw):
    """
      check if the document is in "uploaded" processing state
    """
    dm = self.portal.document_module
    context = getattr(dm, 'one', None)
    return self.assertEquals(context.getExternalProcessingState(), 'uploaded')

  def stepCheckConvertedState(self, sequence=None, sequence_list=None, **kw):
    """
      check if the document is in "converted" processing state
    """
    dm = self.portal.document_module
    context = getattr(dm, 'one', None)
    return self.assertEquals(context.getExternalProcessingState(), 'converted')

  def stepStraightUpload(self, sequence=None, sequence_list=None, **kw):
    """
      Upload a file directly from the form
      check if it has the data and source_reference
    """
    dm = self.portal.document_module
    doc = getattr(dm, 'one')
    f = makeFileUpload('TEST-en-002.doc')
    doc.edit(file=f)
    self.assert_(doc.hasFile())
    self.assertEquals(doc.getSourceReference(), 'TEST-en-002.doc')
    self.assertEquals(doc.getRevision(), '')
    doc.reindexObject(); get_transaction().commit(); self.tic()

  def stepDialogUpload(self, sequence=None, sequence_list=None, **kw):
    """
      upload a file using dialog
      should increase revision
    """
    dm = self.portal.document_module
    context = getattr(dm, 'one')
    f = makeFileUpload('TEST-en-002.doc')
    context.Document_uploadFile(file=f)
    self.assertEquals(context.getRevision(), '001')
    context.reindexObject(); get_transaction().commit(); self.tic()

  def stepDiscoverFromFilename(self, sequence=None, sequence_list=None, **kw):
    """
      upload file using dialog
      this should trigger metadata discovery and we should have
      basic coordinates immediately, from first stage
    """
    dm = self.portal.document_module
    context = getattr(dm, 'one')
    f = makeFileUpload('TEST-en-002.doc')
    context.Document_uploadFile(file=f)
    self.assertEquals(context.getReference(), 'TEST')
    self.assertEquals(context.getLanguage(), 'en')
    self.assertEquals(context.getVersion(), '002')

  def stepCheckConvertedContent(self, sequence=None, sequence_list=None, **kw):
    """
      check if the input file was successfully converted
      and that it includes what it should
    """
    self.tic()
    dm = self.portal.document_module
    context = getattr(dm, 'one')
    self.assert_(context.hasOOFile())
    self.assert_('magic' in context.SearchableText())

  def stepSetDiscoveryScripts(self, sequence=None, sequence_list=None, **kw):
    """
      Create Text_getPropertyDictFrom[source] scripts
      to simulate custom site's configuration
    """
    dm = self.portal.document_module
    context = getattr(dm, 'one')
    script_id = 'Text_getPropertyDictFromUserLogin'
    factory = context.manage_addProduct['PythonScripts'].manage_addPythonScript
    factory(id=script_id)
    script = getattr(context, script_id)
    script.ZPythonScript_edit('user_name=None',"return {'contributor':'person_module/john'}")
    script_id = 'Text_getPropertyDictFromContent'
    factory(id=script_id)
    script = getattr(context, script_id)
    script.ZPythonScript_edit('', "return {'short_title':'short'}")
    result = context.Text_getPropertyDictFromContent()

  def stepTestMetadataSetting(self, sequence=None, sequence_list=None, **kw):
    """
      Upload with custom getPropertyDict methods
      check that all metadata are correct
    """
    dm = self.portal.document_module
    context = getattr(dm, 'one')
    f = makeFileUpload('TEST-en-002.doc')
    context.Document_uploadFile(file=f)
    get_transaction().commit()
    self.tic()
    # reference from filename (the rest was checked some other place)
    self.assertEquals(context.getReference(), 'TEST')
    # short_title from content
    self.assertEquals(context.getShortTitle(), 'short')
    # contributors from user
    self.assertEquals(context.getContributor(), 'person_module/john')
    # title from metadata inside the doc
    self.assertEquals(context.getTitle(), 'title')

  def stepEditMetadata(self, sequence=None, sequence_list=None, **kw):
    """
      we change metadata in a doc which has ODF
    """
    dm = self.portal.document_module
    context = getattr(dm, 'one')
    kw = dict(title='another title',
              subject='another subject',
              description='another description')
    context.editMetadata(kw)
    # context.edit(**kw) - this works from UI but not from here - is there a problem somewhere?
    context.reindexObject(); get_transaction().commit();
    self.tic(); self.tic();

  def stepCheckChangedMetadata(self, sequence=None, sequence_list=None, **kw):
    """
      then we download it and check if it is changed
    """
    # XXX actually this is an example of how it should be
    # implemented in OOoDocument class - we don't really
    # need oood for getting/setting metadata...
    dm = self.portal.document_module
    context = getattr(dm, 'one')
    newcontent = context.getOOFile()
    cs = cStringIO.StringIO()
    cs.write(unpackData(newcontent))
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
    formats_from = ['rtf', 'doc', 'txt', 'sxw', 'sdw']
    self.ingestFormats('one', formats_from)

  def stepIngestSpreadsheetFormats(self, sequence=None, sequence_list=None, **kw):
    """
      ingest all supported spreadsheet formats
      make sure they are converted
    """
    formats_from = ['xls', 'sxc', 'sdc']
    self.ingestFormats('two', formats_from)

  def stepIngestPresentationFormats(self, sequence=None, sequence_list=None, **kw):
    """
      ingest all supported presentation formats
      make sure they are converted
    """
    formats_from = ['ppt', 'sxi', 'sdd']
    self.ingestFormats('three', formats_from)

  def stepIngestPDFFormats(self, sequence=None, sequence_list=None, **kw):
    """
      ingest all supported PDF formats
      make sure they are converted
    """
    formats_from = ['pdf']
    self.ingestFormats('five', formats_from)

  def stepIngestDrawingFormats(self, sequence=None, sequence_list=None, **kw):
    """
      ingest all supported presentation formats
      make sure they are converted
    """
    formats_from = ['sxd', 'sda']
    self.ingestFormats('four', formats_from)

  def stepIngestPDFFormats(self, sequence=None, sequence_list=None, **kw):
    """
      ingest all supported pdf formats
      make sure they are converted
    """
    formats_from = ['pdf']
    self.ingestFormats('five', formats_from)

  def stepIngestImageFormats(self, sequence=None, sequence_list=None, **kw):
    """
      ingest all supported image formats
    """
    formats_from = ['jpg', 'gif', 'bmp', 'png']
    self.ingestFormats('six', formats_from, 'Image')

  def stepCheckTextDocumentExportList(self, sequence=None, sequence_list=None, **kw):
    self.checkDocumentExportList('one', 'doc', ['pdf', 'doc', 'rtf', 'html-writer', 'txt'])

  def stepCheckSpreadsheetDocumentExportList(self, sequence=None, sequence_list=None, **kw):
    self.checkDocumentExportList('two', 'xls', ['csv', 'html-calc', 'xls', 'calc.pdf'])

  def stepCheckPresentationDocumentExportList(self, sequence=None, sequence_list=None, **kw):
    self.checkDocumentExportList('three', 'ppt', ['impr.pdf', 'ppt'])

  def stepCheckDrawingDocumentExportList(self, sequence=None, sequence_list=None, **kw):
    self.checkDocumentExportList('four', 'sxd', ['jpg', 'draw.pdf', 'svg'])

  def stepExportPDF(self, sequence=None, sequence_list=None, **kw):
    shout('not yet implemented')

  def stepExportImage(self, sequence=None, sequence_list=None, **kw):
    shout('not yet implemented')

  def stepCheckHasSnapshot(self, sequence=None, sequence_list=None, **kw):
    dm = self.portal.document_module
    context = getattr(dm, 'one')
    self.failUnless(context.hasSnapshot())

  def stepCheckHasNoSnapshot(self, sequence=None, sequence_list=None, **kw):
    dm = self.portal.document_module
    context = getattr(dm, 'one')
    self.failIf(context.hasSnapshot())

  def stepCreateSnapshot(self, sequence=None, sequence_list=None, **kw):
    dm = self.portal.document_module
    context = getattr(dm, 'one')
    context.createSnapshot()

  def stepTryRecreateSnapshot(self, sequence=None, sequence_list=None, **kw):
    dm = self.portal.document_module
    context = getattr(dm, 'one')
    # XXX this always fails, don't know why
    #self.assertRaises(ConversionError, context.createSnapshot)

  def stepDeleteSnapshot(self, sequence=None, sequence_list=None, **kw):
    dm = self.portal.document_module
    context = getattr(dm, 'one')
    context.deleteSnapshot()

  def stepContributeFilesWithType(self, sequence=None, sequence_list=None, **kw):
    """
      Contribute all kinds of files giving portal type explicitly
      TODO: test situation whereby portal_type given explicitly is wrong
    """
    self.contributeFiles(with_portal_type=True)

  def stepContributeFilesWithNoType(self, sequence=None, sequence_list=None, **kw):
    """
      Contribute all kinds of files
      let the system figure out portal type by itself
    """
    self.contributeFiles(with_portal_type=False)

  def stepReceiveEmailFromUnknown(self, sequence=None, sequence_list=None, **kw):
    shout('not yet implemented')

  def stepReceiveEmailFromJohn(self, sequence=None, sequence_list=None, **kw):
    shout('not yet implemented')

  def stepVerifyEmailedDocuments(self, sequence=None, sequence_list=None, **kw):
    shout('not yet implemented')


  ##################################
  ##  Tests
  ##################################

  def test_01_checkBasics(self, quiet=QUIET, run=RUN_ALL_TEST):
    if testrun and 1 not in testrun:return
    if not run: return
    if not quiet: shout('test_01_checkBasics')
    sequence_list = SequenceList()
    step_list = [ 'stepCheckPreferences'
                 ,'stepCheckContentTypeRegistry'
                ]
    sequence_string = ' '.join(step_list)
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

  def test_02_TextDoc(self, quiet=QUIET, run=RUN_ALL_TEST):
    """
      Test basic behaviour of a document:
      - create empty doc
      - upload a file directly
      - upload a file using upload dialog
      - make sure revision was increased
      - check that it was properly converted
      - check if coordinates were extracted from file name
    """
    if testrun and 2 not in testrun:return
    if not run: return
    if not quiet: shout('test_02_TextDoc')
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

  def test_03_MetadataExtraction(self, quiet=QUIET, run=RUN_ALL_TEST):
    """
      Test metadata extraction from various sources:
      - from filename (doublecheck)
      - from user (by overwriting type-based method)
      - from content (same way)
      - from file metadata
      We try to verity that all this works
      (order will be tested later)
      
      XXX Metadata of document (title, subject, description)
      are retrieved and set upon conversion, and they
      are not taken into account in the procedure
      so they overwrite what was set before content and
      are overwritten by what was after
      XXX why do we use keywords to set subject_list???
    """
    if testrun and 3 not in testrun:return
    if not run: return
    if not quiet: shout('test_03_MetadataExtraction')
    sequence_list = SequenceList()
    step_list = [ 'stepCreateTextDocument'
                 ,'stepSetDiscoveryScripts'
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
    if testrun and 4 not in testrun:return
    if not run: return
    if not quiet: shout('test_04_MetadataEditing')
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
    if testrun and 5 not in testrun:return
    if not run: return
    if not quiet: shout('test_05_FormatIngestion')
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
      T,est generationof files in all possible formats
      (do we need to test it here? it is tested
      in oood tests...)
      XXX except PDF and Image which should be tested here
      - at least check if they have correct lists of available formats for export
    """
    if testrun and 6 not in testrun:return
    if not run: return
    if not quiet: shout('test_06_FormatGeneration')
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
    if testrun and 7 not in testrun:return
    if not run: return
    if not quiet: shout('test_07_SnapshotGeneration')
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
      I don't know how to verify how cache works - the only
      think I know how to check is change file contents and 
      make sure new version is served
    """

  def test_09_Contribute(self, quiet=QUIET, run=RUN_ALL_TEST):
    """
      Create content through portal_contributions
      - use newContent to ingest various types 
        also to test content_type_registry setup
      - verify that
        - appropriate portal_types were created
        - the files were converted
        - metadata was read
    """
    if testrun and 9 not in testrun:return
    if not run: return
    if not quiet: shout('test_09_Contribute')
    sequence_list = SequenceList()
    step_list = ['stepContributeFilesWithNoType'
                 ,'stepContributeFilesWithType'
                ]
    sequence_string = ' '.join(step_list)
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

  def test_10_MetadataSettingPreferenceOrder(self, quiet=QUIET, run=RUN_ALL_TEST):
    """
      Create a doc, try to set the same metadata from different sources
      check that the right ones remained
      change preference order, check again
    """

  def test_11_EmailIngestion(self, quiet=QUIET, run=RUN_ALL_TEST):
    """
      Simulate email piped to ERP5 by an MTA by uploading test email from file
      Check that document objects are created and appropriate data are set
      (owner, and anything discovered from user and mail body)
    """
    if testrun and 11 not in testrun:return
    if not run: return
    if not quiet: shout('test_09_Contribute')
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


# vim: filetype=python syntax=python shiftwidth=2 
