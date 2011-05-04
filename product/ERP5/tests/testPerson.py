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

from AccessControl.SecurityManagement import newSecurityManager
from AccessControl import Unauthorized

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type import Permissions

import transaction


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
    ## instance its reference must be resetted
    self.assertEquals(person_copy_obj.getReference(), None)
    
    ## set object as if installed from bt5 (simulate it)
    request = self.app.REQUEST
    request.set('is_business_template_installation', 1)
    person_copy = person_module.manage_copyObjects(ids=(person.getId(),))
    person_copy_id = person_module.manage_pasteObjects(person_copy)[0]['new_id']
    person_copy_obj = person_module[person_copy_id]
    ## because we setup Person object from business template 
    ## its reference must NOT be resetted
    self.assertEquals(person_copy_obj.getReference(), person.getReference())

  # title & first_name, last_name
  def testEmptyTitle(self):
    p = self._makeOne()
    self.assertEquals('', p.getTitle())
  
  def testSetFirstName(self):
    p = self._makeOne()
    p.setFirstName('first')
    self.assertEquals('first', p.getFirstName())

  def testSetLastName(self):
    p = self._makeOne(id='person')
    p.setLastName('last')
    self.assertEquals('last', p.getLastName())

  def testTitleFromFirstLastName(self):
    p = self._makeOne(id='person')
    p.setFirstName('first')
    p.setLastName('last')
    self.assertEquals('first last', p.getTitle())

  def testEditFirstNameLastName(self):
    # using 'edit' method
    p = self._makeOne(id='person')
    p.edit( first_name='first',
            last_name='last' )
    self.assertEquals('first', p.getFirstName())
    self.assertEquals('last', p.getLastName())
    self.assertEquals('first last', p.getTitle())

  def testEditTitleFirstNameLastName(self):
    p = self._makeOne(id='person')
    p.edit( first_name='first',
            last_name='last',
            title='title' )
    # no infinite loop :) but there's no guarantee on the behaviour
    
  def testGetTitleOrId(self):
    p = self._makeOne(id='person')
    self.assertEquals('person', p.getTitleOrId())
    self.assertEquals('person', p.title_or_id())

    p.edit( first_name='first',
            last_name='last', )
    self.assertEquals('first last', p.getTitleOrId())
    self.assertEquals('first last', p.title_or_id())
    
  def testHasTitle(self):
    p = self._makeOne(id='person')
    self.assertFalse(p.hasTitle())
    p.setFirstName('bob')
    self.assertTrue(p.hasTitle())

  def testSetPasswordSecurity(self):
    p = self._makeOne(id='person')
    p.manage_permission(Permissions.SetOwnPassword, [], 0)
    self.assertRaises(Unauthorized, p.setPassword, 'secret')
    self.assertRaises(Unauthorized, p.edit, password='secret')

    # setPassword(None) has no effect, because in the user interface we always
    # show an empty field for password. Note that it also does not require any
    # specific permission.
    p.setPassword(None)
    self.assertFalse(p.getPassword())
    # Make sure that edit method cannot call __setPasswordByForce and nothing
    # changes.
    p.edit(password_by_force='waaa')
    self.assertFalse(p.getPassword())

    p.manage_permission(Permissions.SetOwnPassword, ['Anonymous'], 0)
    p.setPassword('secret')
    self.assertTrue(p.getPassword())

  def testPasswordFormat(self):
    p = self._makeOne(id='person')
    p._setEncodedPassword('pass_A', format='A')
    p._setEncodedPassword('pass_B', format='B')
    self.assertEquals('pass_A', p.getPassword(format='A'))
    self.assertEquals('pass_B', p.getPassword(format='B'))

    self.assertEquals(None, p.getPassword(format='unknown'))
    self.assertEquals('default', p.getPassword('default', format='unknown'))

    self.assertEquals(None, p.getPassword())
    self.assertEquals('default', p.getPassword('default'))

  def testPreferenceInteractionWorkflow(self):
    """ when setting reference, a script create preference is
        called by activities, check this behavior. """
    person_module = self.getPersonModule()
    title = "Séb"
    person = person_module.newContent(portal_type='Person', title=title)
    person.setReference('test_seb')
    transaction.commit()
    self.tic()
    portal = self.getPortal()
    last_id = portal.portal_preferences.getLastId()
    last_preference = portal.portal_preferences[last_id]
    self.assertTrue("Séb" in last_preference.getTitle())
    

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestPerson))
  return suite
