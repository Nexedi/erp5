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
from DateTime import DateTime
from Products.ERP5.Document.Person import Person
from AccessControl.SecurityManagement import newSecurityManager, noSecurityManager
from zLOG import LOG
import time

class TestInteractionWorkflow(ERP5TypeTestCase):

  # Different variables used for this test
  run_all_test = 1
  portal_type = 'Organisation'

  def getTitle(self):
    """
    """
    return "Interaction Workflow"

  def getBusinessTemplateList(self):
    return ('erp5_base',)

  def afterSetUp(self):
    self.login()

  def login(self, quiet=0):
    uf = self.getPortal().acl_users
    uf._doAddUser('seb', '', ['Manager'], [])
    user = uf.getUserById('seb').__of__(uf)
    newSecurityManager(None, user)

  def createData(self):
    def doSomethingStupid(self,value,**kw):
      """
      """
      self.setDescription(value)
    Organisation.doSomethingStupid = doSomethingStupid
    portal_type = self.getTypeTool()['Organisation']
    portal_type.base_category_list = ['size']
    organisation_module = self.getOrganisationModule()
    self.organisation = organisation_module.newContent(
                          portal_type = self.portal_type)
    self.organisation.immediateReindexObject()

  def createInteractionWorkflow(self):
    id = 'test_workflow'
    wf_type = "interaction_workflow (Web-configurable interaction workflow)"
    self.getWorkflowTool().manage_addWorkflow(workflow_type=wf_type,id=id)
    wf = self.getWorkflowTool()[id]
    self.wf = wf
    wf.scripts.manage_addProduct['PythonScripts']\
                  .manage_addPythonScript(id='afterEdit')
    self.script = wf.scripts['afterEdit']
    wf.interactions.addInteraction(id='edit')
    self.interaction = wf.interactions['edit']
    self.getWorkflowTool().setChainForPortalTypes(
                  [self.portal_type],'test_workflow')
    _aq_reset() # XXX Fails XXX _setLastId not found when doing newContent
  
  def createInteractionWorkflowWithTwoInteractions(self):
    id = 'test_workflow'
    wf_type = "interaction_workflow (Web-configurable interaction workflow)"
    self.getWorkflowTool().manage_addWorkflow(workflow_type=wf_type,id=id)
    wf = self.getWorkflowTool()[id]
    self.wf = wf
    wf.scripts.manage_addProduct['PythonScripts']\
                  .manage_addPythonScript(id='afterEditA')
    self.scriptA = wf.scripts['afterEditA']
    wf.interactions.addInteraction(id='editA')
    self.interactionA = wf.interactions['editA']
    wf.scripts.manage_addProduct['PythonScripts']\
                  .manage_addPythonScript(id='afterEditB')
    self.scriptB = wf.scripts['afterEditB']
    wf.interactions.addInteraction(id='editB')
    self.interactionB = wf.interactions['editB']
    self.getWorkflowTool().setChainForPortalTypes(
                  [self.portal_type],'test_workflow')
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
    self.interaction.setProperties(
            'afterEdit',
            method_id='edit',
            after_script_name=('afterEdit',))
    #body = "sci.object.setDescription('toto')"
    params = 'sci,**kw'
    body = "context = sci.object\n" +\
           "context.setDescription('toto')"
    self.script.ZPythonScript_edit(params,body)
    self.createData()
    organisation = self.organisation
    organisation.setDescription('bad')
    organisation.edit()
    self.assertEquals(organisation.getDescription(),'toto')

  def test_03(self, quiet=0, run=run_all_test):
    if not run: return
    if not quiet:
      self.logMessage(
        'Interactions, Edit Set Description and also After Script')
    self.createInteractionWorkflow()
    self.interaction.setProperties(
            'afterEdit',
            method_id='edit',
            after_script_name=('afterEdit',))
    body = "context = sci.object\n" +\
           "context.setDescription('toto')"
    params = 'sci,**kw'
    self.script.ZPythonScript_edit(params,body)
    self.createData()
    organisation = self.organisation
    organisation.setDescription('bad')
    organisation.edit(description='tutu')
    self.assertEquals(organisation.getDescription(),'toto')

  def test_04(self, quiet=0, run=run_all_test):
    if not run: return
    if not quiet:
      self.logMessage('Interactions, Automatic Workflow Method')
    self.createInteractionWorkflow()
    self.interaction.setProperties(
            'afterEdit',
            method_id='doSomethingStupid',
            after_script_name=('afterEdit',))
    body = "context = sci.object\n" +\
           "context.setDescription('toto')"
    params = 'sci,**kw'
    self.script.ZPythonScript_edit(params,body)
    self.createData()
    organisation = self.organisation
    organisation.setDescription('bad')
    organisation.doSomethingStupid('tutu')
    self.assertEquals(organisation.getDescription(),'toto')

  def test_05(self, quiet=0, run=run_all_test):
    if not run: return
    if not quiet:
      self.logMessage(
        'Interactions, Automatic Workflow Method With Extra Base Category')
    self.createInteractionWorkflow()
    self.interaction.setProperties(
            'afterEdit',
            method_id='setSizeList _setSizeList',
            after_script_name=('afterEdit',))
    body = "context = sci.object\n" +\
           "context.setDescription('toto')"
    params = 'sci,**kw'
    self.script.ZPythonScript_edit(params,body)
    self.createData()
    organisation = self.organisation
    organisation.setDescription('bad')
    organisation.setSizeList(['size/1','size/2'])
    self.assertEquals(organisation.getDescription(),'toto')

  def test_06(self, quiet=0, run=run_all_test):
    if not run: return
    if not quiet:
      self.logMessage('Interactions, Check If There Is Only One Call')
    self.createInteractionWorkflow()
    self.interaction.setProperties(
            'afterEdit',
            method_id='edit',
            after_script_name=('afterEdit',))
    params = 'sci,**kw'
    body = "context = sci.object\n" +\
           "description = context.getDescription()\n" +\
           "context.setDescription(description + 'a')"
    self.script.ZPythonScript_edit(params,body)
    self.createData()
    organisation = self.organisation
    organisation.edit()
    self.assertEquals(organisation.getDescription(),'a')
    organisation.edit()
    self.assertEquals(organisation.getDescription(),'aa')

  def test_07(self, quiet=0, run=run_all_test):
    if not run: return
    if not quiet:
      self.logMessage('Interactions, Check If The Return Value Is Not Altered')
    self.createInteractionWorkflow()
    self.interaction.setProperties(
            'afterEdit',
            method_id='newContent',
            after_script_name=('afterEdit',))
    params = 'sci,**kw'
    body = "context = sci.object\n" +\
           "return 3\n"
    self.script.ZPythonScript_edit(params,body)
    self.createData()
    organisation = self.organisation
    dummy_bank_account = organisation.newContent(
          portal_type='Bank Account',
          id='dummy_bank_account')
    self.assertNotEquals(dummy_bank_account, None)
    self.assertNotEquals(dummy_bank_account, 3)
    self.assertEquals(dummy_bank_account.getPortalType(), 'Bank Account')

  def test_08(self, quiet=0, run=run_all_test):
    if not run: return
    if not quiet:
      self.logMessage('Interactions, Check If Multiple method_id Can Be Hooked')
    self.createInteractionWorkflow()
    self.interaction.setProperties(
            'afterEdit',
            method_id='setCorporateName setActivityCode',
            after_script_name=('afterEdit',))
    params = 'sci,**kw'
    body = "context = sci.object\n" +\
           "description = context.getDescription()\n" +\
           "context.setDescription(description + 'a')"
    self.script.ZPythonScript_edit(params,body)
    self.createData()
    organisation = self.organisation
    organisation.setCorporateName('corp')
    self.assertEquals(organisation.getDescription(),'a')
    organisation.setActivityCode('acode')
    self.assertEquals(organisation.getDescription(),'aa')
    
  def test_09(self, quiet=0, run=run_all_test):
    if not run: return
    if not quiet:
      self.logMessage('Interactions, Check if the same method_id '\
                      'can be hooked by two Interactions')
    self.createInteractionWorkflowWithTwoInteractions()
    self.interactionA.setProperties(
            'afterEditA',
            method_id='edit',
            after_script_name=('afterEditA',))
    self.interactionB.setProperties(
            'afterEditB',
            method_id='edit',
            after_script_name=('afterEditB',))
    params = 'sci,**kw'
    body = "context = sci.object\n" +\
           "context.log('InteractionWF.test_09 in script', 'a')\n" +\
           "description = context.getDescription()\n" +\
           "context.setDescription(description + 'a')"
    self.scriptA.ZPythonScript_edit(params, body)
    self.scriptB.ZPythonScript_edit(params, body.replace("'a'", "'b'"))
    
    self.createData()
    organisation = self.organisation
    organisation.edit()
    self.assert_(organisation.getDescription() in ('ab', 'ba'),
        "description should be 'ab' or 'ba', it is %s" %
        organisation.getDescription())
    organisation.setCorporateName("this should not change anything")
    self.assert_(organisation.getDescription() in ('ab', 'ba'),
        "description should be 'ab' or 'ba', it is %s" %
        organisation.getDescription())
    
  def test_10(self, quiet=0, run=run_all_test):
    if not run: return
    if not quiet:
      self.logMessage('Interactions, check if multiple scripts can be '
                      'called')
    self.createInteractionWorkflowWithTwoInteractions()
    self.interactionA.setProperties(
            'afterEdit',
            method_id='edit',
            after_script_name=('afterEditA', 'afterEditB'))
    params = 'sci,**kw'
    body = "context = sci.object\n" +\
           "context.log('InteractionWF.test_10 in script', 'a')\n" +\
           "description = context.getDescription()\n" +\
           "context.setDescription(description + 'a')"
    self.scriptA.ZPythonScript_edit(params, body)
    self.scriptB.ZPythonScript_edit(params, body.replace("'a'", "'b'"))
    
    self.createData()
    organisation = self.organisation
    organisation.edit()
    self.assert_(organisation.getDescription() in ('ab', 'ba'),
        "description should be 'ab' or 'ba', it is %s" %
        organisation.getDescription())
    organisation.setCorporateName("this should not change anything")
    self.assert_(organisation.getDescription() in ('ab', 'ba'),
        "description should be 'ab' or 'ba', it is %s" %
        organisation.getDescription())
    
  def test_11(self, quiet=0, run=run_all_test):
    if not run: return
    if not quiet:
      self.logMessage(
        'Interactions, Test that the private accessor is called')

    self.createInteractionWorkflowWithTwoInteractions()
    self.interactionA.setProperties(
            'afterEditA',
            method_id='_setVatCode',
            after_script_name=('afterEditA',))
    self.interactionB.setProperties(
            'afterEditB',
            method_id='setVatCode',
            after_script_name=('afterEditB',))
    params = 'sci,**kw'
    body = "context = sci.object\n" +\
           "context.log('InteractionWF.test_10 in script', 'a')\n" +\
           "description = context.getDescription()\n" +\
           "context.setDescription(description + 'a')"
    self.scriptA.ZPythonScript_edit(params, body)
    self.scriptB.ZPythonScript_edit(params, body.replace("'a'", "'b'"))

    self.createData()
    organisation = self.organisation
    organisation._baseSetVatCode('x')
    organisation.setDescription('x')
    self.assertEquals(organisation.getVatCode(),'x')
    self.assertEquals(organisation.getDescription(),'x')
    organisation.edit(description='bar')
    organisation.edit(vat_code='foo')
    self.assertEquals(organisation.getVatCode(),'foo')
    self.assertEquals(organisation.getDescription(),'bara')

  def test_12(self, quiet=0, run=run_all_test):
    if not run: return
    if not quiet:
      self.logMessage(
        'Interactions, Test that the private accessor is called, '
        'when using an Acquired Property')

    self.createInteractionWorkflowWithTwoInteractions()
    self.interactionA.setProperties(
            'afterEditA',
            method_id='_setDefaultEmailText',
            after_script_name=('afterEditA',))
    self.interactionB.setProperties(
            'afterEditB',
            method_id='setDefaultEmailText',
            after_script_name=('afterEditB',))
    params = 'sci,**kw'
    body = "context = sci.object\n" +\
           "context.log('InteractionWF.test_10 in script', 'a')\n" +\
           "vat_code = context.getVatCode()\n" +\
           "if vat_code is None:\n" +\
           "  vat_code = ''\n" +\
           "context.setVatCode(vat_code + 'a')"
    self.scriptA.ZPythonScript_edit(params, body)
    self.scriptB.ZPythonScript_edit(params, body.replace("'a'", "'b'"))

    self.createData()
    organisation = self.organisation
    organisation._baseSetDefaultEmailText('x')
    organisation.setVatCode('x')
    self.assertEquals(organisation.getDefaultEmailText(),'x')
    self.assertEquals(organisation.getVatCode(),'x')
    organisation.edit(vat_code='foo')
    organisation.edit(default_email_text='bar')
    self.assertEquals(organisation.getVatCode(),'fooa')
    self.assertEquals(organisation.getDefaultEmailText(),'bar')

  def test_13(self, quiet=0, run=run_all_test):
    if not run: return
    if not quiet:
      self.logMessage('Interactions, Check that edit does not detect the '
          'property modified in interaction script as modified by user')
    self.createInteractionWorkflow()
    self.interaction.setProperties(
            'afterEdit',
            method_id='setTitle',
            after_script_name=('afterEdit',))
    params = 'sci,**kw'
    body = "context = sci.object\n" +\
           "vat_code = context.getVatCode()\n" +\
           "if vat_code is None:\n" +\
           "  vat_code = ''\n" +\
           "context.setVatCode(vat_code + 'a')"
    self.script.ZPythonScript_edit(params,body)
    self.createData()
    organisation = self.organisation
    organisation.setTitle('foo')
    organisation.setVatCode('bar')
    self.assertEquals(organisation.getTitle(), 'foo')
    self.assertEquals(organisation.getVatCode(), 'bar')

    organisation.edit(title='baz', vat_code='bar')
    self.assertEquals(organisation.getTitle(),'baz')
    # here, the wrong behaviour was:
    # - edit:setTitle(baz)
    # - interaction:setVatCode(bara)
    # - edit:setVatCode(bar)
    # whereas, the correct order is:
    # - edit:setTitle(baz)
    # - edit:setVatCode(bar)
    # - interaction:setVatCode(bara)
    self.assertEquals(organisation.getVatCode(),'bara')
    
if __name__ == '__main__':
    framework()
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(TestInteractionWorkflow))
        return suite

