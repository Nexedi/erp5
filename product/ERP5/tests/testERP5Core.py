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

from AccessControl.SecurityManagement import newSecurityManager
from Testing import ZopeTestCase
from Products.PageTemplates.GlobalTranslationService import \
                                      setGlobalTranslationService

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase

HTTP_OK = 200
HTTP_UNAUTHORIZED = 401
HTTP_REDIRECT = 302

class DummyTranslationService:
  """A dummy translation service where you can access translated msgids and
  mappings in _translated.
  """
  _translated = {}
  def translate(self, domain, msgid, mapping=None, *args, **kw):
    self._translated.setdefault(domain, []).append((msgid, mapping))
    return msgid

class TestERP5Core(ERP5TypeTestCase, ZopeTestCase.Functional):
  """Test for erp5_core business template.
  """
  run_all_test = 1
  quiet = 1
  manager_username = 'rc'
  manager_password = ''

  def getTitle(self):
    return "ERP5Core"

  def login(self, quiet=0, run=run_all_test):
    uf = self.getPortal().acl_users
    uf._doAddUser(self.manager_username, self.manager_password, ['Manager'], [])
    user = uf.getUserById(self.manager_username).__of__(uf)
    newSecurityManager(None, user)

  def afterSetUp(self):
    self.login()
    self.portal = self.getPortal()
    self.portal_id = self.portal.getId()
    self.auth = '%s:%s' % (self.manager_username, self.manager_password)

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
    self.failUnless(self.portal._getOb(module_id, None) is not None)
    self.assertNotEqual(
        self.portal.portal_skins._getOb(portal_skins_folder, None), None)
    self.assertEquals(module_title,
                      self.portal._getOb(module_id).getTitle())
    self.assertNotEqual(self.portal.portal_types.getTypeInfo(module_portal_type),
                        None)
    self.assertNotEqual(self.portal.portal_types.getTypeInfo(object_portal_type),
                        None)
    #self.assertEqual(self.portal.portal_types[object_portal_type].title,
    #                  object_title)
  
  def test_02_FavouritesMenu(self, quiet=quiet, run=run_all_test):
    """
      Test that Manage members is not an entry in the My Favourites menu.
    """
    if not run: return
    portal_actions = getattr(self.getPortal(), 'portal_actions', None)
    global_action_list = portal_actions.listFilteredActionsFor(
                               self.getPortal())['global']
    action_name_list = []
    for action in global_action_list:
      if(action['visible']):
        action_name_list.append(action['title'])

    self.assertTrue('Create Module' in action_name_list)

    for action_name in action_name_list:
      self.assertNotEqual(action_name, "Manage Members")
      self.assertNotEqual(action_name, "Manage members")

  def test_frontpage(self):
    """Test we can view the front page.
    """
    response = self.publish('%s/view' % self.portal_id, self.auth)
    self.assertEquals(HTTP_OK, response.getStatus())
    
  def test_login_form(self):
    """Test anonymous user are redirected to login_form
    """
    response = self.publish('%s/view' % self.portal_id)
    self.assertEquals(HTTP_REDIRECT, response.getStatus())
    self.assertEquals('%s/login_form' % self.portal.absolute_url(),
                      response.getHeader('Location'))

  def test_view_tools(self):
    """Test we can view tools."""
    for tool in ('portal_categories',
                 'portal_templates',
                 'portal_orders',
                 'portal_deliveries',
                 'portal_rules',
                 'portal_alarms',):
      response = self.publish('%s/%s/view' % (self.portal_id, tool), self.auth)
      self.assertEquals(HTTP_OK, response.getStatus(),
                        "%s: %s" % (tool, response.getStatus()))
 
  def test_allowed_content_types_translated(self):
    """Tests allowed content types from the action menu are translated"""
    translation_service = DummyTranslationService()
    setGlobalTranslationService(translation_service)
    # assumes that we can add Business Template in template tool
    response = self.publish('%s/portal_templates/view' %
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
    self.getTypesTool().getTypeInfo('Template Tool').addAction(
                      id='dummy_jump_action',
                      name='Dummy Jump Action',
                      action='',
                      condition='',
                      permission='View',
                      category='object_jump',
                      visible=1)
    response = self.publish('%s/portal_templates/view' %
                            self.portal_id, self.auth)
    self.assertEquals(HTTP_OK, response.getStatus())
    self.failUnless(('Dummy Jump Action', {}) in
                      translation_service._translated['ui'])

  def test_error_log(self):
    self.failUnless('error_log' in self.portal.objectIds())
  
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

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestERP5Core))
  return suite

