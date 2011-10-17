##############################################################################
#
# Copyright (c) 2004, 2005, 2006 Nexedi SARL and Contributors.
# All Rights Reserved.
#          Romain Courteaud <romain@nexedi.com>
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
from hashlib import md5
import pprint

import transaction
from AccessControl.SecurityManagement import newSecurityManager
from Testing import ZopeTestCase

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.tests.utils import DummyTranslationService

if 1: # BBB
  # Zope 2.12, simulate setting the globalTranslationService with
  # zope.i18n utilities
  import zope.interface
  import zope.component
  import Acquisition

  global_translation_service = None

  from zope.i18n.interfaces import ITranslationDomain, \
                                   IFallbackTranslationDomainFactory
  class DummyTranslationDomainFallback(object):
    zope.interface.implements(ITranslationDomain)
    zope.interface.classProvides(IFallbackTranslationDomainFactory)

    def __init__(self, domain):
      self.domain = domain

    def translate(self, msgid, mapping=None, *args, **kw):
      return global_translation_service.translate(self.domain, msgid, mapping,
                                                  *args, **kw)

  def setGlobalTranslationService(translation_service):
    global global_translation_service
    global_translation_service = translation_service
    zope.component.provideUtility(DummyTranslationDomainFallback,
                                  provides=IFallbackTranslationDomainFactory)
    # disable translation for the 'ui' domain so it can use the fallback above.
    # Save it on a portal attribute since we don't have access to the test
    # class
    sm = zope.component.getSiteManager()
    portal = Acquisition.aq_parent(sm)
    ui_domain = sm.getUtility(ITranslationDomain, name='ui')
    # store in a list to avoid acquisition wrapping
    portal._save_ui_domain = [ui_domain]
    sm.unregisterUtility(provided=ITranslationDomain, name='ui')

  def unregister_translation_domain_fallback():
    from zope.component.globalregistry import base
    base.unregisterUtility(DummyTranslationDomainFallback)
    sm = zope.component.getSiteManager()
    portal = Acquisition.aq_parent(sm)
    ui_domain = getattr(portal, '_save_ui_domain', [None]).pop()
    if ui_domain is not None:
      sm.registerUtility(ui_domain, ITranslationDomain, 'ui')
      del portal._save_ui_domain

HTTP_OK = 200
HTTP_UNAUTHORIZED = 401
HTTP_REDIRECT = 302

