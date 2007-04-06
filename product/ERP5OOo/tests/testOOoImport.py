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
  return os.getenv('INSTANCE_HOME') + '/../Products/ERP5OOo/tests/test_document/' + name

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

  ##################################
  ##  Basic steps
  ##################################

  def stepTic(self, sequence=None, sequence_list=None, **kw):
    self.tic()

  def stepImportRawDataFile(self, sequence=None, sequence_list=None, **kw):
    f = makeFileUpload('import_data_list.ods')
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
