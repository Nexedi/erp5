# -*- coding: utf-8 -*-
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

import transaction
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.Base import _aq_reset
from AccessControl import ClassSecurityInfo
from AccessControl.SecurityManagement import newSecurityManager
import Products.ERP5Type
from Products.ERP5Type.Workflow import addWorkflowByType

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

  def beforeTearDown(self):
    Organisation = Products.ERP5.Document.Organisation.Organisation
    Organisation.security.names.pop('doSomethingStupid', None)
    if hasattr(Organisation, 'doSomethingStupid'):
      delattr(Organisation, 'doSomethingStupid')
    if hasattr(Organisation, 'doSomethingStupid__roles__'):
      delattr(Organisation, 'doSomethingStupid__roles__')

  def login(self, quiet=0):
    uf = self.getPortal().acl_users
    uf._doAddUser('seb', '', ['Manager', 'Assignor'], [])
    user = uf.getUserById('seb').__of__(uf)
    newSecurityManager(None, user)

  def createData(self):
    def doSomethingStupid(self,value,**kw):
      """
      """
      self.setDescription(value)
    Organisation = Products.ERP5.Document.Organisation.Organisation
    Organisation.doSomethingStupid = doSomethingStupid
    portal_type = self.getTypeTool()['Organisation']
    portal_type._setTypeBaseCategoryList(['size'])
    organisation_module = self.getOrganisationModule()
    self.organisation = organisation_module.newContent(
                          portal_type = self.portal_type)
    self.organisation.immediateReindexObject()

  def _createInteractionWorkflowWithId(self, wf_id):
    wf_tool = self.getWorkflowTool()
    return addWorkflowByType(wf_tool, "interaction_workflow", wf_id)

  def createInteractionWorkflow(self):
    id = 'test_workflow'
    wf_type = "interaction_workflow"
    if getattr(self.getWorkflowTool(), id, None) is None:
      self._createInteractionWorkflowWithId(id)
    wf = self.getWorkflowTool()[id]
    self.wf = wf
    if getattr(wf.scripts, 'afterEdit', None) is None:
      wf.scripts.manage_addProduct['PythonScripts']\
                    .manage_addPythonScript(id='afterEdit')
    self.script = wf.scripts['afterEdit']
    if getattr(wf.interactions, 'edit_interaction', None) is None:
      wf.interactions.addInteraction(id='edit_interaction')
    self.interaction = wf.interactions['edit_interaction']
    self.getWorkflowTool().setChainForPortalTypes(
                  [self.portal_type],'test_workflow, validation_workflow')
    _aq_reset() # XXX Fails XXX _setLastId not found when doing newContent

  def createInteractionWorkflowWithTwoInteractions(self):
    id = 'test_workflow'
    wf_type = "interaction_workflow (Web-configurable interaction workflow)"
    wf = self._createInteractionWorkflowWithId(id)
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
                  [self.portal_type],'test_workflow, validation_workflow')
    _aq_reset() # XXX Fails XXX _setLastId not found when doing newContent

  def test_01(self, quiet=0, run=run_all_test):
    if not run: return
    if not quiet:
      self.logMessage('No Interactions')
    self.createData()
    organisation = self.organisation
    organisation.edit()
    self.assertEqual(organisation.getDescription(),'')

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
    self.assertEqual(organisation.getDescription(),'toto')

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
    self.assertEqual(organisation.getDescription(),'toto')

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
    self.script.ZPythonScript_edit(params, body)
    self.createData()
    organisation = self.organisation
    organisation.setDescription('bad')
    organisation.doSomethingStupid('tutu')
    self.assertEqual(organisation.getDescription(),'toto')

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
    self.assertEqual(organisation.getDescription(),'toto')

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
    self.assertEqual(organisation.getDescription(),'a')
    organisation.edit()
    self.assertEqual(organisation.getDescription(),'aa')

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
    self.assertEqual(dummy_bank_account.getPortalType(), 'Bank Account')

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
    self.assertEqual(organisation.getDescription(),'a')
    organisation.setActivityCode('acode')
    self.assertEqual(organisation.getDescription(),'aa')

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
           "context.log('InteractionWF.test_11 in script', 'a')\n" +\
           "description = context.getDescription()\n" +\
           "context.setDescription(description + 'a')"
    self.scriptA.ZPythonScript_edit(params, body)
    self.scriptB.ZPythonScript_edit(params, body.replace("'a'", "'b'"))

    self.createData()
    organisation = self.organisation
    organisation._baseSetVatCode('x')
    organisation.setDescription('x')
    self.assertEqual(organisation.getVatCode(),'x')
    self.assertEqual(organisation.getDescription(),'x')
    organisation.edit(description='bar')
    organisation.edit(vat_code='foo')
    self.assertEqual(organisation.getVatCode(),'foo')
    self.assertEqual(organisation.getDescription(),'bara')

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
           "context.log('InteractionWF.test_12 in script', 'a')\n" +\
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
    self.assertEqual(organisation.getDefaultEmailText(),'x')
    self.assertEqual(organisation.getVatCode(),'x')
    organisation.edit(vat_code='foo')
    organisation.edit(default_email_text='bar')
    self.assertEqual(organisation.getVatCode(),'fooa')
    self.assertEqual(organisation.getDefaultEmailText(),'bar')

  def test_13(self, quiet=0, run=run_all_test):
    if not run: return
    if not quiet:
      self.logMessage('Interactions, Check that edit does not detect the '
          'property modified in interaction script as modified by user')
    self.createInteractionWorkflow()
    self.interaction.setProperties(
            'afterEdit',
            method_id='_setTitle',
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
    self.assertEqual(organisation.getTitle(), 'foo')
    self.assertEqual(organisation.getVatCode(), 'bar')

    organisation.edit(title='baz', vat_code='bar', edit_order=['vat_code',
      'title'])
    self.assertEqual(organisation.getTitle(),'baz')
    # here, the wrong behaviour is:
    # - edit:setTitle(baz)
    # - interaction:setVatCode(bara)
    # - edit:setVatCode(bar)
    # whereas, the correct order is:
    # - edit:setTitle(baz)
    # - edit:setVatCode(bar)
    # - interaction:setVatCode(bara)
    self.assertEqual(organisation.getVatCode(),'bara')
    # now, test the other way around
    organisation.edit(title='baz', vat_code='bara', edit_order=['title',
      'vat_code'])
    self.assertEqual(organisation.getTitle(),'baz')
    # here, we assert the failure:
    # - edit:setTitle(baz)
    # - interaction:setVatCode(baraa)
    # - edit:setVatCode(bara)
    self.assertEqual(organisation.getVatCode(),'bara')


  def test_14_BeforeScriptParameters(self, quiet=0, run=run_all_test):
    if not run: return
    if not quiet:
      self.logMessage('Before Script Parameters')
    self.createInteractionWorkflow()
    self.interaction.setProperties(
            'afterEdit',
            method_id='getProperty',
            script_name=('afterEdit',))
    params = 'sci,**kw'
    body = """\
context = sci['object']
kwargs = sci['kwargs'] or {}
d = kwargs.get('d', None)
args = kwargs.get('workflow_method_args', ())
result = kwargs.get('workflow_method_result', None)
context.setDescription('%s,%s,%s' % (d, args, result))
"""
    self.script.ZPythonScript_edit(params,body)
    self.createData()
    organisation = self.organisation
    organisation.setDescription('bad')
    value = organisation.getProperty('description', d='toto')
    self.assertEqual(value, "toto,('description',),None")

  def test_15_AfterScriptParameters(self, quiet=0, run=run_all_test):
    if not run: return
    if not quiet:
      self.logMessage('After Script Parameters')
    self.createInteractionWorkflow()
    self.interaction.setProperties(
            'afterEdit',
            method_id='getProperty',
            after_script_name=('afterEdit',))
    params = 'sci,**kw'
    body = """\
context = sci['object']
kwargs = sci['kwargs'] or {}
d = kwargs.get('d', None)
args = kwargs.get('workflow_method_args', ())
result = kwargs.get('workflow_method_result', None)
context.setDescription('%s,%s,%s' % (d, args, result))
"""
    self.script.ZPythonScript_edit(params,body)
    self.createData()
    organisation = self.organisation
    organisation.setDescription('bad')
    organisation.getProperty('description', d='toto')
    value = organisation.getDescription()
    self.assertEqual(value, "toto,('description',),bad")

  def test_16_BeforeCommitParameters(self, quiet=0, run=run_all_test):
    if not run: return
    if not quiet:
      self.logMessage('Before Commit Script Parameters')
    self.createInteractionWorkflow()
    self.interaction.setProperties(
            'beforeCommit',
            method_id='getProperty',
            before_commit_script_name=('afterEdit',))
    params = 'sci, **kw'
    body = """\
context = sci['object']
kwargs = sci['kwargs'] or {}
d = kwargs.get('d', None)
args = kwargs.get('workflow_method_args', ())
result = kwargs.get('workflow_method_result', None)
context.setDescription('%s,%s,%s' % (d, args, result))
"""
    self.script.ZPythonScript_edit(params, body)
    self.createData()
    organisation = self.organisation
    organisation.setDescription('bad')
    self.assertEqual(organisation.getDescription(), 'bad')
    organisation.getProperty('description', d='toto')
    self.assertEqual(organisation.getDescription(), 'bad')
    # before-commit interactions should be immune to security changes
    self.logout()
    transaction.commit()
    self.login()
    self.assertEqual(organisation.getDescription(), "toto,('description',),bad")

  def test_17_activity_interaction(self, quiet=0, run=run_all_test):
    if not run: return
    if not quiet:
      self.logMessage('Later Script (In activity)')
    self.createInteractionWorkflow()
    self.interaction.setProperties(
            'editObject',
            once_per_transaction=1,
            method_id='_setGroup.*',
            activate_script_name=('afterEdit',))
    params = 'sci, **kw'
    body = """\
context = sci['object']
context.setTitle('Bar')
"""
    self.script.ZPythonScript_edit(params, body)
    self.createData()
    organisation = self.organisation
    organisation.setTitle('Foo')
    organisation.setGroupValue(organisation)
    self.assertEqual(organisation.getTitle(), 'Foo')
    transaction.commit()
    self.assertEqual(organisation.getTitle(), 'Foo')
    self.tic()
    self.assertEqual(organisation.getTitle(), 'Bar')

  def test_18_no_temp_object(self, quiet=0, run=run_all_test):
    if not run: return
    if not quiet:
      self.logMessage('Skips Temp Objects')
    self.createInteractionWorkflow()
    self.interaction.setProperties(
            'editObject',
            temporary_document_disallowed=False,
            method_id='_setGroup.*',
            after_script_name=('afterEdit',))
    params = 'sci, **kw'
    body = """\
context = sci['object']
context.setTitle('Bar')
"""
    self.script.ZPythonScript_edit(params, body)
    self.createData()
    organisation = self.organisation
    temp = organisation.asContext()
    temp.setTitle('Foo')
    # interaction workflows can affect temp objects
    temp.setGroupValue(organisation)
    self.assertEqual(temp.getTitle(), 'Bar')
    # but not if it has been forbidden
    temp.setTitle('Foo')
    self.interaction.setProperties(
            'editObject',
            temporary_document_disallowed=True,
            method_id='_setGroup.*',
            after_script_name=('afterEdit',))
    temp.setGroupValue(None)
    self.assertEqual(temp.getTitle(), 'Foo')

  def test_19_temp_object_doesnt_skip_normal(self, quiet=0, run=run_all_test):
    if not run: return
    if not quiet:
      self.logMessage('Skips Temp Objects, but run in normal objects in the same transaction')
    self.createInteractionWorkflow()
    self.interaction.setProperties(
            'editObject',
            once_per_transaction=True,
            temporary_document_disallowed=True,
            method_id='_setGroup.*',
            after_script_name=('afterEdit',))
    params = 'sci, **kw'
    body = """\
context = sci['object']
context.setTitle('Bar')
"""
    self.script.ZPythonScript_edit(params, body)
    self.createData()
    organisation = self.organisation
    organisation.setTitle('Foo')
    temp = organisation.asContext()
    # temp and organisation have the same path
    self.assertEqual(temp.getPath(), organisation.getPath())
    # which means that a transactional variable key based on path
    # would match both the organisation and the temp object, but
    # triggering the workflow on the temp object should not change it
    # because it's prevented by configuration:
    temp.setGroupValue(organisation)
    self.assertEqual(temp.getTitle(), 'Foo')
    # nor should it change the normal object
    self.assertEqual(organisation.getTitle(), 'Foo')
    # however, it should allow triggering the normal object later on the same
    # transaction
    organisation.setGroupValue(organisation)
    self.assertEqual(organisation.getTitle(), 'Bar')
    # while still not changing the temp object
    self.assertEqual(temp.getTitle(), 'Foo')

  def test_20_temp_object_does_skip_normal(self, quiet=0, run=run_all_test):
    if not run: return
    if not quiet:
      self.logMessage('Runs on temp Objects and skip normal objects')
    self.createInteractionWorkflow()
    self.interaction.setProperties(
            'editObject',
            once_per_transaction=True,
            temporary_document_disallowed=False,
            method_id='_setGroup.*',
            after_script_name=('afterEdit',))
    params = 'sci, **kw'
    body = """\
context = sci['object']
context.setTitle('Bar')
"""
    self.script.ZPythonScript_edit(params, body)
    self.createData()
    organisation = self.organisation
    organisation.setTitle('Foo')
    temp = organisation.asContext()
    # temp and organisation have the same path
    self.assertEqual(temp.getPath(), organisation.getPath())
    # which means that a transactional variable key based on path
    # would match both the organisation and the temp
    # object. Triggering the workflow on the temp object Will change
    # it, since this is not prevented by configuration:
    temp.setGroupValue(organisation)
    self.assertEqual(temp.getTitle(), 'Bar')
    # This should not change the normal object
    self.assertEqual(organisation.getTitle(), 'Foo')
    # However, since the interaction can only run once per transaction
    # (and per object path), it cannot run again on the normal object:
    organisation.setGroupValue(organisation)
    self.assertEqual(organisation.getTitle(), 'Foo')
    # This can be considered an undesired side-effect, so if this test
    # starts failing in the assertion above for a good reason, just
    # fix the test.
    transaction.commit()
    # committing the transaction allows the interaction workflow to
    # run on the normal object again:
    organisation.setGroupValue(None)
    self.assertEqual(organisation.getTitle(), 'Bar')

  def test_regular_expression(self):
    # test that we can add an interaction by defining methods using regular
    # expression
    self.createInteractionWorkflow()
    self.interaction.setProperties(
            'regexp',
            method_id='_set.* set.*',
            after_script_name=('afterEdit',))

    call_list = self.portal.REQUEST['call_list'] = []
    self.script.ZPythonScript_edit('sci',
        'container.REQUEST["call_list"].append(1)')
    self.createData()
    organisation = self.organisation
    # all methods matching set.* regular expression are matched
    organisation.setDescription('')
    # two calls: setDescription, _setDescription
    self.assertEqual(len(call_list), 2)
    organisation.setTitle('')
    # two calls: setTitle, _setTitle
    self.assertEqual(len(call_list), 4)
    organisation.getDescription()
    # no calls
    self.assertEqual(len(call_list), 4)
    organisation.edit(description='desc')
    # two calls: one to _setProperty, and one to _setDescription
    self.assertEqual(len(call_list), 6)


  def test_security(self):
    # wrapping a method in an interaction workflow adds a default security to
    # this method if the method does not exists.
    self.createInteractionWorkflow()
    self.interaction.setProperties(
            'default',
            method_id='nonExistantMethod',
            after_script_name=('afterEdit',))
    self.script.ZPythonScript_edit('sci', '')
    self.createData()
    # the default security is "Access contents information"
    self.organisation.manage_permission(
                      'Access contents information', ['Role1'], 0)
    self.assertEqual(self.organisation.nonExistantMethod__roles__,
                      ('Role1',))

  def test_security_defined(self):
    # wrapping a method in an interaction workflow adds a default security to
    # this method, but does not override existing security definition
    self.createInteractionWorkflow()
    self.interaction.setProperties(
            'default',
            method_id='setDescription',
            after_script_name=('afterEdit',))
    self.script.ZPythonScript_edit('sci', '')
    self.createData()
    # This rely on the fact that 'setDescription' is protected with 'Modify
    # portal content'
    self.organisation.manage_permission(
                     'Modify portal content', ['Role2'], 0)
    self.assertEqual(self.organisation.setDescription__roles__,
                      ('Role2',))

  def test_security_defined_on_class(self):
    # wrapping a method in an interaction workflow adds a default security to
    # this method, but does not override existing security definition (defined
    # on the class)
    Organisation = Products.ERP5.Document.Organisation.Organisation
    security = ClassSecurityInfo()
    security.declarePrivate('doSomethingStupid')
    security.apply(Organisation)

    self.createInteractionWorkflow()
    self.interaction.setProperties(
            'default',
            method_id='doSomethingStupid',
            after_script_name=('afterEdit',))
    self.script.ZPythonScript_edit('sci', '')
    self.createData()

    self.assertEqual(self.organisation.doSomethingStupid__roles__, ())

  def test_wrap_workflow_transition(self):
    self.logMessage('Wrap workflow transition')
    self.createInteractionWorkflow()
    self.interaction.setProperties(
            'default',
            method_id='validate',
            after_script_name=('afterEdit',))
    params = 'sci, **kw'
    body = "context = sci[\'object\']\n" +\
           "context.setDescription('titi')"
    self.script.ZPythonScript_edit(params, body)
    self.createData()
    self.assertEqual('', self.organisation.getDescription())
    self.portal.portal_workflow.doActionFor(self.organisation, 'validate_action')
    self.assertEqual('validated', self.organisation.getValidationState())
    self.assertEqual('titi', self.organisation.getDescription())

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestInteractionWorkflow))
  return suite
