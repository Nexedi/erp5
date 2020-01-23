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
import httplib
import transaction

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.Base import _aq_reset
import Products.ERP5
from AccessControl import ClassSecurityInfo
from Products.ERP5Type.Workflow import addWorkflowByType

class TestInteractionWorkflow(ERP5TypeTestCase):
  portal_type = 'Organisation'

  def getTitle(self):
    return "Interaction Workflow"

  def getBusinessTemplateList(self):
    return ('erp5_base',)

  def beforeTearDown(self):
    transaction.abort()
    self.tic()
    Organisation = Products.ERP5.Document.Organisation.Organisation
    Organisation.security.names.pop('doSomethingStupid', None)
    if hasattr(Organisation, 'doSomethingStupid'):
      delattr(Organisation, 'doSomethingStupid')
    if hasattr(Organisation, 'doSomethingStupid__roles__'):
      delattr(Organisation, 'doSomethingStupid__roles__')
    # delete workflows
    workflow_tool = self.getWorkflowTool()
    if 'test_workflow' in workflow_tool.objectIds():
      workflow_tool.manage_delObjects(['test_workflow'])
    _aq_reset()
    self.tic()

  def afterSetUp(self):
    def doSomethingStupid(self,value,**kw):
      """A patched method
      """
      self.setDescription(value)
    Organisation = Products.ERP5.Document.Organisation.Organisation
    Organisation.doSomethingStupid = doSomethingStupid
    portal_type = self.getTypeTool()['Organisation']
    portal_type._setTypeBaseCategoryList(['size'])
    organisation_module = self.getOrganisationModule()
    self.organisation = organisation_module.newContent(
                          portal_type = self.portal_type)

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

  def test_no_interactions(self):
    organisation = self.organisation
    organisation.edit()
    self.assertEqual(organisation.getDescription(),'')

  def test_edit_interaction(self):
    self.createInteractionWorkflow()
    self.interaction.setProperties(
            'afterEdit',
            method_id='edit',
            after_script_name=('afterEdit',))
    params = 'sci,**kw'
    body = "context = sci.object\n" +\
           "context.setDescription('toto')"
    self.script.ZPythonScript_edit(params,body)
    organisation = self.organisation
    organisation.setDescription('bad')
    organisation.edit()
    self.assertEqual(organisation.getDescription(),'toto')

  def test_interaction_on_edit(self):
    self.createInteractionWorkflow()
    self.interaction.setProperties(
            'afterEdit',
            method_id='edit',
            after_script_name=('afterEdit',))
    body = "context = sci.object\n" +\
           "context.setDescription('toto')"
    params = 'sci,**kw'
    self.script.ZPythonScript_edit(params,body)
    organisation = self.organisation
    organisation.setDescription('bad')
    organisation.edit(description='tutu')
    self.assertEqual(organisation.getDescription(),'toto')

  def test_interaction_on_method(self):
    self.createInteractionWorkflow()
    self.interaction.setProperties(
            'afterEdit',
            method_id='doSomethingStupid',
            after_script_name=('afterEdit',))
    body = "context = sci.object\n" +\
           "context.setDescription('toto')"
    params = 'sci,**kw'
    self.script.ZPythonScript_edit(params, body)
    organisation = self.organisation
    organisation.setDescription('bad')
    organisation.doSomethingStupid('tutu')
    self.assertEqual(organisation.getDescription(),'toto')

  def test_interaction_on_category_setter(self):
    self.createInteractionWorkflow()
    self.interaction.setProperties(
            'afterEdit',
            method_id='setSizeList _setSizeList',
            after_script_name=('afterEdit',))
    body = "context = sci.object\n" +\
           "context.setDescription('toto')"
    params = 'sci,**kw'
    self.script.ZPythonScript_edit(params,body)
    organisation = self.organisation
    organisation.setDescription('bad')
    organisation.setSizeList(['size/1','size/2'])
    self.assertEqual(organisation.getDescription(),'toto')

  def test_interaction_executed_once(self):
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
    organisation = self.organisation
    organisation.edit()
    self.assertEqual(organisation.getDescription(),'a')
    organisation.edit()
    self.assertEqual(organisation.getDescription(),'aa')

  def test_returned_value(self):
    self.createInteractionWorkflow()
    self.interaction.setProperties(
            'afterEdit',
            method_id='newContent',
            after_script_name=('afterEdit',))
    params = 'sci,**kw'
    body = "context = sci.object\n" +\
           "return 3\n"
    self.script.ZPythonScript_edit(params,body)
    organisation = self.organisation
    dummy_bank_account = organisation.newContent(
          portal_type='Bank Account',
          id='dummy_bank_account')
    self.assertNotEquals(dummy_bank_account, 3)
    self.assertEqual(dummy_bank_account.getPortalType(), 'Bank Account')

  def test_multiple_methods(self):
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
    organisation = self.organisation
    organisation.setCorporateName('corp')
    self.assertEqual(organisation.getDescription(),'a')
    organisation.setActivityCode('acode')
    self.assertEqual(organisation.getDescription(),'aa')

  def test_same_method_two_interactions(self):
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

    organisation = self.organisation
    organisation.edit()
    self.assert_(organisation.getDescription() in ('ab', 'ba'),
        "description should be 'ab' or 'ba', it is %s" %
        organisation.getDescription())
    organisation.setCorporateName("this should not change anything")
    self.assert_(organisation.getDescription() in ('ab', 'ba'),
        "description should be 'ab' or 'ba', it is %s" %
        organisation.getDescription())

  def test_multiple_scripts(self):
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

    organisation = self.organisation
    organisation.edit()
    self.assert_(organisation.getDescription() in ('ab', 'ba'),
        "description should be 'ab' or 'ba', it is %s" %
        organisation.getDescription())
    organisation.setCorporateName("this should not change anything")
    self.assert_(organisation.getDescription() in ('ab', 'ba'),
        "description should be 'ab' or 'ba', it is %s" %
        organisation.getDescription())

  def test_private_accessor(self):
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

    organisation = self.organisation
    organisation._baseSetVatCode('x')
    organisation.setDescription('x')
    self.assertEqual(organisation.getVatCode(),'x')
    self.assertEqual(organisation.getDescription(),'x')
    organisation.edit(description='bar')
    organisation.edit(vat_code='foo')
    self.assertEqual(organisation.getVatCode(),'foo')
    self.assertEqual(organisation.getDescription(),'bara')

  def test_private_accessor_on_acquired_property(self):
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

    organisation = self.organisation
    organisation._baseSetDefaultEmailText('x')
    organisation.setVatCode('x')
    self.assertEqual(organisation.getDefaultEmailText(),'x')
    self.assertEqual(organisation.getVatCode(),'x')
    organisation.edit(vat_code='foo')
    organisation.edit(default_email_text='bar')
    self.assertEqual(organisation.getVatCode(),'fooa')
    self.assertEqual(organisation.getDefaultEmailText(),'bar')

  def test_edit_modied_property(self):
    # Check that edit does not detect the property modified in interaction
    # script as modified by user
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


  def test_BeforeScriptParameters(self):
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
    organisation = self.organisation
    organisation.setDescription('bad')
    value = organisation.getProperty('description', d='toto')
    self.assertEqual(value, "toto,('description',),None")

  def test_AfterScriptParameters(self):
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
    organisation = self.organisation
    organisation.setDescription('bad')
    organisation.getProperty('description', d='toto')
    value = organisation.getDescription()
    self.assertEqual(value, "toto,('description',),bad")

  def test_BeforeCommitParameters(self):
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
    organisation = self.organisation
    organisation.setDescription('bad')
    self.assertEqual(organisation.getDescription(), 'bad')
    organisation.getProperty('description', d='toto')
    self.assertEqual(organisation.getDescription(), 'bad')
    # before-commit interactions should be immune to security changes
    self.logout()
    self.commit()
    self.login()
    self.assertEqual(organisation.getDescription(), "toto,('description',),bad")

    # Delete the organisation, because this test modifies the objects each time
    # getProperty is called, which creates an infinite loop during indexing
    self.getOrganisationModule().manage_delObjects([self.organisation.getId()])
    self.commit()

  def test_activity_interaction(self):
    # Tests for Later Script (in activity)
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
    organisation = self.organisation
    organisation.setTitle('Foo')
    organisation.setGroupValue(organisation)
    self.assertEqual(organisation.getTitle(), 'Foo')
    self.commit()
    self.assertEqual(organisation.getTitle(), 'Foo')
    self.tic()
    self.assertEqual(organisation.getTitle(), 'Bar')

  def test_skip_temp_object(self):
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

  def test_temp_object_doesnt_skip_normal(self):
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

  def test_temp_object_does_skip_normal(self):
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
    self.commit()
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

  def test_interaction_workflow_methods_are_published(self):
    """Wrapping a publishable method in an interaction workflow does not prevent its publication.
    """
    self.assertIsNotNone(self.organisation.getTitle.__doc__)
    self.createInteractionWorkflow()
    self.interaction.setProperties('default', method_id='getTitle')
    self.assertIsNotNone(self.organisation.getTitle.__doc__)

    self.organisation.setTitle(self.id())
    ret = self.publish('%s/getTitle' % self.organisation.getPath(), basic='ERP5TypeTestCase:')
    self.assertEqual(httplib.OK, ret.getStatus())
    self.assertEqual(self.id(), ret.getBody())

  def test_security(self):
    # wrapping a method in an interaction workflow adds a default security to
    # this method if the method does not exists.
    self.createInteractionWorkflow()
    self.interaction.setProperties(
            'default',
            method_id='nonExistantMethod',
            after_script_name=('afterEdit',))
    self.script.ZPythonScript_edit('sci', '')
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

    self.assertEqual(self.organisation.doSomethingStupid__roles__, ())

  def test_wrap_workflow_transition(self):
    self.createInteractionWorkflow()
    self.interaction.setProperties(
            'default',
            method_id='validate',
            after_script_name=('afterEdit',))
    params = 'sci, **kw'
    body = "context = sci[\'object\']\n" +\
           "context.setDescription('titi')"
    self.script.ZPythonScript_edit(params, body)
    self.assertEqual('', self.organisation.getDescription())
    self.portal.portal_workflow.doActionFor(self.organisation, 'validate_action')
    self.assertEqual('validated', self.organisation.getValidationState())
    self.assertEqual('titi', self.organisation.getDescription())

  def test_portal_type_filter(self):
    self.createInteractionWorkflow()
    self.getWorkflowTool().setChainForPortalTypes(
                  ['Bank Account'],'test_workflow, validation_workflow')
    self.interaction.setProperties(
            'default',
            # only for bank accounts
            portal_type_filter=['Bank Account'],
            method_id='getReference',
            after_script_name=('afterEdit',))
    params = 'sci, **kw'
    body = "context = sci[\'object\']\n" +\
           "context.setDescription('modified')"
    self.script.ZPythonScript_edit(params, body)

    bank_account = self.organisation.newContent(
      portal_type='Bank Account')
    self.assertEqual('', bank_account.getDescription())

    self.organisation.getReference()
    self.assertEqual('', self.organisation.getDescription())

    bank_account.getReference()
    self.assertEqual('modified', bank_account.getDescription())

  def test_portal_type_group_filter(self):
    self.createInteractionWorkflow()
    self.getWorkflowTool().setChainForPortalTypes(
                  ['Bank Account'],'test_workflow, validation_workflow')
    self.interaction.setProperties(
            'default',
            # only for payment nodes portal type group (ie. bank account)
            portal_type_group_filter=['payment_node'],
            method_id='getReference',
            after_script_name=('afterEdit',))
    params = 'sci, **kw'
    body = "context = sci[\'object\']\n" +\
           "context.setDescription('modified')"
    self.script.ZPythonScript_edit(params, body)

    bank_account = self.organisation.newContent(
      portal_type='Bank Account')
    self.assertEqual('', bank_account.getDescription())

    self.organisation.getReference()
    self.assertEqual('', self.organisation.getDescription())

    bank_account.getReference()
    self.assertEqual('modified', bank_account.getDescription())



def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestInteractionWorkflow))
  return suite
