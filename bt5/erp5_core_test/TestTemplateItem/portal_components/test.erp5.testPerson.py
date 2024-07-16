# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2005 Nexedi SARL and Contributors. All Rights Reserved.
#                     Ivan Tyagov <ivan@nexedi.com>
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

import unittest
import mock

from AccessControl.SecurityManagement import newSecurityManager
from AccessControl import Unauthorized
from AccessControl.ZopeGuards import guarded_getattr

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type import Permissions



class TestPerson(ERP5TypeTestCase):

  run_all_test = 1

  def getTitle(self):
    return "Person Test"

  def getBusinessTemplateList(self):
    """  """
    return ('erp5_base',)

  def afterSetUp(self):
    self.portal = self.getPortal()
    self.login()

  def login(self, quiet=0, run=run_all_test):
    uf = self.getPortal().acl_users
    uf._doAddUser('seb', '', ['Manager'], [])
    uf._doAddUser('ERP5TypeTestCase', '', ['Manager'], [])
    user = uf.getUserById('seb').__of__(uf)
    newSecurityManager(None, user)

  def _makeOne(self, **kw):
    module = self.portal.person_module
    return module.newContent(portal_type="Person", **kw)

  def test_01_CopyPastePersonObject(self, quiet=0, run=run_all_test):
    """ Test copy/paste a Person object. """
    if not run:
      return
    person_module = self.getPersonModule()
    person = person_module.newContent(portal_type='Person')
    person.setReference('ivan')

    ## copy object as if using ERP5/ZMI UI
    person_copy = person_module.manage_copyObjects(ids=(person.getId(),))
    person_copy_id = person_module.manage_pasteObjects(person_copy)[0]['new_id']
    person_copy_obj = person_module[person_copy_id]
    ## because we copy/paste Person object in the same ERP5
    ## instance its user_id must be reset
    self.assertNotEqual(person_copy_obj.getUserId(), person.getUserId())

    ## set object as if installed from bt5 (simulate it)
    request = self.app.REQUEST
    request.set('is_business_template_installation', 1)
    person_copy = person_module.manage_copyObjects(ids=(person.getId(),))
    person_copy_id = person_module.manage_pasteObjects(person_copy)[0]['new_id']
    person_copy_obj = person_module[person_copy_id]
    ## because we setup Person object from business template
    ## its reference must NOT be resetted
    self.assertEqual(person_copy_obj.getReference(), person.getReference())
    # User id must still be different
    self.assertNotEqual(person_copy_obj.getUserId(), person.getUserId())

  def test_PersonGetTitleDefined(self):
    p = self._makeOne(title="title")
    self.assertEqual("title", p.getTitle())

  # title & first_name, last_name
  def testEmptyTitleFallbackOnUserId(self):
    p = self._makeOne()
    self.assertEqual(p.getUserId(), p.getTitle())

  def testEmptyTranslatedTitleFallbackOnUserId(self):
    p = self._makeOne()
    self.assertEqual(p.getUserId(), p.getTranslatedTitle())

  def testEmptyCompactTitleFallbackOnUserId(self):
    p = self._makeOne()
    self.assertEqual(p.getUserId(), p.getCompactTitle())

  def testEmptyCompactTranslatedTitleFallbackOnUserId(self):
    p = self._makeOne()
    self.assertEqual(p.getUserId(), p.getCompactTranslatedTitle())

  def testEmptyTitleFallbackOnId(self):
    # in the now rare event of a person without user id, the fallback is still to the id.
    p = self._makeOne(id=self.id(), user_id=None)
    self.assertEqual(self.id(), p.getTitle())

  def testEmptyTranslatedTitleFallbackOnId(self):
    p = self._makeOne(id=self.id(), user_id=None)
    self.assertEqual(self.id(), p.getTranslatedTitle())

  def testEmptyCompactTitleFallbackOnId(self):
    p = self._makeOne(id=self.id(), user_id=None)
    self.assertEqual(self.id(), p.getCompactTitle())

  def testEmptyCompactTranslatedTitleFallbackOnId(self):
    p = self._makeOne(id=self.id(), user_id=None)
    self.assertEqual(self.id(), p.getCompactTranslatedTitle())

  def testEmptyTitleFallbackOnReference(self):
    p = self._makeOne(reference='reference')
    self.assertEqual('reference', p.getTitle())

  def testEmptyTranslatedTitleFallbackOnReference(self):
    p = self._makeOne(reference='reference')
    self.assertEqual('reference', p.getTranslatedTitle())

  def testEmptyCompactTitleFallbackOnReference(self):
    p = self._makeOne(reference='reference')
    self.assertEqual('reference', p.getCompactTitle())

  def testEmptyCompactTranslatedTitleFallbackOnReference(self):
    p = self._makeOne(reference='reference')
    self.assertEqual('reference', p.getCompactTranslatedTitle())

  def testSetFirstName(self):
    p = self._makeOne()
    p.setFirstName('first')
    self.assertEqual('first', p.getFirstName())

  def testSetLastName(self):
    p = self._makeOne(id='person')
    p.setLastName('last')
    self.assertEqual('last', p.getLastName())

  def testTitleFromFirstLastName(self):
    p = self._makeOne(id='person')
    p.setFirstName('first')
    p.setLastName('last')
    self.assertEqual('first last', p.getTitle())
    p.setMiddleName('middle')
    self.assertEqual('first middle last', p.getTitle())

  def testTranslatedTitleFromFirstLastName(self):
    p = self._makeOne(id='person')
    p.setFirstName('first')
    p.setLastName('last')
    self.assertEqual('first last', p.getTranslatedTitle())
    p.setMiddleName('middle')
    self.assertEqual('first middle last', p.getTranslatedTitle())

  def testCompactTranslatedTitleFromFirstLastName(self):
    p = self._makeOne(id='person')
    p.setFirstName('first')
    p.setLastName('last')
    self.assertEqual('first last', p.getCompactTranslatedTitle())
    p.setMiddleName('middle')
    self.assertEqual('first middle last', p.getCompactTranslatedTitle())

  def testEditFirstNameLastName(self):
    # using 'edit' method
    p = self._makeOne(id='person')
    p.edit( first_name='first',
            last_name='last' )
    self.assertEqual('first', p.getFirstName())
    self.assertEqual('last', p.getLastName())
    self.assertEqual('first last', p.getTitle())
    self.assertEqual('first last', p.getTranslatedTitle())
    p.edit(middle_name='middle')
    self.assertEqual('first middle last', p.getTitle())
    self.assertEqual('first middle last', p.getTranslatedTitle())

  def testEditTitleFirstNameLastName(self):
    p = self._makeOne(id='person')
    p.edit( first_name='first',
            last_name='last',
            title='title' )
    self.assertEqual('first last', p.getTitle())
    p.edit(middle_name='middle')
    self.assertEqual('first middle last', p.getTitle())

  def testGetTitleOrId(self):
    p = self._makeOne()
    self.assertEqual(p.getUserId(), p.getTitleOrId())
    self.assertEqual(p.getUserId(), p.title_or_id())

    p.edit(reference='reference')
    self.assertEqual('reference', p.getTitleOrId())
    self.assertEqual('reference', p.title_or_id())

    p.edit( first_name='first',
            last_name='last', )
    self.assertEqual('first last', p.getTitleOrId())
    self.assertEqual('first last', p.title_or_id())

    p.edit(middle_name='middle')
    self.assertEqual('first middle last', p.getTitleOrId())
    self.assertEqual('first middle last', p.title_or_id())

  def testHasTitle(self):
    p = self._makeOne(id='person')
    self.assertFalse(p.hasTitle())
    p.setFirstName('bob')
    self.assertTrue(p.hasTitle())

  def testCreatingPersonDoesNotModifyPersonModule(self):
    # creating a first entry in the module modifies the module, so make sure we have at least one.
    self.portal.person_module.newContent()
    self.tic()
    self.assertFalse(self.portal.person_module._p_changed)

    # use an id generator which does not modify the module
    with mock.patch.object(self.portal.person_module.__class__, 'generateNewId', return_value=self.id()):
      person = self.portal.person_module.newContent(portal_type='Person')
    self.assertTrue(person.getUserId())
    self.assertFalse(self.portal.person_module._p_changed)

  def testSetPasswordSecurityOnPerson(self):
    self._testSetPasswordSecurity(
        self._makeOne())

  def testSetPasswordSecurityOnERP5Login(self):
    self._testSetPasswordSecurity(
        self._makeOne().newContent(portal_type='ERP5 Login'))

  def _testSetPasswordSecurity(self, login):
    login.manage_permission(Permissions.SetOwnPassword, [], 0)
    with self.assertRaises(Unauthorized):
      guarded_getattr(login, 'setPassword')('secret')
    with self.assertRaises(Unauthorized):
      guarded_getattr(login, 'edit')(password='secret')

    # edit(password=None) has no effect. It's a special case, because in the user interface
    # we show an empty field for password.
    login.edit(password=None)
    self.assertFalse(login.getPassword())
    # Make sure that edit method cannot call __setPasswordByForce and nothing
    # changes.
    login.edit(password_by_force='waaa')
    self.assertFalse(login.getPassword())

    login.manage_permission(Permissions.SetOwnPassword, ['Anonymous'], 0)
    login.setPassword('secret')
    password = login.getPassword()
    self.assertTrue(password)
    login.edit(password=None)
    self.assertEqual(login.getPassword(), password)

  def testSetUserIdSecurity(self):
    # Changing an already set user id needs "manage users" permissions,
    # but setting an initial user id does not.
    p = self._makeOne(user_id=None)
    p.manage_permission(Permissions.ManageUsers, [], 0)
    p.setUserId('initial_user_id')
    self.tic()
    self.assertRaises(Unauthorized, p.setUserId, 'something_else')
    self.abort()
    self.assertRaises(Unauthorized, p.edit, user_id='something_else')

  def testPasswordFormat(self):
    p = self._makeOne(id='person')
    p._setEncodedPassword(b'pass_A', format='A')
    p._setEncodedPassword(b'pass_B', format='B')
    self.assertEqual(b'pass_A', p.getPassword(format='A'))
    self.assertEqual(b'pass_B', p.getPassword(format='B'))

    self.assertEqual(None, p.getPassword(format='unknown'))
    self.assertEqual(b'default', p.getPassword(b'default', format='unknown'))

    self.assertEqual(None, p.getPassword())
    self.assertEqual(b'default', p.getPassword(b'default'))


def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestPerson))
  return suite
