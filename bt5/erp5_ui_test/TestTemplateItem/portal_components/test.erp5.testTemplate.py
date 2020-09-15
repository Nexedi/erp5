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
from unittest import expectedFailure
from AccessControl.SecurityManagement import newSecurityManager
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Form.PreferenceTool import Priority


class TestTemplate(ERP5TypeTestCase):
  """A test for Template.
  """

  def getTitle(self):
    return "Template"

  def getBusinessTemplateList(self):
    """Returns list of BT to be installed."""
    return ('erp5_base', 'erp5_knowledge_pad', 'erp5_ui_test')

  def createUserAndLogin(self, name=None, additional_role_list=()):
    """login with Member, Author and specified roles."""
    uf = self.getPortal().acl_users
    role_list = ['Member', 'Author', 'Auditor']
    role_list.extend(additional_role_list)
    uf._doAddUser(name, '', role_list, [])
    user = uf.getUserById(name).__of__(uf)
    newSecurityManager(None, user)

  def afterSetUp(self):
    self.login()
    portal_preferences = self.portal.portal_preferences
    portal_preferences.deleteContent(list(portal_preferences.objectIds()))
    self.tic()
    self.portal.portal_types.Preference._setTypeAllowedContentTypeList(
      ('Foo', 'Knowledge Pad'))

  def test_Template(self):
    self.createUserAndLogin(self.id())
    preference = self.portal.portal_preferences.newContent(portal_type='Preference')
    preference.priority = Priority.USER
    preference.enable()

    self.tic()

    document = self.portal.foo_module.newContent(portal_type='Foo')
    document.edit(title='My Foo 1')
    document.newContent(portal_type='Foo Line')

    self.tic()

    document.Base_makeTemplateFromDocument(form_id=None)

    self.tic()

    self.assertEqual(len(preference.objectIds()), 1)

    # make sure that subobjects are not unindexed after making template.
    subobject_uid = document.objectValues()[0].getUid()
    self.assertEqual(len(self.portal.portal_catalog(uid=subobject_uid)), 1)

    self.portal.foo_module.manage_delObjects(ids=[document.getId()])

    self.tic()

    template = preference.objectValues()[0]

    cp = preference.manage_copyObjects(ids=[template.getId()], REQUEST=None, RESPONSE=None)
    new_document_list = self.portal.foo_module.manage_pasteObjects(cp)
    new_document_id = new_document_list[0]['new_id']
    new_document = self.portal.foo_module[new_document_id]
    new_document.makeTemplateInstance()

    self.tic()

    self.assertEqual(new_document.getTitle(), 'My Foo 1')


  def test_TemplateDeletable(self):
    self.createUserAndLogin(self.id())
    preference = self.portal.portal_preferences.newContent(portal_type='Preference')
    preference.priority = Priority.USER
    preference.enable()

    self.tic()

    document = self.portal.foo_module.newContent(portal_type='Foo')
    document.edit(title='My Foo 1')
    document.newContent(portal_type='Foo Line')

    self.tic()

    document.Base_makeTemplateFromDocument(form_id=None)

    self.tic()

    self.assertEqual(len(preference.objectIds()), 1)

    # make sure that subobjects are not unindexed after making template.
    subobject_uid = document.objectValues()[0].getUid()
    self.assertEqual(len(self.portal.portal_catalog(uid=subobject_uid)), 1)

    self.portal.foo_module.manage_delObjects(ids=[document.getId()])

    self.tic()

    template = preference.objectValues()[0]

    cp = preference.manage_copyObjects(ids=[template.getId()], REQUEST=None, RESPONSE=None)
    new_document_list = self.portal.foo_module.manage_pasteObjects(cp)
    new_document_id = new_document_list[0]['new_id']
    new_document = self.portal.foo_module[new_document_id]
    new_document.makeTemplateInstance()

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
    self.createUserAndLogin(self.id())
    user_preference = self.portal.portal_preferences.newContent(
        portal_type='Preference')
    user_preference.setPriority(Priority.USER)
    user_preference.enable()
    self.tic()

    document = self.portal.foo_module.newContent(portal_type='Foo')
    self.tic()

    document.Base_makeTemplateFromDocument(form_id=None)
    self.tic()

    # created preference is reused to store template
    self.assertEqual('enabled', user_preference.getPreferenceState())
    self.assertEqual(len(user_preference.objectIds()), 1)

  def test_TemplateCreatePreferenceWithExistingNonAuthorizedPreference(self):
    # When there is an active preference, but without add permission in that
    # preference, another preference is created when making a template
    self.createUserAndLogin(self.id())
    unauthorized_preference = self.portal.portal_preferences.newContent(
        portal_type='Preference')
    unauthorized_preference.enable()
    # it's not authorized to add content in this preference
    unauthorized_preference.manage_permission('Add portal content', (), acquire=0)
    preference_id_list = list(self.portal.portal_preferences.objectIds())

    self.tic()

    document = self.portal.foo_module.newContent(portal_type='Foo')
    self.tic()

    document.Base_makeTemplateFromDocument(form_id=None)
    self.tic()

    # this preference was not used
    self.assertEqual(len(unauthorized_preference.objectIds()), 0)

    # a new preference is created
    new_preference_id_list = list(self.portal.portal_preferences.objectIds())
    self.assertEqual(len(preference_id_list) + 1, len(new_preference_id_list))
    preference_id = [x for x in new_preference_id_list if x not in
                            preference_id_list][0]
    preference = self.portal.portal_preferences._getOb(preference_id)
    self.assertEqual('Preference', preference.getPortalType())
    self.assertEqual('enabled', preference.getPreferenceState())

    self.assertEqual(len(preference.objectIds()), 1)

  def test_TemplateCreateWithSameTitleUpdateExisting(self):
    # When we create a template with the same title as an existing template, it
    # replaces the existing one.
    self.createUserAndLogin(self.id())
    user_preference = self.portal.portal_preferences.newContent(
        portal_type='Preference')
    user_preference.setPriority(Priority.USER)
    user_preference.enable()
    self.tic()

    document = self.portal.foo_module.newContent(portal_type='Foo',
                                                 title='template',
                                                 description='First document')
    self.tic()

    document.Base_makeTemplateFromDocument(form_id=None)
    self.tic()

    self.assertEqual(len(user_preference.objectIds()), 1)
    self.assertEqual(user_preference.objectValues()[0].getDescription(),
                     'First document')

    other_document = self.portal.foo_module.newContent(
                                    portal_type='Foo',
                                    title='template',
                                    description="Another document")
    other_document.Base_makeTemplateFromDocument(form_id=None)
    self.tic()
    self.assertEqual(len(user_preference.objectIds()), 1)
    self.assertEqual(user_preference.objectValues()[0].getDescription(),
                     'Another document')


  def test_TemplateCreatePreferenceWithSystemPreferenceEnabled(self):
    # TODO: This test *might* be removed if it is good to trust
    #       getActivePreference to return only Preference portal type
    self.login()
    system_preference = self.portal.portal_preferences.newContent(
        portal_type='System Preference')
    system_preference.setPriority(Priority.SITE)
    system_preference.enable()
    self.tic()
    self.createUserAndLogin(self.id())
    user_preference = self.portal.portal_preferences.newContent(
        portal_type='Preference')
    user_preference.setPriority(Priority.USER)
    user_preference.enable()
    self.tic()

    document = self.portal.foo_module.newContent(portal_type='Foo')
    self.tic()

    document.Base_makeTemplateFromDocument(form_id=None)
    self.tic()

    # created preference is reused to store template
    self.assertEqual('enabled', user_preference.getPreferenceState())
    self.assertEqual(len(user_preference.objectIds()), 1)

  def test_TemplateCreatePreference(self):
    self.createUserAndLogin('another user with no active preference')
    active_user_preference_list = [p for p in
        self.portal.portal_preferences._getSortedPreferenceList()
        if p.getPriority() == Priority.USER]
    self.assertEqual([], active_user_preference_list)

    preference_id_list = list(self.portal.portal_preferences.objectIds())
    document = self.portal.foo_module.newContent(portal_type='Foo')
    self.tic()

    document.Base_makeTemplateFromDocument(form_id=None)
    self.tic()

    # a new preference is created
    new_preference_id_list = list(self.portal.portal_preferences.objectIds())
    self.assertEqual(len(preference_id_list) + 1, len(new_preference_id_list))
    preference_id = [x for x in new_preference_id_list if x not in
                            preference_id_list][0]
    preference = self.portal.portal_preferences._getOb(preference_id)
    self.assertEqual('Preference', preference.getPortalType())
    self.assertEqual('Document Template Container', preference.getTitle())
    self.assertEqual(Priority.USER, preference.getPriority())
    self.assertEqual('enabled', preference.getPreferenceState())

    self.assertEqual(len(preference.objectIds()), 1)

  # Reason for test failure:
  #
  # Base_makeTemplateFromDocument uses portal_preference.getActivePreference(),
  # and if the user has no preference, it creates a new preference to attach it
  # the template.
  # But getActivePreference uses the catalog, for performance reasons. Which
  # means that two successive calls to Base_makeTemplateFromDocument, from an
  # initial state where the user has no active preferences, will create wrongly
  # two preferences instead of one: during the second call, a preference does
  # exist, and is enabled for current user, but is just not yet reindexed.
  @expectedFailure
  def test_manyTemplatesWithoutReindexation(self):
    """Check what happen when templates are created one by one without reindexation"""
    self.createUserAndLogin(self.id())
    active_user_preference_list = [p for p in
        self.portal.portal_preferences._getSortedPreferenceList()
        if p.getPriority() == Priority.USER]
    self.assertEqual([], active_user_preference_list)

    preference_id_list = list(self.portal.portal_preferences.objectIds())

    document1 = self.portal.foo_module.newContent(portal_type='Foo')
    self.commit()
    document2 = self.portal.foo_module.newContent(portal_type='Foo')
    self.tic()

    document1.Base_makeTemplateFromDocument(form_id=None)
    self.commit()

    document2.Base_makeTemplateFromDocument(form_id=None)
    self.commit()

    self.tic()

    # a new preference is created
    new_preference_id_list = list(self.portal.portal_preferences.objectIds())
    self.assertEqual(len(preference_id_list) + 1, len(new_preference_id_list))
    preference_id = [x for x in new_preference_id_list if x not in
                            preference_id_list][0]
    preference = self.portal.portal_preferences._getOb(preference_id)

    self.assertEqual('Preference', preference.getPortalType())
    self.assertEqual('enabled', preference.getPreferenceState())
    self.assertEqual(len(preference.objectIds()), 2)

  def _testTemplateNotIndexable(self, document, additional_role_list=()):
    # template documents are not indexable
    self.portal.portal_activities.manage_enableActivityTracking()
    self.portal.portal_activities.manage_enableActivityTimingLogging()
    self.portal.portal_activities.manage_enableActivityCreationTrace()
    self.createUserAndLogin(self.id(), additional_role_list=additional_role_list)
    preference = self.portal.portal_preferences.newContent(portal_type='Preference')
    preference.priority = Priority.USER
    preference.enable()

    self.tic()
    self.assertEqual(
      self.portal.portal_catalog(
        path=preference.getPath() + '/%',
      ).dictionaries(),
      [],
    )

    document.Base_makeTemplateFromDocument(form_id=None)
    self.tic()

    # making a new template should not index the new template nor any of
    # its subobjects
    self.assertEqual(
      self.portal.portal_catalog(
        path=preference.getPath() + '/%',
      ).dictionaries(),
      [],
    )

    self.assertTrue(document.isIndexable)
    self.assertEqual(len(preference.objectIds()), 1)
    template = preference.objectValues()[0]
    self.assertFalse(template.isIndexable)

    # Because they are not indexable, they cannot be found by catalog
    self.assertEqual(0, len(self.portal.portal_catalog(uid=template.getUid())))
    template_line = template.objectValues()[0]
    self.assertEqual(0,
        len(self.portal.portal_catalog(uid=template_line.getUid())))

    # change the title, because creating another template with same title will
    # replace the first one
    document.setTitle('%sb' % document.getTitle())

    # and this is still true if you create two templates from the same document
    # #929
    document.Base_makeTemplateFromDocument(form_id=None)
    self.tic()

    self.assertTrue(document.isIndexable)
    self.assertEqual(len(preference.objectIds()), 2)
    for template in preference.objectValues():
      self.assertFalse(template.isIndexable)

  def test_DeliveryTemplateNotIndexable(self):
    document = self.portal.foo_module.newContent(portal_type='Foo')
    document.edit(title='My Foo 1')
    document.newContent(portal_type='Foo Line')
    self.tic()
    self._testTemplateNotIndexable(document)

  def test_NonDeliveryTemplateNotIndexable(self):
    document = self.portal.knowledge_pad_module.newContent(portal_type='Knowledge Pad')
    document.edit(title='My Knowledge Pad 1')
    document.newContent(portal_type='Knowledge Box')
    self.tic()
    # Only Manager can Copy and Move at Knowlede Pad Document when it is
    # 'invisible' state.
    self._testTemplateNotIndexable(document, additional_role_list=['Manager'])


def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestTemplate))
  return suite
