# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2005-2009 Nexedi SA and Contributors. All Rights Reserved.
#                    Jerome Perrin <jerome@nexedi.com>
#                    Łukasz Nowak <luke@nexedi.com>
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
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import noSecurityManager
from AccessControl.SecurityManagement import getSecurityManager
from zExceptions import Unauthorized
from DateTime import DateTime

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Form.Document.Preference import Priority


class TestPreferences(ERP5TypeTestCase):

  def getTitle(self):
    return "Portal Preference"

  def afterSetUp(self):
    uf = self.getPortal().acl_users
    uf._doAddUser('manager', '', ['Manager', 'Assignor', ], [])
    user = uf.getUserById('manager').__of__(uf)
    newSecurityManager(None, user)
    self.createPreferences()

  def beforeTearDown(self):
    portal_preferences = self.getPreferenceTool()
    portal_preferences.manage_delObjects(list(portal_preferences.objectIds()))
    transaction.commit()
    self.tic()

  def createPreferences(self):
    """ create some preferences objects  """
    portal_preferences = self.getPreferenceTool()
    ## create initial preferences
    person1 = portal_preferences.newContent(
        id='person1', portal_type='Preference')
    person2 = portal_preferences.newContent(
        id='person2', portal_type='Preference')
    group = portal_preferences.newContent(
        id='group', portal_type='Preference')
    group.setPriority(Priority.GROUP)
    site = portal_preferences.newContent(
        id='site', portal_type='Preference')
    site.setPriority(Priority.SITE)

    # commit transaction
    transaction.commit()
    self.getPreferenceTool().recursiveReindexObject()
    self.tic()

    # check preference levels are Ok
    self.assertEquals(person1.getPriority(), Priority.USER)
    self.assertEquals(person2.getPriority(), Priority.USER)
    self.assertEquals(group.getPriority(),   Priority.GROUP)
    self.assertEquals(site.getPriority(),    Priority.SITE)
    # check initial states
    self.assertEquals(person1.getPreferenceState(), 'disabled')
    self.assertEquals(person2.getPreferenceState(), 'disabled')
    self.assertEquals(group.getPreferenceState(),   'disabled')
    self.assertEquals(site.getPreferenceState(),    'disabled')

  def test_PreferenceToolTitle(self):
    """Tests that the title of the preference tool is correct.
    """
    self.assertEquals('Preferences', self.getPreferenceTool().Title())

  def test_AllowedContentTypes(self):
    """Tests Preference can be added in Preference Tool.
    """
    self.failUnless('Preference' in [x.getId() for x in
           self.getPortal().portal_preferences.allowedContentTypes()])

  def test_EnablePreferences(self):
    """ tests preference workflow """
    portal_workflow = self.getWorkflowTool()
    person1 = self.getPreferenceTool()['person1']
    person2 = self.getPreferenceTool()['person2']
    group = self.getPreferenceTool()['group']
    site = self.getPreferenceTool()['site']

    person1.portal_workflow.doActionFor(
       person1, 'enable_action', wf_id='preference_workflow')
    self.assertEquals(person1.getPreferenceState(), 'enabled')

    portal_workflow.doActionFor(
       site, 'enable_action', wf_id='preference_workflow')
    self.assertEquals(person1.getPreferenceState(), 'enabled')
    self.assertEquals(site.getPreferenceState(),    'global')

    portal_workflow.doActionFor(
       group, 'enable_action', wf_id='preference_workflow')
    self.assertEquals(person1.getPreferenceState(), 'enabled')
    self.assertEquals(group.getPreferenceState(),   'enabled')
    self.assertEquals(site.getPreferenceState(),    'global')

    portal_workflow.doActionFor(
       person2, 'enable_action', wf_id='preference_workflow')
    self.assertEquals(person2.getPreferenceState(), 'enabled')
    # enabling a preference disable all other of the same level
    self.assertEquals(person1.getPreferenceState(), 'disabled')
    self.assertEquals(group.getPreferenceState(),   'enabled')
    self.assertEquals(site.getPreferenceState(),    'global')

  def test_GetPreference(self):
    """ checks that getPreference returns the good preferred value"""
    portal_workflow = self.getWorkflowTool()
    pref_tool = self.getPreferenceTool()
    person1 = self.getPreferenceTool()['person1']
    group = self.getPreferenceTool()['group']
    site = self.getPreferenceTool()['site']

    portal_workflow.doActionFor(
       person1, 'enable_action', wf_id='preference_workflow')
    portal_workflow.doActionFor(
       group, 'enable_action', wf_id='preference_workflow')
    portal_workflow.doActionFor(
       site, 'enable_action', wf_id='preference_workflow')
    self.assertEquals(person1.getPreferenceState(), 'enabled')
    self.assertEquals(group.getPreferenceState(),   'enabled')
    self.assertEquals(site.getPreferenceState(),    'global')
    person1.setPreferredAccountingTransactionSimulationState([])
    self.assertEquals(
      person1.getPreferredAccountingTransactionSimulationState(), None)
    group.setPreferredAccountingTransactionSimulationState([])
    self.assertEquals(
      group.getPreferredAccountingTransactionSimulationState(), None)
    site.setPreferredAccountingTransactionSimulationState([])
    self.assertEquals(
      site.getPreferredAccountingTransactionSimulationState(), None)

    self.assertEquals(len(pref_tool.getPreference(
      'preferred_accounting_transaction_simulation_state_list')), 0)

    site.edit(
      preferred_accounting_transaction_simulation_state_list=
      ['stopped', 'delivered'])
    self.assertEquals(list(pref_tool.getPreference(
      'preferred_accounting_transaction_simulation_state_list')),
      list(site.getPreferredAccountingTransactionSimulationStateList()))

    # getPreference on the tool has the same behaviour as getProperty
    # on the preference (unless property is unset on this pref)
    for prop in ['preferred_accounting_transaction_simulation_state',
            'preferred_accounting_transaction_simulation_state_list']:

      self.assertEquals(pref_tool.getPreference(prop),
                        site.getProperty(prop))

    group.edit(
      preferred_accounting_transaction_simulation_state_list=['draft'])
    self.assertEquals(list(pref_tool.getPreference(
      'preferred_accounting_transaction_simulation_state_list')),
      list(group.getPreferredAccountingTransactionSimulationStateList()))

    person1.edit(preferred_accounting_transaction_simulation_state_list=
              ['cancelled'])
    self.assertEquals(list(pref_tool.getPreference(
      'preferred_accounting_transaction_simulation_state_list')),
      list(person1.getPreferredAccountingTransactionSimulationStateList()))
    # disable person -> group is selected
    self.getWorkflowTool().doActionFor(person1,
            'disable_action', wf_id='preference_workflow')
    self.assertEquals(list(pref_tool.getPreference(
      'preferred_accounting_transaction_simulation_state_list')),
      list(group.getPreferredAccountingTransactionSimulationStateList()))

    self.assertEquals('default', pref_tool.getPreference(
                                        'this_does_not_exists', 'default'))


  def test_GetAttr(self):
    """ checks that preference methods can be called directly
      on portal_preferences """
    portal_workflow = self.getWorkflowTool()
    pref_tool = self.getPreferenceTool()
    person1 = self.getPreferenceTool()['person1']
    group = self.getPreferenceTool()['group']
    site = self.getPreferenceTool()['site']
    self.assertEquals(person1.getPreferenceState(), 'disabled')
    portal_workflow.doActionFor(
       group, 'enable_action', wf_id='preference_workflow')
    self.assertEquals(group.getPreferenceState(),    'enabled')
    portal_workflow.doActionFor(
       site, 'enable_action', wf_id='preference_workflow')
    self.assertEquals(site.getPreferenceState(),     'global')
    group.setPreferredAccountingTransactionSimulationStateList(['cancelled'])

    self.assertNotEquals( None,
      pref_tool.getPreferredAccountingTransactionSimulationStateList())
    self.assertNotEquals( [],
      list(pref_tool.getPreferredAccountingTransactionSimulationStateList()))
    self.assertEquals(
      list(pref_tool.getPreferredAccountingTransactionSimulationStateList()),
      list(pref_tool.getPreference(
         'preferred_accounting_transaction_simulation_state_list')))
    # standards attributes must not be looked up on Preferences
    self.assertNotEquals(pref_tool.getTitleOrId(), group.getTitleOrId())
    self.assertNotEquals(pref_tool.objectValues(), group.objectValues())
    self.assertNotEquals(pref_tool.getParentValue(), group.getParentValue())
    try :
      pref_tool.getPreferredNotExistingPreference()
      self.fail('Attribute error should be raised for dummy methods')
    except AttributeError :
      pass

  def test_SetPreference(self):
    """ check setting a preference modifies
     the first enabled user preference """
    portal_workflow = self.getWorkflowTool()
    pref_tool = self.getPreferenceTool()
    person1 = self.getPreferenceTool()['person1']

    portal_workflow.doActionFor(
       person1, 'enable_action', wf_id='preference_workflow')
    self.assertEquals(person1.getPreferenceState(),    'enabled')
    person1.setPreferredAccountingTransactionAtDate(DateTime(2005, 01, 01))
    pref_tool.setPreference(
      'preferred_accounting_transaction_at_date', DateTime(2004, 12, 31))
    self.tic()
    self.assertEquals(
      pref_tool.getPreferredAccountingTransactionAtDate(),
      DateTime(2004, 12, 31))
    self.assertEquals(
      person1.getPreferredAccountingTransactionAtDate(),
      DateTime(2004, 12, 31))

  def test_UserIndependance(self):
    """ check that the preferences are related to the user. """
    portal_workflow = self.getWorkflowTool()
    portal_preferences = self.getPreferenceTool()
    # create 2 users: user_a and user_b
    uf = self.getPortal().acl_users
    uf._doAddUser('user_a', '', ['Member', ], [])
    user_a = uf.getUserById('user_a').__of__(uf)
    uf._doAddUser('user_b', '', ['Member', ], [])
    user_b = uf.getUserById('user_b').__of__(uf)

    # log as user_a
    newSecurityManager(None, user_a)

    # create 2 prefs as user_a
    user_a_1 = portal_preferences.newContent(
        id='user_a_1', portal_type='Preference')
    user_a_2 = portal_preferences.newContent(
        id='user_a_2', portal_type='Preference')
    transaction.commit(); self.tic()

    # enable a pref
    portal_workflow.doActionFor(
       user_a_1, 'enable_action', wf_id='preference_workflow')
    self.assertEquals(user_a_1.getPreferenceState(), 'enabled')
    self.assertEquals(user_a_2.getPreferenceState(), 'disabled')

    # log as user_b
    newSecurityManager(None, user_b)

    # create a pref for user_b
    user_b_1 = portal_preferences.newContent(
        id='user_b_1', portal_type='Preference')
    user_b_1.setPreferredAccountingTransactionAtDate(DateTime(2002, 02, 02))
    transaction.commit(); self.tic()

    # enable this preference
    portal_workflow.doActionFor(
       user_b_1, 'enable_action', wf_id='preference_workflow')
    self.assertEquals(user_b_1.getPreferenceState(), 'enabled')

    # check user_a's preference is still enabled
    self.assertEquals(user_a_1.getPreferenceState(), 'enabled')
    self.assertEquals(user_a_2.getPreferenceState(), 'disabled')

    # Checks that a manager preference doesn't disable any other user
    # preferences
    # log as manager
    newSecurityManager(None, uf.getUserById('manager').__of__(uf))

    self.assert_('Manager' in
      getSecurityManager().getUser().getRolesInContext(portal_preferences))

    # create a pref for manager
    manager_pref = portal_preferences.newContent(
        id='manager_pref', portal_type='Preference')
    manager_pref.setPreferredAccountingTransactionAtDate(
                                DateTime(2012, 12, 12))
    transaction.commit(); self.tic()
    # enable this preference
    portal_workflow.doActionFor(
       manager_pref, 'enable_action', wf_id='preference_workflow')
    self.assertEquals(manager_pref.getPreferenceState(), 'enabled')

    # check users preferences are still enabled
    self.assertEquals(user_a_1.getPreferenceState(), 'enabled')
    self.assertEquals(user_b_1.getPreferenceState(), 'enabled')
    self.assertEquals(user_a_2.getPreferenceState(), 'disabled')

  def test_GlobalPreference(self):
    # globally enabled preference are preference for anonymous users.
    ptool = self.getPreferenceTool()
    ptool.site.setPreferredAccountingTransactionSimulationStateList(
                          ['this_is_visible_by_anonymous'])
    self.getPortal().portal_workflow.doActionFor(
                  ptool.site, 'enable_action', wf_id='preference_workflow')
    self.assertEquals('global', ptool.site.getPreferenceState())
    transaction.commit()
    self.tic()
    noSecurityManager()
    self.assertEquals(['this_is_visible_by_anonymous'],
        ptool.getPreferredAccountingTransactionSimulationStateList())

  def test_GetDefault(self):
    portal_workflow = self.getWorkflowTool()
    pref_tool = self.getPreferenceTool()
    site = self.getPreferenceTool()['site']
    portal_workflow.doActionFor(
       site, 'enable_action', wf_id='preference_workflow')
    self.assertEquals(site.getPreferenceState(),    'global')

    method = pref_tool.getPreferredAccountingTransactionSimulationState
    state = method()
    self.assertEquals(state, None)
    state = method('default')
    self.assertEquals(state, 'default')

    method = lambda *args: pref_tool.getPreference('preferred_accounting_transaction_simulation_state', *args)
    state = method()
    self.assertEquals(state, None)
    state = method('default')
    self.assertEquals(state, 'default')

    method = pref_tool.getPreferredAccountingTransactionSimulationStateList
    state_list = method()
    self.assertEquals(state_list, None)
    state_list = method(('default',))
    self.assertEquals(state_list, ['default',]) # getPreferredAccountingTransactionSimulationStateList
                                                # always tries to cast tuples to lists

    method = lambda *args: pref_tool.getPreference('preferred_accounting_transaction_simulation_state_list', *args)
    state_list = method()
    self.assertEquals(state_list, None)
    state_list = method(('default',))
    self.assertEquals(state_list, ('default',))

  def test_Permissions(self):
    # create a new site preference for later
    preference_tool = self.portal.portal_preferences
    site_pref = preference_tool.newContent(
                          portal_type='Preference',
                          priority=Priority.SITE)
    self.portal.portal_workflow.doActionFor(site_pref, 'enable_action')
    self.assertEquals(site_pref.getPreferenceState(), 'global')

    # Members can add new preferences
    uf = self.getPortal().acl_users
    uf._doAddUser('member', '', ['Member', ], [])
    member = uf.getUserById('member').__of__(uf)
    newSecurityManager(None, member)
    user_pref = preference_tool.newContent(portal_type='Preference')

    # Members can copy & paste existing preferences
    user_pref.Base_createCloneDocument()
    # note that copy & pasting a site preference reset the priority to USER
    # preference.
    cp_data = preference_tool.manage_copyObjects(ids=[site_pref.getId()])
    copy_id = preference_tool.manage_pasteObjects(cp_data)[0]['new_id']
    self.assertEquals(Priority.USER, preference_tool[copy_id].getPriority())

    # Globally enabled preferences can be viewed by Members
    self.assertTrue(member.has_permission('View', site_pref))

    # Member does not have Manage properties on their own preferences, 
    # otherwise the "Metadata" tab is shown
    self.assertFalse(member.has_permission(
                         'Manage properties', user_pref))


  def test_SystemPreference(self):
    preference_tool = self.portal.portal_preferences
    site_pref = preference_tool.newContent(
                          portal_type='System Preference',
                          preferred_accounting_transaction_simulation_state_list="this_is_default",
                          priority=Priority.SITE)
    # check not taken into account if not enabled
    self.assertEquals(None,
                      preference_tool.getPreferredAccountingTransactionSimulationStateList())
    # enable it and check preference is returned
    self.portal.portal_workflow.doActionFor(site_pref, 'enable_action')
    self.assertEquals(site_pref.getPreferenceState(), 'global')
    transaction.commit()
    self.tic()
    self.assertEquals(['this_is_default'],
                      preference_tool.getPreferredAccountingTransactionSimulationStateList())

    # Members can't add new system preferences
    uf = self.getPortal().acl_users
    uf._doAddUser('member', '', ['Member', ], [])
    member = uf.getUserById('member').__of__(uf)
    newSecurityManager(None, member)
    self.assertRaises(Unauthorized, preference_tool.newContent, portal_type='System Preference')
    # But they can see others
    site_pref.view()
    # check accessors works
    site_pref.setPreferredAccountingTransactionSimulationStateList(
      ['this_is_system'])
    transaction.commit()
    self.tic()
    self.assertEquals(['this_is_system'],
                      preference_tool.getPreferredAccountingTransactionSimulationStateList())

    # create a user pref and check it doesn't outranks the system one if
    # they both defined same pref
    user_pref = preference_tool.newContent(
                          portal_type='Preference',
                          priority=Priority.USER)
    user_pref.setPreferredAccountingTransactionSimulationStateList(
      ['this_is_user'])
    self.portal.portal_workflow.doActionFor(user_pref, 'enable_action')
    self.assertEquals(user_pref.getPreferenceState(), 'enabled')
    transaction.commit()
    self.tic()
    self.assertEquals(['this_is_user'],
                      user_pref.getPreferredAccountingTransactionSimulationStateList())
    self.assertEquals(['this_is_system'],
                      preference_tool.getPreferredAccountingTransactionSimulationStateList())

    # check a user can't edit preference which are marked for manager (only for zope2.8)
    try:
      from ZODB.Transaction import Transaction
    except ImportError:
      self.assertRaises(Unauthorized, user_pref.edit, preferred_ooodoc_server_address="localhost")

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestPreferences))
  return suite
