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


import unittest
from Testing import ZopeTestCase
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from AccessControl.SecurityManagement import newSecurityManager
from zLOG import LOG

class Test(ERP5TypeTestCase):
  """
  This is the list of test

  """

  def getTitle(self):
    return "CatalogSecurity"

  def getBusinessTemplateList(self):
    return ('erp5_base',)

  # Different variables used for this test
  run_all_test = 1
  source_company_id = 'Nexedi'
  destination_company_id = 'Coramy'
  component_id = 'brick'
  sales_order_id = '1'
  quantity = 10
  base_price = 0.7832

  #def populate(self, quiet=1, run=1):
  def afterSetUp(self, quiet=1, run=1):
    self.login()
    portal = self.getPortal()
    catalog_tool = self.getCatalogTool()
    # XXX This does not works
    #catalog_tool.reindexObject(portal)

    # First reindex
    #LOG('afterSetup',0,'portal.portal_categories.immediateReindexObject')
    #portal.portal_categories.immediateReindexObject()
    #LOG('afterSetup',0,'portal.portal_simulation.immediateReindexObject')
    #portal.portal_simulation.immediateReindexObject()

  def login(self, username='seb',quiet=0, run=run_all_test):
    uf = self.getPortal().acl_users
    if getattr(uf,'seb',None) is None:
      uf._doAddUser('seb', '', ['Manager'], [])
      uf._addGroup('GroupA')
      uf._addGroup('GroupB')
      uf._doAddUser('UserA', '', ['Member'], [],groups=['GroupA'])
      uf._doAddUser('UserB', '', ['Member'], [],groups=['GroupB'])
    user = uf.getUserById(username).__of__(uf)
    newSecurityManager(None, user)

  def getSQLPathList(self):
    """
    Give the full list of path in the catalog
    """
    sql_connection = self.getSQLConnection()
    sql = 'select path from catalog'
    result = sql_connection.manage_test(sql)
    path_list = map(lambda x: x['path'],result)
    return path_list

  def checkRelativeUrlInSQLPathList(self,url_list):
    path_list = self.getSQLPathList()
    portal_id = self.getPortalId()
    for url in url_list:
      path = '/' + portal_id + '/' + url
      self.failUnless(path in path_list)
      LOG('checkRelativeUrlInSQLPathList found path:',0,path)

  def checkRelativeUrlNotInSQLPathList(self,url_list):
    path_list = self.getSQLPathList()
    portal_id = self.getPortalId()
    for url in url_list:
      path = '/' + portal_id + '/' + url
      self.failUnless(path not in  path_list)
      LOG('checkRelativeUrlInSQLPathList not found path:',0,path)


  def test_01_StandardSearchFolder(self, quiet=0, run=run_all_test):
    # Test if portal_synchronizations was created
    if not run: return
    if not quiet:
      ZopeTestCase._print('\nTest Standard Search Folder ')
      LOG('Testing... ',0,'testStandardSearchFolder')
    organisation_module = self.getOrganisationModule()
    organisation_module.manage_addLocalGroupRoles('GroupA',['Author'])
    organisation_module.manage_addLocalGroupRoles('GroupB',['Author'])
    self.login('UserA')
    organisation_module.newContent(id='A',immediate_reindex=1)
    organisation_list = organisation_module.searchFolder()
    self.assertEquals(len(organisation_list),1)
    self.login('UserB')
    organisation_list = organisation_module.searchFolder()
    self.assertEquals(len(organisation_list),1)

  def test_02_SearchFolderWithNegativeGroup(self, quiet=0, run=run_all_test):
    # Test if portal_synchronizations was created
    if not run: return
    if not quiet:
      ZopeTestCase._print('\nTest Search Folder With Negative Group')
      LOG('Testing... ',0,'testSeachFolderWithNegativeGroup')
    organisation_module = self.getOrganisationModule()
    organisation_module.manage_addLocalGroupRoles('GroupA',['Author'])
    organisation_module.manage_addLocalGroupRoles('GroupB',['Author'])
    self.login('UserA')
    organisation = organisation_module.newContent(id='A',immediate_reindex=1)
    organisation_list = organisation_module.searchFolder()
    self.assertEquals(len(organisation_list),1)
    self.login()
    organisation.manage_addLocalGroupRoles('GroupB',['-Author'])
    organisation.immediateReindexObject()
    self.login('UserB')
    organisation_list = organisation_module.searchFolder()
    self.assertEquals(len(organisation_list),0)


def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(Test))
  return suite

