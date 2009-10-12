##############################################################################
#
# Copyright (c) 2007 Nexedi SA and Contributors. All Rights Reserved.
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
import os
from AccessControl.SecurityManagement import newSecurityManager

import transaction
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.tests.utils import DummyMailHost

class TestQueryModule(ERP5TypeTestCase):
  """Test Query Module, and query actions for all documents
  """

  def getBusinessTemplateList(self):
    return ('erp5_base', )

  def afterSetUp(self):
    portal = self.portal
    self.doc = portal.person_module.newContent(
                      portal_type='Person', id='pers')
    if 'MailHost' in portal.objectIds():
      portal.manage_delObjects(['MailHost'])
    portal._setObject('MailHost', DummyMailHost('MailHost'))

  def beforeTearDown(self):
    transaction.abort()
    # clear modules if necessary
    for module in (self.portal.person_module, self.portal.query_module,):
      module.manage_delObjects(list(module.objectIds()))
    transaction.commit()
    self.tic()

  def test_post_query_action_visible(self):
    # check the action is visible
    action_list = self.portal.portal_actions.listFilteredActionsFor(
                self.doc).get('object_action')
    self.assertEquals(1, len([ai for ai in
            action_list if ai['name'] == 'Post a Query']))

  def test_jump_query_action_visible(self):
    action_list = self.portal.portal_actions.listFilteredActionsFor(
                self.doc).get('object_jump')
    self.assertEquals(1, len([ai for ai in
            action_list if ai['name'] == 'Queries']))

  def test_post_query(self):
    self.doc.Base_postQuery(description='question ?')
    self.assertEquals(len(self.portal.query_module), 1)
    query = self.portal.query_module.contentValues()[0]
    self.assertEquals(self.doc, query.getAgentValue())
    self.assertEquals('Person', query.getTitle())
    self.assertEquals('posted', query.getValidationState())

  def test_reply_query(self):
    self.doc.Base_postQuery(description='question ?')
    query = self.portal.query_module.contentValues()[0]
    self.portal.portal_workflow.doActionFor(
                      query, 'answer_action')
    self.assertEquals('answered', query.getValidationState())


  def test_reply_query_with_persons(self):
    owner_person = self.portal.person_module.newContent(
                    portal_type='Person',
                    reference='owner_user',
                    password='secret',
                    default_email_text='owner_user@example.invalid')
    assignment = owner_person.newContent(portal_type='Assignment')
    assignment.validate()
    question_person = self.portal.person_module.newContent(
                    portal_type='Person',
                    reference='question_user',
                    password='secret',
                    default_email_text='question_user@example.invalid')
    assignment = question_person.newContent(portal_type='Assignment')
    assignment.validate()
    transaction.commit()
    self.tic()
    uf = self.portal.acl_users
    owner_user = uf.getUser('owner_user').__of__(uf)
    question_user = uf.getUser('question_user').__of__(uf)

    # add Author local roles on person and query modules
    self.portal.person_module.manage_setLocalRoles('owner_user', ['Author'])
    self.portal.person_module.manage_setLocalRoles('question_user', ['Author'])
    self.portal.query_module.manage_setLocalRoles('owner_user', ['Author'])
    self.portal.query_module.manage_setLocalRoles('question_user', ['Author'])

    newSecurityManager(None, owner_user)
    doc = self.portal.person_module.newContent(
                                  portal_type='Person',)
    doc.manage_setLocalRoles('owner_user', ['Assignee'])

    newSecurityManager(None, question_user)
    doc.Base_postQuery(description='question ?')
    query = self.portal.query_module.contentValues()[0]
    
    # owner user has an Assignee local role on this query
    self.assertTrue('Assignee' in owner_user.getRolesInContext(query))
 
    newSecurityManager(None, owner_user)
    self.portal.portal_workflow.doActionFor(query, 'answer_action')
    self.assertEquals('answered', query.getValidationState())
    # this should have sent an email from owner_user to question_user
    last_message = self.portal.MailHost._last_message
    self.assertNotEquals((), last_message)
    mfrom, mto, messageText = last_message
    self.assertEquals('owner_user@example.invalid', mfrom)
    self.assertEquals(['question_user@example.invalid'], mto)
    self.assertTrue('Query' in messageText, messageText)


def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestQueryModule))
  return suite