class TestERP5Core(ERP5TypeTestCase, ZopeTestCase.Functional):
  """Test for erp5_core business template.
  """
  run_all_test = 1
  quiet = 1

  manager_username = 'rc'
  manager_password = 'w'

  def getTitle(self):
    return "ERP5Core"

  def getBusinessTemplateList(self):
    """
    """
    return ('erp5_base', )

  def login(self, quiet=0, run=run_all_test):
    uf = self.getPortal().acl_users
    uf._doAddUser(self.manager_username, self.manager_password, ['Manager'], [])
    user = uf.getUserById(self.manager_username).__of__(uf)
    newSecurityManager(None, user)

  def afterSetUp(self):
    self.login()
    self.portal_id = self.portal.getId()
    self.auth = '%s:%s' % (self.manager_username, self.manager_password)

  def beforeTearDown(self):
    transaction.abort()
    unregister_translation_domain_fallback()
    if 'test_folder' in self.portal.objectIds():
      self.portal.manage_delObjects(['test_folder'])
    self.portal.portal_selections.setSelectionFor('test_selection', None)
    transaction.commit()
    self.tic()

  def test_01_ERP5Site_createModule(self, quiet=quiet, run=run_all_test):
    """
      Test that a module is created when ERP5Site_createModule is given the
      strict minimum number of arguments.
      A created module is composed of :
       - the module itself, directly in the portal object
       - a skin folder, directly in the skins tool
       - a portal type for the module
       - a portal type for the objects which can be contained in the module

      TODO: check more behaviours of the creation script, like skin priority, ...
    """
    if not run: return

    module_portal_type='UnitTest Module'
    portal_skins_folder='erp5_unittest'
    object_portal_type='UnitTest'
    object_title='UnitTest'
    module_id='unittest_module'
    module_title='UnitTests'


    skins_tool = self.portal.portal_skins
    types_tool = self.portal.portal_types
    self.failIf(self.portal._getOb(module_id, None) is not None)
    self.assertEqual(skins_tool._getOb(portal_skins_folder, None), None)
    self.assertEqual(types_tool._getOb(module_portal_type, None), None)
    self.assertEqual(types_tool._getOb(object_portal_type, None), None)

    self.portal.ERP5Site_createModule(module_portal_type=module_portal_type,
                                      portal_skins_folder=portal_skins_folder,
                                      object_portal_type=object_portal_type,
                                      object_title=object_title,
                                      module_id=module_id,
                                      module_title=module_title)
    self.failUnless(self.portal._getOb(module_id, None) is not None)
    self.assertEquals(module_title,
                      self.portal._getOb(module_id).getTitle())
    self.assertNotEqual(types_tool.getTypeInfo(module_portal_type), None)
    self.assertNotEqual(types_tool.getTypeInfo(object_portal_type), None)
    self.assertTrue(module_portal_type
                      in self.portal.getPortalModuleTypeList())

    skin_folder = skins_tool._getOb(portal_skins_folder, None)
    self.assertNotEqual(skin_folder, None)
    self.assert_('UnitTest_view' in skin_folder.objectIds())
    view_form = skin_folder.UnitTest_view
    self.assertEquals('form_view', view_form.pt)
    self.assertEquals('Base_edit', view_form.action)

    self.assert_('UnitTestModule_viewUnitTestList' in skin_folder.objectIds())
    list_form = skin_folder.UnitTestModule_viewUnitTestList
    self.assertEquals('form_list', list_form.pt)
    self.assertEquals('Base_doSelect', list_form.action)
    self.assert_('listbox' in [x.getId() for x in list_form.get_fields()])
    self.assert_('listbox' in
            [x.getId() for x in list_form.get_fields_in_group('bottom')])

    # make sure we can use our module
    self.portal.unittest_module.view()
    self.portal.unittest_module.newContent(id='document', portal_type=object_portal_type)
    self.portal.unittest_module.document.view()

    # make sure translation domains are set correctly
    self.assertEquals('erp5_ui',
        self.portal.unittest_module.getTitleTranslationDomain())
    self.assertEquals('erp5_ui',
        self.portal.unittest_module.getShortTitleTranslationDomain())

    type_information = self.portal.portal_types[module_portal_type]
    self.assertTrue('business_application'
                    in type_information.getTypeBaseCategoryList())

  def check_actions(self, target, expected):
    actions = self.portal.portal_actions.listFilteredActionsFor(target)
    got = {}
    for category, actions in actions.items():
      got[category] = [dict(title=action['title'], id=action['id'])
                       for action in actions
                       if action['visible']]
    msg = ("Actions do not match. Expected:\n%s\n\nGot:\n%s\n" %
           (pprint.pformat(expected), pprint.pformat(got)))
    self.assertEquals(expected, got, msg)

  def test_manager_actions_on_portal(self):
    # as manager:
    expected = {'folder': [],
                'global': [{'title': 'Manage Business Templates',
                            'id': 'bt_tool'},
                           {'title': 'Configure Categories',
                            'id': 'category_tool'},
                           {'title': 'Create Module',
                            'id': 'create_module'},
                           {'title': 'Configure Portal Types',
                            'id': 'types_tool'},
                           {'id': 'property_sheet_tool',
                            'title': 'Configure Property Sheets'},
                           {'id': 'portal_alarms_action', 
                            'title': 'Configure Alarms'},
                           {'title': 'Undo', 'id': 'undo'}],
                'object': [],
                'object_action': [{'id': 'post_query', 'title': 'Post a Query'}],
                'object_jump': [{'id': 'jump_query', 'title': 'Queries'}],
                'object_search': [{'title': 'Search', 'id': 'search'}],
                'object_sort': [{'title': 'Sort', 'id': 'sort_on'}],
                'object_ui': [{'title': 'Modify UI', 'id': 'list_ui'}],
                'object_view': [{'title': 'History', 'id': 'history'},
                                {'title': 'Metadata', 'id': 'metadata'}],
                'user': [{'title': 'Preferences', 'id': 'preferences'},
                         {'title': 'Log out', 'id': 'logout'}],
                'workflow': []}
    self.check_actions(self.portal, expected)

  def test_member_actions_on_portal(self):
    # as Member
    self.createUser('usual_member')
    self.logout()
    transaction.commit()
    self.tic()
    super(TestERP5Core, self).login('usual_member')
    expected = {'folder': [],
                'global': [],
                'object': [],
                'object_search': [{'title': 'Search', 'id': 'search'}],
                'object_sort': [{'title': 'Sort', 'id': 'sort_on'}],
                'object_ui': [{'title': 'Modify UI', 'id': 'list_ui'}],
                'object_view': [{'title': 'History', 'id': 'history'}],
                'user': [{'title': 'Preferences', 'id': 'preferences'},
                         {'title': 'Log out', 'id': 'logout'}],
                'workflow': []}
    self.check_actions(self.portal, expected)

  def test_anonymous_actions_on_portal(self):
    # as anonymous:
    self.logout()
    expected = {'folder': [],
                'global': [],
                'object': [],
                'object_search': [{'title': 'Search', 'id': 'search'}],
                'object_sort': [{'title': 'Sort', 'id': 'sort_on'}],
                'object_ui': [{'title': 'Modify UI', 'id': 'list_ui'}],
                'object_view': [{'title': 'History', 'id': 'history'}],
                'user': [{'id': 'login', 'title': 'Login'}],
                'workflow': []}
    self.check_actions(self.portal, expected)

  def test_frontpage(self):
    """Test we can view the front page.
    """
    response = self.publish(self.portal_id, self.auth)
    self.assertEquals(HTTP_OK, response.getStatus())

  def test_login_form(self):
    """Test anonymous user are redirected to login_form
    """
    response = self.publish(self.portal_id)
    self.assertEquals(HTTP_REDIRECT, response.getStatus())
    self.assertEquals('%s/login_form' % self.portal.absolute_url(),
                      response.getHeader('Location'))

  def test_view_tools(self):
    """Test we can view tools."""
    for tool in ('portal_categories',
                 'portal_templates',
                 'portal_rules',
                 'portal_alarms',):
      response = self.publish('%s/%s' % (self.portal_id, tool), self.auth)
      self.assertEquals(HTTP_OK, response.getStatus(),
                        "%s: %s (%s)" % (tool, response.getStatus(),
                                         str(response)))

  def test_allowed_content_types_translated(self):
    """Tests allowed content types from the action menu are translated"""
    translation_service = DummyTranslationService()
    setGlobalTranslationService(translation_service)
    # assumes that we can add Business Template in template tool
    response = self.publish('%s/portal_templates' %
                                self.portal_id, self.auth)
    self.assertEquals(HTTP_OK, response.getStatus())
    self.failUnless(('Business Template', {})
                    in translation_service._translated['ui'])
    self.failUnless(
      ('Add ${portal_type}', {'portal_type': 'Business Template'}) in
      translation_service._translated['ui'])

  def test_jump_action_translated(self):
    """Tests jump actions are translated"""
    translation_service = DummyTranslationService()
    setGlobalTranslationService(translation_service)
    # adds a new jump action to Template Tool portal type
    self.getTypesTool().getTypeInfo('Template Tool').newContent(
                      portal_type='Action Information',
                      reference='dummy_jump_action',
                      title='Dummy Jump Action',
                      action_permission='View',
                      action_type='object_jump')
    response = self.publish('%s/portal_templates' %
                            self.portal_id, self.auth)
    self.assertEquals(HTTP_OK, response.getStatus())
    self.failUnless(('Dummy Jump Action', {}) in
                      translation_service._translated['ui'])

  def test_error_log(self):
    self.failUnless('error_log' in self.portal.objectIds())
    self.failUnless(self.portal.error_log.getProperties()['copy_to_zlog'])
    self.failIf('Unauthorized' in
                self.portal.error_log.getProperties()['ignored_exceptions'])

  def test_03_getDefaultModule(self, quiet=quiet, run=run_all_test):
    """
    test getDefaultModule method
    """
    if not run:
      return
    portal_id = self.getPortal().getId()
    object_portal_type = ' '.join([part.capitalize() for part \
                                    in portal_id.split('_')])
    module_portal_type='%s Module' % object_portal_type
    portal_skins_folder='erp5_unittest'
    object_title=object_portal_type
    module_id="%s_module" % portal_id
    module_title='%ss' % object_portal_type

    # Create module for testing
    self.failIf(self.portal._getOb(module_id, None) is not None)
    self.assertEqual(self.portal.portal_skins._getOb(portal_skins_folder, None),
                     None)
    self.assertEqual(self.portal.portal_types.getTypeInfo(module_portal_type),
                     None)
    self.assertEqual(self.portal.portal_types.getTypeInfo(object_portal_type),
                     None)
    self.portal.ERP5Site_createModule(module_portal_type=module_portal_type,
                                      portal_skins_folder=portal_skins_folder,
                                      object_portal_type=object_portal_type,
                                      object_title=object_title,
                                      module_id=module_id,
                                      module_title=module_title)

    # Test
    self.assertEquals(
        module_id,
        self.portal.getDefaultModule(object_portal_type).getId())
    self.assertEquals(
        module_portal_type,
        self.portal.getDefaultModule(object_portal_type).getPortalType())
    self.assertEquals(
        module_id,
        self.portal.getDefaultModule(module_portal_type).getId())
    self.assertEquals(
        module_portal_type,
        self.portal.getDefaultModule(module_portal_type).getPortalType())

  def test_catalog_with_very_long_login_name(self, quiet=quiet, run=run_all_test):
    """Make sure that user with very long login name can find his document by catalog"""
    portal = self.getPortal()
    # Create user account with very long login name
    login_name = 'very_very_looooooooooooooooooooooooooooooooooooooooooooooooooooo' + \
    'oooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooong_login_name'
    password = 'very_long_passworddddddddddddddddddddddddddddddddddddddddddddddddd' + \
    'ddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd'
    acl_users = portal.acl_users
    acl_users._doAddUser(login_name, password, ['Member'], [])
    user = acl_users.getUserById(login_name).__of__(acl_users)
    # Login as the above user
    newSecurityManager(None, user)
    self.auth = '%s:%s' % (login_name, password)
    transaction.commit()

    # Create preference
    portal.portal_preferences.newContent('Preference', title='My Test Preference')

    transaction.commit()
    self.tic()

    self.assertEqual(
      len(portal.portal_catalog(portal_type='Preference',
                                title='My Test Preference')),
      1)
    response = self.publish(self.portal_id, self.auth)
    self.assertEquals(HTTP_OK, response.getStatus())

  def test_Folder_delete(self):
    module = self.portal.newContent(portal_type='Folder', id='test_folder')
    document_1 = module.newContent(portal_type='Folder', id='1')
    document_2 = module.newContent(portal_type='Folder', id='2')
    uid_list = [document_1.getUid(), document_2.getUid()]
    self.portal.portal_selections.setSelectionParamsFor(
          'test_selection', dict(uids=uid_list))
    transaction.commit()
    self.tic()
    md5_string = md5(str(sorted(map(str, uid_list)))).hexdigest()
    redirect = module.Folder_delete(selection_name='test_selection',
                                    uids=uid_list,
                                    md5_object_uid_list=md5_string)
    self.assert_('Deleted.' in redirect, redirect)
    transaction.savepoint(optimistic=True)
    self.assertEquals(len(module.objectValues()), 0)

  def test_Folder_delete_related_object(self):
    # deletion is refused if there are related objects
    organisation_module_len = len(self.portal.organisation_module)
    person_module_len = len(self.portal.person_module)
    organisation = self.portal.organisation_module.newContent()
    person = self.portal.person_module.newContent(
      default_career_subordination_value=organisation)
    for obj in person, organisation:
      obj.manage_addLocalRoles(self.manager_username, ['Assignor'])
    transaction.commit()
    self.assertEqual(0, organisation.getRelationCountForDeletion())
    self.tic()
    self.assertEqual(2, organisation.getRelationCountForDeletion())
    self.assertEqual(0, person.getRelationCountForDeletion())
    def delete(assert_deleted, obj):
      uid_list = [obj.getUid()]
      self.portal.portal_selections.setSelectionParamsFor(
                          'test_selection', dict(uids=uid_list))
      md5_string = md5(str(sorted(map(str, uid_list)))).hexdigest()
      redirect = obj.getParentValue().Folder_delete(uids=uid_list,
        selection_name='test_selection', md5_object_uid_list=md5_string)
      self.assertTrue(('Sorry, 1 item is in use.', 'Deleted.')[assert_deleted]
                      in redirect, redirect)
      transaction.commit()
      self.tic()
    delete(0, organisation)
    delete(1, person)
    self.assertEqual(0, organisation.getRelationCountForDeletion())
    delete(1, organisation)
    self.assertEquals(organisation_module_len + 1,
                      len(self.portal.organisation_module))
    self.assertEquals(person_module_len + 1,
                      len(self.portal.person_module))

  def test_Folder_delete_non_accessible_object(self):
    # deletion is refused if there are related objects, even if those related
    # objects cannot be accessed
    module = self.portal.newContent(portal_type='Folder', id='test_folder')
    document_1 = module.newContent(portal_type='Folder', id='1')
    document_2 = module.newContent(portal_type='Folder', id='2')
    self.portal.portal_categories.setCategoryMembership(
                                context=document_1,
                                base_category_list=('source',),
                                category_list=document_2.getRelativeUrl())
    uid_list = [document_2.getUid(), ]
    self.portal.portal_selections.setSelectionParamsFor(
                          'test_selection', dict(uids=uid_list))
    transaction.commit()
    self.tic()
    self.assertEquals([document_1],
        self.portal.portal_categories.getRelatedValueList(document_2))
    md5_string = md5(str(sorted(map(str, uid_list)))).hexdigest()

    document_1.manage_permission('View', [], acquire=0)
    document_1.manage_permission('Access contents information', [], acquire=0)
    redirect = module.Folder_delete(selection_name='test_selection',
                                    uids=uid_list,
                                    md5_object_uid_list=md5_string)
    self.assert_('Sorry, 1 item is in use.' in redirect, redirect)
    transaction.savepoint(optimistic=True)
    self.assertEquals(len(module.objectValues()), 2)

  def test_getPropertyForUid(self):
    error_list = []
    for i in self.portal.objectValues():
      if i.getUid() != 0 and i.getUid() != i.getProperty('uid'):
        error_list.append((i.getId(), i.getUid(), i.getProperty('uid')))
    self.assertEquals(error_list, [])

  def test_site_manager_and_translation_migration(self):
    from zope.site.hooks import getSite, setSite
    from zope.component import queryUtility
    from zope.i18n.interfaces import ITranslationDomain
    # check translation is working normaly
    erp5_ui_catalog = self.portal.Localizer.erp5_ui
    self.assertEqual(queryUtility(ITranslationDomain, 'erp5_ui'),
                     erp5_ui_catalog)
    self.assertEqual(queryUtility(ITranslationDomain, 'ui'), erp5_ui_catalog)
    # let's damage it intentionally to see how it is rebuild from scratch
    # in a migration from Zope 2.8
    sm = self.portal.getSiteManager()
    sm.unregisterUtility(provided=ITranslationDomain, name=u'ui')
    self.assertEqual(queryUtility(ITranslationDomain, 'erp5_ui'),
                     erp5_ui_catalog)
    self.assertEqual(queryUtility(ITranslationDomain, 'ui'), None)
    # now let's simulate a site just migrated from Zope 2.8 that's being
    # accessed for the first time:
    old_site = getSite()
    try:
      setSite()
      # Sites from Zope2.8 don't have a site_manager yet.
      del self.portal._components
      # check that we can't get any translation utility
      self.assertEqual(queryUtility(ITranslationDomain, 'erp5_ui'), None)
      # Now simulate first access. Default behaviour from
      # ObjectManager is to raise a ComponentLookupError here:
      setSite(self.portal)
      # This should have automatically reconstructed the i18n utility
      # registrations:
      self.assertEqual(queryUtility(ITranslationDomain, 'erp5_ui'),
                       erp5_ui_catalog)
      self.assertEqual(queryUtility(ITranslationDomain, 'ui'), erp5_ui_catalog)
    finally:
      # clean everything up, we don't want to mess the test environment
      transaction.abort()
      setSite(old_site)

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestERP5Core))
  return suite

