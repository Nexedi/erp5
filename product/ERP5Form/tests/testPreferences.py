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
import mock

from AccessControl.SecurityManagement import noSecurityManager
from AccessControl.SecurityManagement import getSecurityManager
from zExceptions import Unauthorized
from AccessControl.ZopeGuards import guarded_hasattr
from DateTime import DateTime

from Products.ERP5Type.tests.testERP5Type import PropertySheetTestCase
from Products.ERP5Type.tests.utils import createZODBPythonScript
from Products.ERP5Form.PreferenceTool import Priority

# should match what's configured by default in HtmlStylePreference
default_large_image_height = 768


class TestPreferences(PropertySheetTestCase):

  def getTitle(self):
    return "Portal Preferences"

  def afterSetUp(self):
    uf = self.getPortal().acl_users
    uf._doAddUser('manager', '', ['Manager', 'Assignor', ], [])
    self.loginByUserName('manager')
    self.createPreferences()

  def beforeTearDown(self):
    self.abort()
    portal_preferences = self.getPreferenceTool()
    portal_preferences.manage_delObjects(list(portal_preferences.objectIds()))
    super(TestPreferences, self).beforeTearDown()

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

    self.tic()

    # check preference levels are Ok
    self.assertEqual(person1.getPriority(), Priority.USER)
    self.assertEqual(person2.getPriority(), Priority.USER)
    self.assertEqual(group.getPriority(),   Priority.GROUP)
    self.assertEqual(site.getPriority(),    Priority.SITE)
    # check initial states
    self.assertEqual(person1.getPreferenceState(), 'disabled')
    self.assertEqual(person2.getPreferenceState(), 'disabled')
    self.assertEqual(group.getPreferenceState(),   'disabled')
    self.assertEqual(site.getPreferenceState(),    'disabled')

  def test_PreferenceToolTitle(self):
    """Tests that the title of the preference tool is correct.
    """
    self.assertEqual('Preferences', self.getPreferenceTool().Title())

  def test_AllowedContentTypes(self):
    """Tests Preference can be added in Preference Tool.
    """
    self.assertTrue('Preference' in [x.getId() for x in
           self.getPortal().portal_preferences.allowedContentTypes()])
    self.assertTrue('System Preference' in [x.getId() for x in
           self.getPortal().portal_preferences.allowedContentTypes()])

  def test_EnablePreferences(self):
    """ tests preference workflow """
    portal_workflow = self.getWorkflowTool()
    person1 = self.getPreferenceTool()['person1']
    person2 = self.getPreferenceTool()['person2']
    group = self.getPreferenceTool()['group']
    site = self.getPreferenceTool()['site']

    self.assertEqual(None, self.getPreferenceTool().getActivePreference())
    self.assertEqual(None, self.getPreferenceTool().getActiveUserPreference())
    self.assertEqual(None,
        self.getPreferenceTool().getActiveSystemPreference())

    person1.portal_workflow.doActionFor(
       person1, 'enable_action', wf_id='preference_workflow')
    self.commit()
    self.assertEqual(person1.getPreferenceState(), 'enabled')

    self.assertEqual( person1, self.getPreferenceTool().getActivePreference())
    self.assertEqual( person1, self.getPreferenceTool().getActiveUserPreference())
    self.assertEqual(None,
        self.getPreferenceTool().getActiveSystemPreference())

    portal_workflow.doActionFor(
       site, 'enable_action', wf_id='preference_workflow')
    self.assertEqual(person1.getPreferenceState(), 'enabled')
    self.assertEqual(site.getPreferenceState(),    'global')

    self.assertEqual(person1, self.getPreferenceTool().getActivePreference())
    self.assertEqual(person1, self.getPreferenceTool().getActiveUserPreference())
    self.assertEqual(None,
        self.getPreferenceTool().getActiveSystemPreference())

    portal_workflow.doActionFor(
       group, 'enable_action', wf_id='preference_workflow')
    self.assertEqual(person1.getPreferenceState(), 'enabled')
    self.assertEqual(group.getPreferenceState(),   'enabled')
    self.assertEqual(site.getPreferenceState(),    'global')

    self.assertEqual(person1, self.getPreferenceTool().getActivePreference())
    self.assertEqual(person1, self.getPreferenceTool().getActiveUserPreference())
    self.assertEqual(None,
        self.getPreferenceTool().getActiveSystemPreference())

    portal_workflow.doActionFor(
       person2, 'enable_action', wf_id='preference_workflow')
    self.commit()
    self.assertEqual(person2, self.getPreferenceTool().getActivePreference())
    self.assertEqual(person2, self.getPreferenceTool().getActiveUserPreference())
    self.assertEqual(None,
        self.getPreferenceTool().getActiveSystemPreference())
    self.assertEqual(person2.getPreferenceState(), 'enabled')
    self.tic()
    # enabling a preference disable all other of the same level
    self.assertEqual(person1.getPreferenceState(), 'disabled')
    self.assertEqual(group.getPreferenceState(),   'enabled')
    self.assertEqual(site.getPreferenceState(),    'global')

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
    self.assertEqual(person1.getPreferenceState(), 'enabled')
    self.assertEqual(group.getPreferenceState(),   'enabled')
    self.assertEqual(site.getPreferenceState(),    'global')
    person1.setPreferredAccountingTransactionSimulationState([])
    self.assertEqual(
      person1.getPreferredAccountingTransactionSimulationState(), None)
    group.setPreferredAccountingTransactionSimulationState([])
    self.assertEqual(
      group.getPreferredAccountingTransactionSimulationState(), None)
    site.setPreferredAccountingTransactionSimulationState([])
    self.assertEqual(
      site.getPreferredAccountingTransactionSimulationState(), None)

    self.assertEqual(len(pref_tool.getPreference(
      'preferred_accounting_transaction_simulation_state_list')), 0)

    site.edit(
      preferred_accounting_transaction_simulation_state_list=
      ['stopped', 'delivered'])
    self.assertEqual(list(pref_tool.getPreference(
      'preferred_accounting_transaction_simulation_state_list')),
      list(site.getPreferredAccountingTransactionSimulationStateList()))

    # getPreference on the tool has the same behaviour as getProperty
    # on the preference (unless property is unset on this pref)
    for prop in ['preferred_accounting_transaction_simulation_state',
            'preferred_accounting_transaction_simulation_state_list']:

      self.assertEqual(pref_tool.getPreference(prop),
                        site.getProperty(prop))

    group.edit(
      preferred_accounting_transaction_simulation_state_list=['draft'])
    self.assertEqual(list(pref_tool.getPreference(
      'preferred_accounting_transaction_simulation_state_list')),
      list(group.getPreferredAccountingTransactionSimulationStateList()))

    person1.edit(preferred_accounting_transaction_simulation_state_list=
              ['cancelled'])
    self.assertEqual(list(pref_tool.getPreference(
      'preferred_accounting_transaction_simulation_state_list')),
      list(person1.getPreferredAccountingTransactionSimulationStateList()))
    # edits can also be made with setters
    person1.setPreferredAccountingTransactionSimulationStateList(['planned'])
    self.assertEqual(list(pref_tool.getPreference(
      'preferred_accounting_transaction_simulation_state_list')),
      list(person1.getPreferredAccountingTransactionSimulationStateList()))

    # disable person -> group is selected
    self.getWorkflowTool().doActionFor(person1,
            'disable_action', wf_id='preference_workflow')
    self.commit()
    self.assertEqual(list(pref_tool.getPreference(
      'preferred_accounting_transaction_simulation_state_list')),
      list(group.getPreferredAccountingTransactionSimulationStateList()))

    self.assertEqual(None, pref_tool.getPreference('this_does_not_exists'))
    self.assertEqual('default', pref_tool.getPreference(
                                        'this_does_not_exists', 'default'))


  def test_GetAttr(self):
    """ checks that preference methods can be called directly
      on portal_preferences """
    portal_workflow = self.getWorkflowTool()
    pref_tool = self.getPreferenceTool()
    person1 = self.getPreferenceTool()['person1']
    group = self.getPreferenceTool()['group']
    site = self.getPreferenceTool()['site']
    self.assertEqual(person1.getPreferenceState(), 'disabled')
    portal_workflow.doActionFor(
       group, 'enable_action', wf_id='preference_workflow')
    self.assertEqual(group.getPreferenceState(),    'enabled')
    portal_workflow.doActionFor(
       site, 'enable_action', wf_id='preference_workflow')
    self.assertEqual(site.getPreferenceState(),     'global')
    group.setPreferredAccountingTransactionSimulationStateList(['cancelled'])

    self.assertNotEquals( None,
      pref_tool.getPreferredAccountingTransactionSimulationStateList())
    self.assertNotEquals( [],
      list(pref_tool.getPreferredAccountingTransactionSimulationStateList()))
    self.assertEqual(
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
    self.assertEqual(person1.getPreferenceState(),    'enabled')
    person1.setPreferredAccountingTransactionAtDate(DateTime(2005, 01, 01))
    pref_tool.setPreference(
      'preferred_accounting_transaction_at_date', DateTime(2004, 12, 31))
    self.tic()
    self.assertEqual(
      pref_tool.getPreferredAccountingTransactionAtDate(),
      DateTime(2004, 12, 31))
    self.assertEqual(
      person1.getPreferredAccountingTransactionAtDate(),
      DateTime(2004, 12, 31))

  def test_UserIndependance(self):
    """ check that the preferences are related to the user. """
    portal_workflow = self.getWorkflowTool()
    portal_preferences = self.getPreferenceTool()
    # create 2 users: user_a and user_b
    uf = self.getPortal().acl_users
    uf._doAddUser('user_a', '', ['Member', ], [])
    uf._doAddUser('user_b', '', ['Member', ], [])

    self.loginByUserName('user_a')

    # create 2 prefs as user_a
    user_a_1 = portal_preferences.newContent(
        id='user_a_1', portal_type='Preference')
    user_a_2 = portal_preferences.newContent(
        id='user_a_2', portal_type='Preference')
    self.tic()

    # enable a pref
    portal_workflow.doActionFor(
       user_a_1, 'enable_action', wf_id='preference_workflow')
    self.assertEqual(user_a_1.getPreferenceState(), 'enabled')
    self.assertEqual(user_a_2.getPreferenceState(), 'disabled')

    self.loginByUserName('user_b')

    # create a pref for user_b
    user_b_1 = portal_preferences.newContent(
        id='user_b_1', portal_type='Preference')
    user_b_1.setPreferredAccountingTransactionAtDate(DateTime(2002, 02, 02))
    self.tic()

    # enable this preference
    portal_workflow.doActionFor(
       user_b_1, 'enable_action', wf_id='preference_workflow')
    self.assertEqual(user_b_1.getPreferenceState(), 'enabled')

    # check user_a's preference is still enabled
    self.assertEqual(user_a_1.getPreferenceState(), 'enabled')
    self.assertEqual(user_a_2.getPreferenceState(), 'disabled')

    # Checks that a manager preference doesn't disable any other user
    # preferences
    self.loginByUserName('manager')

    self.assert_('Manager' in
      getSecurityManager().getUser().getRolesInContext(portal_preferences))

    # create a pref for manager
    manager_pref = portal_preferences.newContent(
        id='manager_pref', portal_type='Preference')
    manager_pref.setPreferredAccountingTransactionAtDate(
                                DateTime(2012, 12, 12))
    self.tic()
    # enable this preference
    portal_workflow.doActionFor(
       manager_pref, 'enable_action', wf_id='preference_workflow')
    self.assertEqual(manager_pref.getPreferenceState(), 'enabled')
    self.tic()

    # check users preferences are still enabled
    self.assertEqual(user_a_1.getPreferenceState(), 'enabled')
    self.assertEqual(user_b_1.getPreferenceState(), 'enabled')
    self.assertEqual(user_a_2.getPreferenceState(), 'disabled')

    # A user with Manager and Owner can view all preferences, because this user
    # is Manager and Owner, but for Manager, we have an exception, only
    # preferences actually owned by the user are taken into account.
    uf._doAddUser('manager_and_owner', '', ['Manager', 'Owner'], [])
    self.loginByUserName('manager_and_owner')
    self.assert_('Owner' in
      getSecurityManager().getUser().getRolesInContext(manager_pref))
    self.assertEqual(None,
        portal_preferences.getPreferredAccountingTransactionAtDate())

  def test_proxy_roles(self):
    # make sure we can get preferences in a script with proxy roles
    portal_workflow = self.getWorkflowTool()
    portal_preferences = self.getPreferenceTool()
    # create 2 users: user_a and user_b
    uf = self.portal.acl_users
    uf._doAddUser('user_a', '', ['Member', ], [])
    uf._doAddUser('user_b', '', ['Member', ], [])

    self.loginByUserName('user_a')

    user_a = portal_preferences.newContent(
        id='user_a', portal_type='Preference',
        # this preference have group priority, so preference for user_b would get
        # picked first
        priority=Priority.GROUP,
        preferred_accounting_transaction_simulation_state_list=['user_a'])
    self.tic()

    # enable a pref
    portal_workflow.doActionFor(
       user_a, 'enable_action', wf_id='preference_workflow')

    self.loginByUserName('user_b')
    # create a pref for user_b
    user_b = portal_preferences.newContent(
        id='user_b', portal_type='Preference',
        preferred_accounting_transaction_simulation_state_list=['user_b'])
    self.tic()

    # enable this preference
    portal_workflow.doActionFor(
       user_b, 'enable_action', wf_id='preference_workflow')

    self.login()
    script = createZODBPythonScript(
     self.portal.portal_skins.custom,
     'PreferenceTool_testPreferencesProxyRole', '',
     'return context.getPreferredAccountingTransactionSimulationStateList()')
    script.manage_proxy(['Manager'])

    self.loginByUserName('user_a')
    self.assertEqual(['user_a'],
        portal_preferences.PreferenceTool_testPreferencesProxyRole())

  def test_GlobalPreference(self):
    # globally enabled preference are preference for anonymous users.
    ptool = self.getPreferenceTool()
    ptool.site.setPreferredAccountingTransactionSimulationStateList(
                          ['this_is_visible_by_anonymous'])
    self.getPortal().portal_workflow.doActionFor(
                  ptool.site, 'enable_action', wf_id='preference_workflow')
    self.assertEqual('global', ptool.site.getPreferenceState())
    self.tic()
    noSecurityManager()
    self.assertEqual(['this_is_visible_by_anonymous'],
        ptool.getPreferredAccountingTransactionSimulationStateList())

  def test_GetDefault(self):
    portal_workflow = self.getWorkflowTool()
    pref_tool = self.getPreferenceTool()
    site = self.getPreferenceTool()['site']
    portal_workflow.doActionFor(
       site, 'enable_action', wf_id='preference_workflow')
    self.assertEqual(site.getPreferenceState(),    'global')

    method = pref_tool.getPreferredAccountingTransactionSimulationState
    state = method()
    self.assertEqual(state, [])
    state = method('default')
    self.assertEqual(state, 'default')

    method = lambda *args: pref_tool.getPreference('preferred_accounting_transaction_simulation_state', *args)
    state = method()
    self.assertEqual(state, [])
    state = method('default')
    self.assertEqual(state, 'default')

    method = pref_tool.getPreferredAccountingTransactionSimulationStateList
    state_list = method()
    self.assertEqual(state_list, [])
    state_list = method(('default',))
    # Initially, tuples were always casted to lists. This is not the case
    # anymore when preference_tool.getXxxList returns the default value.
    self.assertEqual(state_list, ('default',))

    method = lambda *args: pref_tool.getPreference('preferred_accounting_transaction_simulation_state_list', *args)
    state_list = method()
    self.assertEqual(state_list, [])
    state_list = method(('default',))
    self.assertEqual(state_list, ('default',))

  def test_Permissions(self):
    # create a new site preference for later
    preference_tool = self.portal.portal_preferences
    site_pref = preference_tool.newContent(
                          portal_type='Preference',
                          priority=Priority.SITE)
    self.portal.portal_workflow.doActionFor(site_pref, 'enable_action')
    self.assertEqual(site_pref.getPreferenceState(), 'global')

    # Members can add new preferences
    uf = self.getPortal().acl_users
    uf._doAddUser('member', '', ['Member', ], [])
    member = uf.getUserById('member').__of__(uf)
    self.loginByUserName('member')
    user_pref = preference_tool.newContent(portal_type='Preference')

    # Members can copy & paste existing preferences
    user_pref.Base_createCloneDocument()
    # note that copy & pasting a site preference reset the priority to USER
    # preference.
    cp_data = preference_tool.manage_copyObjects(ids=[site_pref.getId()])
    copy_id = preference_tool.manage_pasteObjects(cp_data)[0]['new_id']
    self.assertEqual(Priority.USER, preference_tool[copy_id].getPriority())

    # Globally enabled preferences can be viewed by Members
    self.assertTrue(member.has_permission('View', site_pref))

    # Member does not have Manage properties on their own preferences,
    # otherwise the "Metadata" tab is shown
    self.assertFalse(member.has_permission(
                         'Manage properties', user_pref))


  def test_SystemPreference(self):
    # We want to test a property with a default value defined
    self.assertTrue(default_large_image_height > 0)
    large_image_height = default_large_image_height + 1

    preference_tool = self.portal.portal_preferences
    system_pref = preference_tool.newContent(
                          portal_type='System Preference',
                          preferred_document_conversion_server_url_list=['http://127.0.0.1'],
                          priority=Priority.SITE)
    # check not taken into account if not enabled
    self.assertEqual([],
                     preference_tool.getPreferredDocumentConversionServerUrlList())
    self.assertEqual(['http://localhost'],
                     preference_tool.getPreferredDocumentConversionServerUrlList(['http://localhost']))
    self.assertEqual(default_large_image_height,
                     preference_tool.getPreferredLargeImageHeight())
    # enable it and check preference is returned
    self.portal.portal_workflow.doActionFor(system_pref, 'enable_action')
    self.assertEqual(system_pref.getPreferenceState(), 'global')
    self.tic()
    self.assertEqual(['http://127.0.0.1'],
                     preference_tool.getPreferredDocumentConversionServerUrlList())
    self.assertEqual(['http://127.0.0.1'],
                     preference_tool.getPreferredDocumentConversionServerUrlList(['http://localhost']))
    self.assertEqual(default_large_image_height,
                     preference_tool.getPreferredLargeImageHeight())
    # Default value passed by parameter has priority over the default in the
    # property sheet.
    self.assertEqual(large_image_height,
                     preference_tool.getPreferredLargeImageHeight(large_image_height))

    # Members can't add new system preferences
    uf = self.getPortal().acl_users
    uf._doAddUser('member', '', ['Member', ], [])
    self.loginByUserName('member')
    self.assertRaises(Unauthorized, preference_tool.newContent, portal_type='System Preference')
    # But they can see others
    system_pref.view()
    # check accessors works
    self.assertEqual(['http://127.0.0.1'],
                     preference_tool.getPreferredDocumentConversionServerUrlList())
    system_pref.setPreferredDocumentConversionServerUrlList(['http://1.2.3.4'])
    self.tic()
    self.assertEqual(['http://1.2.3.4'],
                     preference_tool.getPreferredDocumentConversionServerUrlList())
    self.assertEqual(['http://1.2.3.4'],
                     preference_tool.getPreferredDocumentConversionServerUrlList(['http://localhost']))
    self.assertEqual(default_large_image_height,
                     preference_tool.getPreferredLargeImageHeight())

    # create a user pref and check it doesn't outranks the system one if
    # they both defined same pref
    user_pref = preference_tool.newContent(
                          portal_type='Preference',
                          priority=Priority.USER)
    user_pref.setPreferredLargeImageHeight(large_image_height)
    self.portal.portal_workflow.doActionFor(user_pref, 'enable_action')
    self.assertEqual(user_pref.getPreferenceState(), 'enabled')
    self.tic()
    self.assertEqual(['http://1.2.3.4'],
                     preference_tool.getPreferredDocumentConversionServerUrlList(['http://localhost']))
    self.assertEqual(large_image_height,
                     preference_tool.getPreferredLargeImageHeight())
    self.assertEqual(large_image_height,
                     preference_tool.getPreferredLargeImageHeight(0))

    # check a user can't edit preference which are marked for manager
    self.assertRaises(Unauthorized, user_pref.edit, preferred_document_conversion_server_url_list=["http://localhost"])
    # even if there is System Preference enabled getActivePreference shall return
    # user preference
    self.assertEqual(user_pref, preference_tool.getActivePreference())
    self.assertEqual(user_pref, preference_tool.getActiveUserPreference())
    self.assertEqual(system_pref, preference_tool.getActiveSystemPreference())

  def test_boolean_accessor(self):
    self._addProperty('Preference',
        'test_boolean_accessor Preference',
        portal_type='Standard Property',
        property_id='dummy',
        preference=True,
        elementary_type='boolean')
    portal_preferences = self.portal.portal_preferences
    self.assertFalse(portal_preferences.getDummy())
    self.assertFalse(portal_preferences.isDummy())

    preference = portal_preferences.newContent(portal_type='Preference',
                                               dummy=True)
    preference.enable()
    self.tic()

    self.assertTrue(portal_preferences.getDummy())
    self.assertTrue(portal_preferences.isDummy())

  def test_multivalued_accessor(self):
    self._addProperty('Preference',
        'test_multivaluated_accessor Preference',
        portal_type='Standard Property',
        property_id='dummy_multi',
        preference=True,
        elementary_type='string',
        multivalued=True)
    portal_preferences = self.portal.portal_preferences
    self.assertEqual(None, portal_preferences.getDummyMulti())

    preference = portal_preferences.newContent(portal_type='Preference')
    preference.setDummyMultiList(['one', 'two'])
    preference.enable()
    self.tic()

    self.assertEqual('one', portal_preferences.getDummyMulti())
    self.assertEqual(['one', 'two'], portal_preferences.getDummyMultiList())

  def test_property_sheet_security_on_permission(self):
    """ Added a test to make sure permissions are used into portal
        preference level. """
    write_permission = 'Modify portal content'
    read_permission = 'Manage portal'

    self._addProperty('Preference',
        'test_property_sheet_security_on_permission Preference',
        property_id='preferred_toto',
        portal_type='Standard Property',
        preference=1,
        write_permission='Modify portal content',
        read_permission='Manage portal',
        elementary_type='string')

    obj = self.portal.portal_preferences.newContent(portal_type='Preference')
    obj.enable()
    self.tic()

    self.assertTrue(guarded_hasattr(obj, 'setPreferredToto'))
    obj.setPreferredToto("A TEST")
    self.assertTrue(guarded_hasattr(obj, 'getPreferredToto'))

    obj.manage_permission(write_permission, [], 0)
    self.assertFalse(guarded_hasattr(obj, 'setPreferredToto'))
    self.assertTrue(guarded_hasattr(obj, 'getPreferredToto'))

    obj.manage_permission(write_permission, ['Manager'], 1)
    obj.manage_permission(read_permission, [], 0)
    self.assertTrue(guarded_hasattr(obj, 'setPreferredToto'))
    self.assertFalse(guarded_hasattr(obj, 'getPreferredToto'))

    obj.manage_permission(read_permission, ['Manager'], 1)

    self.tic()

    preference_tool = self.portal.portal_preferences
    self.assertTrue(guarded_hasattr(preference_tool, 'getPreferredToto'))
    self.assertEqual("A TEST", preference_tool.getPreferredToto())

    preference_tool.manage_permission(write_permission, [], 0)
    self.assertTrue(guarded_hasattr(preference_tool, 'getPreferredToto'))

    preference_tool.manage_permission(write_permission, ['Manager'], 1)
    preference_tool.manage_permission(read_permission, [], 0)
    obj.manage_permission(read_permission, [], 0)
    self.assertFalse(guarded_hasattr(preference_tool, 'getPreferredToto'))

    preference_tool.manage_permission(read_permission, ['Manager'], 1)

  def test_system_preference_value_prefererred(self):
    default_preference_string = 'Default Name'
    normal_preference_string = 'Normal Preference'
    system_preference_string = 'System Preference'
    self._addProperty('Preference',
        'test_system_preference_value_prefererred Preference',
        portal_type='Standard Property',
        property_id='dummystring',
        property_default='python: "%s"' % default_preference_string,
        preference=True,
        elementary_type='string')
    portal_preferences = self.portal.portal_preferences
    self.assertEqual(default_preference_string,
        portal_preferences.getDummystring())

    preference = portal_preferences.newContent(portal_type='Preference',
                                               dummystring=normal_preference_string,
                                               priority=Priority.SITE)
    preference.enable()
    self.tic()

    self.assertEqual(normal_preference_string,
        portal_preferences.getDummystring())

    system_preference = portal_preferences.newContent(portal_type='System Preference',
                                               dummystring=system_preference_string)
    system_preference.enable()
    self.tic()

    self.assertEqual(system_preference_string,
        portal_preferences.getDummystring())

  def test_system_preference_value_prefererred_clear_cache_disabled(self):
    default_preference_string = 'Default Name'
    normal_preference_string = 'Normal Preference'
    system_preference_string = 'System Preference'
    self._addProperty('Preference',
        'test_system_preference_value_prefererred_clear_cache_disabled Preference',
        portal_type='Standard Property',
        property_id='dummystring',
        property_default='python: "%s"' % default_preference_string,
        preference=True,
        elementary_type='string')
    portal_preferences = self.portal.portal_preferences
    self.assertEqual(default_preference_string,
        portal_preferences.getDummystring())

    preference = portal_preferences.newContent(portal_type='Preference',
                                               dummystring=normal_preference_string,
                                               priority=Priority.SITE)
    preference.enable()
    self.tic()

    self.assertEqual(normal_preference_string,
        portal_preferences.getDummystring())

    # simulate situation when _clearCache does nothing, for example in case
    # if memcached or any other non-deleteable cache is used
    with mock.patch.object(
        self.portal.portal_caches.__class__,
        'clearAllCache') as clearAllCache,\
      mock.patch.object(
        self.portal.portal_caches.__class__,
        'clearCacheFactory') as clearCacheFactory:

      system_preference = portal_preferences.newContent(
          portal_type='System Preference',
          dummystring=system_preference_string)
      system_preference.enable()
      self.tic()

    self.assertEqual(system_preference_string,
        portal_preferences.getDummystring())

    clearAllCache.assert_not_called()
    clearCacheFactory.assert_not_called()
