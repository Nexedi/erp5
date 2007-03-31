##############################################################################
#
# Copyright (c) 2004 Nexedi SARL and Contributors. All Rights Reserved.
#          Sebastien Robin <seb@nexedi.com>
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

"""
  A test suite for Document Management System functionality.
  This will test:
  - creating text documents
  - setting properties of a document, assigning local roles
  - setting relations between documents (explicit and implicity)
  - searching in basic and advanced modes
  - document publication workflow settings
  - sourcing external content
  - (...)
  This will NOT test:
  - contributing files of various types
  - convertion between many formats
  - metadata extraction and editing
  - email ingestion
  These are subject to another suite "testIngestion".
"""


#
# Skeleton ZopeTestCase
#

from random import randint

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))


# Needed in order to have a log file inside the current folder
os.environ['EVENT_LOG_FILE'] = os.path.join(os.getcwd(), 'zLOG.log')
os.environ['EVENT_LOG_SEVERITY'] = '-300'

from Testing import ZopeTestCase
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from AccessControl.SecurityManagement import newSecurityManager, noSecurityManager
from DateTime import DateTime
from Acquisition import aq_base, aq_inner
from zLOG import LOG
import os
from Products.ERP5Type import product_path
from Products.ERP5OOo.Document.OOoDocument import ConversionError

class TestDocument(ERP5TypeTestCase):
  """
  """

  # Different variables used for this test
  run_all_test = 1

  def getTitle(self):
    return "DMS"

  ## setup

  def afterSetUp(self, quiet=1, run=1):
    self.createCategories()
    self.createObjects()
    self.login()
    portal = self.getPortal()

  def getDocumentModule(self):
    return getattr(self.getPortal(),'document_module')

  def getBusinessTemplateList(self):
    return ('erp5_base','erp5_trade','erp5_project','erp5_dms')

  def getNeededCategoryList(self):
    return ('function/publication/reviewer','function/project/director','function/hq')

  def createCategories(self):
    """Create the categories for our test. """
    # create categories
    for cat_string in self.getNeededCategoryList():
      base_cat = cat_string.split("/")[0]
      path = self.getPortal().portal_categories[base_cat]
      for cat in cat_string.split("/")[1:]:
        if not cat in path.objectIds():
          path = path.newContent(
            portal_type='Category',
            id=cat,
            immediate_reindex=1)
        else:
          path = path[cat]

  ## helper methods

  def getUserFolder(self):
    return self.getPortal().acl_users

  def createObjects(self):
    if not hasattr(self.getPortal().person_module,'1'):
      p1=self.getPortal().person_module.newContent(portal_type='Person',id='1',first_name='John',last_name='McCartney',reference='john',career_role='internal')
      get_transaction().commit()
      self.tic()

  def getTestUser(self):
    user = self.getUserFolder().getUserById('john')
    self.failIf(user is None)
    return user

  def login(self, quiet=0, run=run_all_test):
    uf = self.getPortal().acl_users
    uf._doAddUser('seb', '', ['Manager'], [])
    user = uf.getUserById('seb').__of__(uf)
    newSecurityManager(None, user)

  def _addRoleToDoc(self,doc):
    role=doc.newContent(portal_type='Role Definition')
    role._edit(agent='person_module/1',role_name='Assignor')

  def createTestDocument(self):
    dm=self.getPortal().document_module
    doctext=dm.newContent(portal_type='Text')
    doctext._getServerCoordinate=lambda:('127.0.0.1',8080)
    f=FileObject(os.getenv('INSTANCE_HOME')+'/../Products/ERP5OOo/tests/test.doc')
    f.filename='test.doc'
    doctext._edit(file=f)
    f.close()
    doctext.convert()
    return doctext

  ## tests

  def test_01_HasEverything(self, quiet=0, run=run_all_test):
    if not run: return
    if not quiet:
      ZopeTestCase._print('\nTest Has Everything ')
      LOG('Testing... ',0,'testHasEverything')
    self.failUnless(self.getCategoryTool()!=None)
    self.failUnless(self.getSimulationTool()!=None)
    self.failUnless(self.getTypeTool()!=None)
    self.failUnless(self.getSQLConnection()!=None)
    self.failUnless(self.getCatalogTool()!=None)
    self.failUnless(self.getWorkflowTool()!=None)

  def test_02_ObjectCreation(self,quiet=0,run=run_all_test):
    if not quiet:
      ZopeTestCase._print('\nTest Object Creation')
      LOG('Testing... ',0,'test_02_ObjectCreation')
    dm=self.getPortal().document_module
    doctext=dm.newContent(portal_type='Text')
    self._addRoleToDoc(doctext)
    get_transaction().commit()
    doctext.updateLocalRolesOnSecurityGroups()
    self.tic()
    u=self.getTestUser()
    self.failUnless('Assignor' in u.getRolesInContext(doctext))

if __name__ == '__main__':
    framework()
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(TestDocument))
        return suite


# vim: syntax=python shiftwidth=2 
