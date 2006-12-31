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



#
# Skeleton ZopeTestCase
#

from random import randint

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))


class FileObject(file):
  filename=''

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

# XXX set it to an appropriate value
erp5_port=9090

class TestDocument(ERP5TypeTestCase):
  """
  """

  # Different variables used for this test
  run_all_test = 1

  def getTitle(self):
    return "DMS"

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

  def getUserFolder(self):
    return self.getPortal().acl_users

  def createObjects(self):
    if not hasattr(self.getPortal().person_module,'1'):
      p1=self.getPortal().person_module.newContent(portal_type='Person',id='1',first_name='John',last_name='McCartney',reference='john',career_role='internal')
      #self.getWorkflowTool().doActionFor(p1,'validate_action')
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

  def test_01_HasEverything(self, quiet=0, run=run_all_test):
    if not run: return
    if not quiet:
      ZopeTestCase._print('\nTest Has Everything ')
      LOG('Testing... ',0,'testHasEverything')
    self.failUnless(self.getCategoryTool()!=None)
    self.failUnless(self.getSimulationTool()!=None)
    self.failUnless(self.getTypeTool()!=None)
    self.failUnless(self.getSqlConnection()!=None)
    self.failUnless(self.getCatalogTool()!=None)
    self.failUnless(self.getWorkflowTool()!=None)

  def _addRoleToDoc(self,doc):
    role=doc.newContent(portal_type='Role Definition')
    role._edit(agent='person_module/1',role_name='Assignor')

  #def printAndCheck(self,doc):
    #self.assert_(u'Auditor' in doc.__ac_local_roles__.get('HQ',[]))

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

  def test_03_BasicConversion(self,quiet=0,run=run_all_test):
    if not quiet:
      ZopeTestCase._print('\nTest Basic Conversion')
      LOG('Testing... ',0,'test_03_BasicConversion')
    dm=self.getPortal().document_module
    doctext=dm.newContent(portal_type='Text')
    doctext._getServerCoordinate=lambda:('127.0.0.1',8080)
    f=FileObject(os.getenv('INSTANCE_HOME')+'/../Products/ERP5OOo/tests/test.doc')
    f.filename='test.doc'
    doctext._edit(file=f)
    f.close()
    self.assert_(not doctext.hasOOFile())
    ZopeTestCase._print('\n originalloaded '+str(doctext.getSourceReference()))
    ZopeTestCase._print('\n hasOOFile '+str(doctext.hasOOFile()))
    doctext.convert()
    self.assert_(doctext.hasOOFile())
    ZopeTestCase._print('\n hasOOFile '+str(doctext.hasOOFile()))
    tgts=doctext.getTargetFormatItemList()
    tgtext=[t[1] for t in tgts]
    self.assert_('pdf' in tgtext)
    self.assertEquals('keywords',doctext.getSubjectList()[0])
    self.assert_(doctext.getSearchableText().find('adadadfa'))
    
  def test_04_FileGeneration(self,quiet=0,run=run_all_test):
    if not quiet:
      ZopeTestCase._print('\nTest File Generation')
      LOG('Testing... ',0,'test_04_FileGeneration')
    doctext=self.createTestDocument()
    doctext.getTargetFile('pdf')
    self.assert_(doctext.hasConversion(format = 'pdf'))
    doctext.getTargetFile('doc')
    self.assert_(doctext.hasConversion(format = 'doc'))
    doctext.getTargetFile('txt')
    self.assert_(doctext.hasConversion(format = 'txt'))
    doctext.getTargetFile('html-writer')
    self.assert_(doctext.hasConversion(format = 'html-writer'))
    doctext.getTargetFile('rtf')
    self.assert_(doctext.hasConversion(format = 'rtf'))
    self.failIf(doctext.hasSnapshot())
    doctext.createSnapshot()
    self.failUnless(doctext.hasSnapshot())
    # XXX why this line fails???
    # self.assertRaises(ConversionError,doctext.createSnapshot)

  def test_05_OtherFunctions(self,quiet=0,run=run_all_test):
    if not quiet:
      ZopeTestCase._print('\nTest Other Functions')
      LOG('Testing... ',0,'test_05_OtherFunctions')
    doctext=self.createTestDocument()
    #ZopeTestCase._print('\n'+doctext.getCacheInfo())
    mtype=doctext.guessMimeType('file.doc')
    self.assertEquals(mtype,'application/msword')

  def test_06_ExternalDocument(self,quiet=0,run=run_all_test):
    if not quiet:
      ZopeTestCase._print('\nTest External Web Page')
      LOG('Testing... ',0,'test_06_ExternalWeb Page')
    dm=self.getPortal().external_source_module
    doctext=dm.newContent(portal_type='External Web Page')
    self.assert_('http' in doctext.getProtocolList())
    doctext.setUrlProtocol('http')
    doctext.setUrlString('localhost:%i/erp5' % erp5_port)
    doctext.spiderSource()
    if not quiet:
      ZopeTestCase._print(doctext.getExternalProcessingStatusMessage())
      LOG('Testing External Web Page... ',0,doctext.getExternalProcessingStatusMessage())
    self.assert_(doctext.getTextContent().find('My language')>-1)
    


if __name__ == '__main__':
    framework()
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(TestDocument))
        return suite


# vim: syntax=python shiftwidth=2 
