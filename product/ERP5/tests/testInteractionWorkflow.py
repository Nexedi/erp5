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

# Needed in order to have a log file inside the current folder
os.environ['EVENT_LOG_FILE'] = os.path.join(os.getcwd(), 'zLOG.log')
os.environ['EVENT_LOG_SEVERITY'] = '-300'

from Testing import ZopeTestCase
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.Base import _aq_reset
from Products.ERP5.Document.Organisation import Organisation
from Products.ERP5Type.Tool.ClassTool import _aq_reset
from DateTime import DateTime
from Products.ERP5.Document.Person import Person
from AccessControl.SecurityManagement import newSecurityManager, noSecurityManager
from zLOG import LOG
import time

class Test(ERP5TypeTestCase):

  # Different variables used for this test
  run_all_test = 1
  portal_type = 'Organisation'

  def getTitle(self):
    """
    """
    return "Interaction Workflow"


  def getBusinessTemplateList(self):
    """
      Return the list of business templates.

    """
    return ()

  def getPortalId(self):
    return self.getPortal().getId()

  def logMessage(self,message):
    ZopeTestCase._print('\n%s ' % message)
    LOG('Testing... ',0,message)

  def getSalePackingListModule(self):
    return getattr(self.getPortal(),'sale_packing_list',None)

  def getSaleOrderModule(self):
    return getattr(self.getPortal(),'sale_order',None)

  def getOrderLine(self):
    return self.getSaleOrderModule()['1']['1']

  def getPredicate(self):
    return self.getSalePackingListModule()['1']

  def afterSetup(self):
    self.login()
    #self.createData()

  def login(self, quiet=0):
    uf = self.getPortal().acl_users
    uf._doAddUser('seb', '', ['Manager'], [])
    user = uf.getUserById('seb').__of__(uf)
    newSecurityManager(None, user)

  def createData(self):
    organisation_module = self.getOrganisationModule()
    self.organisation = organisation_module.newContent(portal_type=self.portal_type)
    self.organisation.immediateReindexObject()
    def doSomethingStupid(self,value,**kw):
      """
      """
      self.setDescription(value)
    Organisation.doSomethingStupid = doSomethingStupid


  def createInteractionWorkflow(self):
    id = 'test_workflow'
    #wf = InteractionWorfklowDefinition(id)
    wf_type = "interaction_workflow (Web-configurable interaction workflow)"
    self.getWorkflowTool().manage_addWorkflow(workflow_type=wf_type,id=id)
    wf = self.getWorkflowTool()[id]
    self.wf = wf
    wf.scripts.manage_addProduct['PythonScripts'].manage_addPythonScript(id='afterEdit')
    self.script = wf.scripts['afterEdit']
    wf.interactions.addInteraction(id='edit')
    self.interaction = wf.interactions['edit']
    self.getWorkflowTool().setChainForPortalTypes([self.portal_type],'test_workflow')
    _aq_reset() # XXX Fails XXX _setLastId not found when doing newContent


  def test_01(self, quiet=0, run=run_all_test):
    if not run: return
    if not quiet:
      self.logMessage('No Interactions')
    self.createData()
    organisation = self.organisation
    organisation.edit()
    self.assertEquals(organisation.getDescription(),'')

  def test_02(self, quiet=0, run=run_all_test):
    if not run: return
    if not quiet:
      self.logMessage('Interactions On Edit')
    self.createInteractionWorkflow()
    self.interaction.setProperties('afterEdit',method_id='edit',after_script_name=('afterEdit',))
    #body = "sci.object.setDescription('toto')"
    params = 'sci,**kw'
    body = "context = sci.object\n" +\
           "context.setDescription('toto')"
    self.script.ZPythonScript_edit(params,body)
    self.createData()
    organisation = self.organisation
    organisation.edit()
    self.assertEquals(organisation.getDescription(),'toto')

  def test_03(self, quiet=0, run=run_all_test):
    if not run: return
    if not quiet:
      self.logMessage('Interactions, Edit Set Description and also After Script')
    self.createInteractionWorkflow()
    self.interaction.setProperties('afterEdit',method_id='edit',after_script_name=('afterEdit',))
    body = "context = sci.object\n" +\
           "context.setDescription('toto')"
    params = 'sci,**kw'
    self.script.ZPythonScript_edit(params,body)
    self.createData()
    organisation = self.organisation
    organisation.edit(description='tutu')
    self.assertEquals(organisation.getDescription(),'toto')

  def test_04(self, quiet=0, run=run_all_test):
    if not run: return
    if not quiet:
      self.logMessage('Interactions, Automatic Workflow Method')
    self.createInteractionWorkflow()
    self.interaction.setProperties('afterEdit',method_id='doSomethingStupid',after_script_name=('afterEdit',))
    body = "context = sci.object\n" +\
           "context.setDescription('toto')"
    params = 'sci,**kw'
    self.script.ZPythonScript_edit(params,body)
    self.createData()
    organisation = self.organisation
    organisation.doSomethingStupid('tutu')
    self.assertEquals(organisation.getDescription(),'toto')



if __name__ == '__main__':
    framework()
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(Test))
        return suite

