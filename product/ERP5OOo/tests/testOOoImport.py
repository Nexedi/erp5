##############################################################################
#
# Copyright (c) 2005 Nexedi SARL and Contributors. All Rights Reserved.
#                    Nicolas Delaby <nicolas@nexedi.com>
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
import sys
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
    self.headers = {}

def makeFilePath(name):
  return os.getenv('INSTANCE_HOME') + '/../Products/ERP5OOo/tests/data/' + name

def makeFileUpload(name):
  path = makeFilePath(name)
  return FileUploadTest(path, name)

class TestOOoImport(ERP5TypeTestCase):
  """
    ERP5  test import object list from OOo Document
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
    return "ERP5 Site - importing"

  def getBusinessTemplateList(self):
    """
      Return the list of required business templates.
    """
    return ('erp5_base',)

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
    self.unpackData()

  def unpackData(self):
    """
      Unpack the content of testIngestion_docs.zip
    """
    join = os.path.join
    base_path = join(os.getenv('INSTANCE_HOME'), '..', 'Products', 'ERP5OOo', 'tests')
    zf = zipfile.ZipFile(join(base_path, 'testIngestion_docs.zip'))
    data_dir = join(base_path, 'data')
    if not os.path.isdir(data_dir):
      os.mkdir(data_dir)
    for name in zf.namelist():
      fname = join(data_dir, name)
      if not os.path.exists(fname):
        try:
          f = open(fname, 'w')
          f.write(zf.read(name))
        finally:
          f.close()

  def createTools(self):
    """
      Set up contribution tool and content type registry
    """
    # XXX portal_contributions is not created in bootstrap
    # so we have to create it here
    # before we delete in case it was created before and --saved
    try:
      self.portal._delObject('portal_contributions')
    except AttributeError:
      pass
    addTool = self.portal.manage_addProduct['ERP5'].manage_addTool
    addTool('ERP5 Contribution Tool', None)
    # the same for portal_mailin
    try:
      self.portal._delObject('portal_mailin')
    except AttributeError:
      pass
    addTool = self.portal.manage_addProduct['CMFMailIn'].manage_addTool
    addTool('CMF Mail In Tool', None)
    mailin = self.portal.portal_mailin
    mailin.edit_configuration('Document_ingestEmail')

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
                          ,{'path' : 'group/anybody'
                           ,'title': 'Anybody'
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


  ##################################
  ##  Basic steps
  ##################################
 
  def stepTic(self, sequence=None, sequence_list=None, **kw):
    self.tic()

  def stepImportRawDataFile(self, sequence=None, sequence_list=None, **kw):
    f = makeFileUpload('TEST-en-003.ods')
    person_module = self.getPortal().person_module
    #purge existing persons
    person_module.manage_delObjects([id for id in person_module.getObjectIds()])
    get_transaction().commit(); self.tic()
    listbox=(
    { 'listbox_key': '001',
      'portal_type_property_list':'Person.title'},
    { 'listbox_key': '002',
      'portal_type_property_list':'Person.first_name'},
    { 'listbox_key': '003',
      'portal_type_property_list':'Person.last_name'},
    { 'listbox_key': '004',
      'portal_type_property_list':'Person.default_email_text'}
    )
    person_module.ERP5Site_importObjectFromOOo(import_file=f, listbox=listbox)
  
  def stepCheckActivitiesCount(self, sequence=None, sequence_list=None, **kw):
    message_list = self.getPortal().portal_activities.getMessageList()
    self.assertEqual(1,len(message_list))
    method_id = message_list[0].method_id
    self.assertEqual('ERP5Site_importObjectFromOOoActivity',method_id)
  
  def stepCheckImportedPersonList(self, sequence=None, sequence_list=None, **kw):
    person_module = self.getPortal().person_module
    for i in range(101):
      object = person_module['%s' % (i+1)]
      self.assertEqual('John Doe %s' % (i), object.getTitle())
      self.assertEqual('John', object.getFirstName())
      self.assertEqual('Doe %s' % (i), object.getLastName())
      self.assertEqual('john.doe%s@foo.com' % (i), object.getDefaultEmailText())

  ##################################
  ##  Tests
  ##################################

  def test_01_ImportObjectFromOOoInActivities(self, quiet=QUIET, run=RUN_ALL_TEST):
    """
      Simulate import of OOo file true ERP5Site_importObjectFromOOoFastInput
      For Person Module.
    """
    if testrun and 12 not in testrun:return
    if not run: return
    if not quiet: shout('test_12_ImportObjectOOoInActivities')
    sequence_list = SequenceList()
    step_list = [ 'stepImportRawDataFile'
                 ,'stepCheckActivitiesCount'
                 ,'Tic'
                 ,'stepCheckImportedPersonList'
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
    suite.addTest(unittest.makeSuite(TestOOoImport))
    return suite


# vim: filetype=python syntax=python shiftwidth=2 
