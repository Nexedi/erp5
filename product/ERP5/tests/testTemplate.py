# -*- coding: utf-8 -*-
#############################################################################
#
# Copyright (c) 2007-2009 Nexedi SA and Contributors. All Rights Reserved.
#                    TAHARA Yusei <yusei@nexedi.com>
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
"""Tests Template functionality"""

import unittest
import transaction
from AccessControl.SecurityManagement import newSecurityManager
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type import Permissions
from Products.ERP5Form.Document.Preference import Priority


class TestTemplate(ERP5TypeTestCase):
  """A test for Template.
  """

  def getTitle(self):
    return "Template"

  def getBusinessTemplateList(self):
    """Returns list of BT to be installed."""
    return ('erp5_base', 'erp5_ui_test')

  def login(self, name=None):
    """login with Member & Author roles."""
    if name is None:
      return
    uf = self.getPortal().acl_users
    uf._doAddUser(name, '', ['Member', 'Author'], [])
    user = uf.getUserById(name).__of__(uf)
    newSecurityManager(None, user)

  def afterSetUp(self):
    ERP5TypeTestCase.login(self, 'ERP5TypeTestCase')
    portal_preferences = self.portal.portal_preferences
    portal_preferences.deleteContent(list(portal_preferences.objectIds()))
    transaction.commit()
    self.tic()
    self.portal.portal_types['Preference'].allowed_content_types = ('Foo',)
    self.portal.foo_module.manage_role(role_to_manage='Author',
                                permissions=[Permissions.AddPortalContent,
                                             Permissions.CopyOrMove,
                                             ])

  def test_Template(self):
    self.login(self.id())
    preference = self.portal.portal_preferences.newContent(portal_type='Preference')
    preference.priority = Priority.USER
    preference.enable()

    transaction.commit()
    self.tic()

    document = self.portal.foo_module.newContent(portal_type='Foo')
    document.edit(title='My Foo 1')
    document.newContent(portal_type='Foo Line')

    transaction.commit()
    self.tic()

    document.Base_makeTemplateFromDocument(form_id=None)

    transaction.commit()
    self.tic()

    self.assertEqual(len(preference.objectIds()), 1)

    # make sure that subobjects are not unindexed after making template.
    subobject_uid = document.objectValues()[0].getUid()
    self.assertEqual(len(self.portal.portal_catalog(uid=subobject_uid)), 1)

    self.portal.foo_module.manage_delObjects(ids=[document.getId()])

    transaction.commit()
    self.tic()

    template = preference.objectValues()[0]

    cp = preference.manage_copyObjects(ids=[template.getId()], REQUEST=None, RESPONSE=None)
    new_document_list = self.portal.foo_module.manage_pasteObjects(cp)
    new_document_id = new_document_list[0]['new_id']
    new_document = self.portal.foo_module[new_document_id]
    new_document.makeTemplateInstance()

    transaction.commit()
    self.tic()

    self.assertEqual(new_document.getTitle(), 'My Foo 1')


  def test_TemplateDeletable(self):
    self.login(self.id())
    preference = self.portal.portal_preferences.newContent(portal_type='Preference')
    preference.priority = Priority.USER
    preference.enable()

    transaction.commit()
    self.tic()

    document = self.portal.foo_module.newContent(portal_type='Foo')
    document.edit(title='My Foo 1')
    document.newContent(portal_type='Foo Line')

    transaction.commit()
    self.tic()

    document.Base_makeTemplateFromDocument(form_id=None)

    transaction.commit()
    self.tic()

    self.assertEqual(len(preference.objectIds()), 1)

    # make sure that subobjects are not unindexed after making template.
    subobject_uid = document.objectValues()[0].getUid()
    self.assertEqual(len(self.portal.portal_catalog(uid=subobject_uid)), 1)

    self.portal.foo_module.manage_delObjects(ids=[document.getId()])

    transaction.commit()
    self.tic()

    template = preference.objectValues()[0]

    cp = preference.manage_copyObjects(ids=[template.getId()], REQUEST=None, RESPONSE=None)
    new_document_list = self.portal.foo_module.manage_pasteObjects(cp)
    new_document_id = new_document_list[0]['new_id']
    new_document = self.portal.foo_module[new_document_id]
    new_document.makeTemplateInstance()

    transaction.commit()
    self.tic()

    self.assertEqual(new_document.getTitle(), 'My Foo 1')

    # as templates are not indexable it is required to know, if they would
    # appear on Folder_getDeleteObjectList
    template_uid = template.getUid()
    self.assertEqual(
      1,
      len(preference.Folder_getDeleteObjectList(uid = [template_uid]))
    )

  def test_TemplateCreatePreferenceWithExistingUserPreference(self):
    self.login(self.id())
    user_preference = self.portal.portal_preferences.newContent(
        portal_type='Preference')
    user_preference.setPriority(Priority.USER)
    user_preference.enable()
    transaction.commit()
    self.tic()

    document = self.portal.foo_module.newContent(portal_type='Foo')
    transaction.commit()
    self.tic()

    document.Base_makeTemplateFromDocument(form_id=None)
    transaction.commit()
    self.tic()

    # created preference is reused to store template
    self.assertEquals('enabled', user_preference.getPreferenceState())
    self.assertEqual(len(user_preference.objectIds()), 1)

  def test_TemplateCreatePreferenceWithSystemPreferenceEnabled(self):
    # TODO: This test *might* be removed if it is good to trust
    #       getActivePreference to return only Preference portal type
    ERP5TypeTestCase.login(self, 'ERP5TypeTestCase')
    system_preference = self.portal.portal_preferences.newContent(
        portal_type='System Preference')
    system_preference.setPriority(Priority.SITE)
    system_preference.enable()
    transaction.commit()
    self.tic()
    self.login(self.id())
    user_preference = self.portal.portal_preferences.newContent(
        portal_type='Preference')
    user_preference.setPriority(Priority.USER)
    user_preference.enable()
    transaction.commit()
    self.tic()

    document = self.portal.foo_module.newContent(portal_type='Foo')
    transaction.commit()
    self.tic()

    document.Base_makeTemplateFromDocument(form_id=None)
    transaction.commit()
    self.tic()

    # created preference is reused to store template
    self.assertEquals('enabled', user_preference.getPreferenceState())
    self.assertEqual(len(user_preference.objectIds()), 1)

  def test_TemplateCreatePreference(self):
    self.login('another user with no active preference')
    active_user_preference_list = [p for p in
        self.portal.portal_preferences._getSortedPreferenceList()
        if p.getPriority() == Priority.USER]
    self.assertEquals([], active_user_preference_list)

    preference_id_list = list(self.portal.portal_preferences.objectIds())
    document = self.portal.foo_module.newContent(portal_type='Foo')
    transaction.commit()
    self.tic()

    document.Base_makeTemplateFromDocument(form_id=None)
    transaction.commit()
    self.tic()

    # a new preference is created
    new_preference_id_list = list(self.portal.portal_preferences.objectIds())
    self.assertEqual(len(preference_id_list) + 1, len(new_preference_id_list))
    preference_id = [x for x in new_preference_id_list if x not in
                            preference_id_list][0]
    preference = self.portal.portal_preferences._getOb(preference_id)

    self.assertEquals('Preference', preference.getPortalType())
    self.assertEquals('Document Template Container', preference.getTitle())
    self.assertEquals(Priority.USER, preference.getPriority())
    self.assertEquals('enabled', preference.getPreferenceState())

    self.assertEqual(len(preference.objectIds()), 1)

  def test_manyTemplatesWithoutReindexation(self):
    """Check what happen when templates are created one by one without reindexation"""
    self.login(self.id())
    active_user_preference_list = [p for p in
        self.portal.portal_preferences._getSortedPreferenceList()
        if p.getPriority() == Priority.USER]
    self.assertEquals([], active_user_preference_list)

    preference_id_list = list(self.portal.portal_preferences.objectIds())

    document1 = self.portal.foo_module.newContent(portal_type='Foo')
    transaction.commit()
    document2 = self.portal.foo_module.newContent(portal_type='Foo')
    transaction.commit()
    self.tic()

    document1.Base_makeTemplateFromDocument(form_id=None)
    transaction.commit()

    document2.Base_makeTemplateFromDocument(form_id=None)
    transaction.commit()

    self.tic()

    # a new preference is created
    new_preference_id_list = list(self.portal.portal_preferences.objectIds())
    self.assertEqual(len(preference_id_list) + 1, len(new_preference_id_list))
    preference_id = [x for x in new_preference_id_list if x not in
                            preference_id_list][0]
    preference = self.portal.portal_preferences._getOb(preference_id)

    self.assertEquals('Preference', preference.getPortalType())
    self.assertEquals('Document Template Container', preference.getTitle())
    self.assertEquals(Priority.USER, preference.getPriority())
    self.assertEquals('enabled', preference.getPreferenceState())

    self.assertEqual(len(preference.objectIds()), 2)

  def test_TemplateNotIndexable(self):
    # template documents are not indexable
    self.login(self.id())
    preference = self.portal.portal_preferences.newContent(portal_type='Preference')
    preference.priority = Priority.USER
    preference.enable()

    transaction.commit()
    self.tic()

    document = self.portal.foo_module.newContent(portal_type='Foo')
    document.edit(title='My Foo 1')
    document.newContent(portal_type='Foo Line')

    transaction.commit()
    self.tic()

    document.Base_makeTemplateFromDocument(form_id=None)
    transaction.commit()
    self.tic()
    self.assertTrue(document.isIndexable)
    self.assertEqual(len(preference.objectIds()), 1)
    template = preference.objectValues()[0]
    self.assertFalse(template.isIndexable)
    
    # Because they are not indexable, they cannot be found by catalog
    transaction.commit()
    self.tic()
    self.assertEquals(0, len(self.portal.portal_catalog(uid=template.getUid())))
    template_line = template.objectValues()[0]
    self.assertEquals(0,
        len(self.portal.portal_catalog(uid=template_line.getUid())))

    # and this is still true if you create two templates from the same document
    # #929
    document.Base_makeTemplateFromDocument(form_id=None)
    transaction.commit()
    self.tic()

    self.assertTrue(document.isIndexable)
    self.assertEqual(len(preference.objectIds()), 2)
    for template in preference.objectValues():
      self.assertFalse(template.isIndexable)


def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestTemplate))
  return suite
