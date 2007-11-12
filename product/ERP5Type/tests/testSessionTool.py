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

from Testing import ZopeTestCase
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.Document import newTempOrder
from AccessControl.SecurityManagement import newSecurityManager
from zLOG import LOG

try:
  from transaction import get as get_transaction
except ImportError:
  pass

class TestSessionTool(ERP5TypeTestCase):

  run_all_test = 1
  session_id = "123456789"
  
  def getTitle(self):
    return "Session Tool"
  
  def afterSetUp(self):
    self.login()
    
  def login(self, quiet=0, run=run_all_test):
    uf = self.getPortal().acl_users
    uf._doAddUser('ivan', '', ['Manager'], [])
    uf._doAddUser('ERP5TypeTestCase', '', ['Manager'], [])
    user = uf.getUserById('ivan').__of__(uf)
    newSecurityManager(None, user)

  def test_01_CheckSessionTool(self, quiet=0, run=run_all_test):
    """ Create portal_sessions tool and needed cache factory. """
    if not run:
      return
    if not quiet:
      message = '\nCheck SessionTool '
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
      portal = self.getPortal()
      portal_caches = portal.portal_caches
      portal.manage_addProduct['ERP5Type'].manage_addTool('ERP5 Session Tool')
      self.assertNotEqual(None,getattr(portal, 'portal_sessions', None))
      
      ## create needed cache fatory for Session Tool
      session_cache_factory = portal_caches.newContent(portal_type="Cache Factory", \
                                                       id = 'erp5_session_cache')
      session_cache_factory.setCacheDuration(36000)
      ram_cache_plugin = session_cache_factory.newContent(portal_type="Ram Cache")
      ram_cache_plugin.setCacheDuration(36000)
      ram_cache_plugin.setIntIndex(0)

      ## update Ram Cache structure
      portal_caches.updateCache()
      get_transaction().commit()
      
  def test_02_CreateSessionObject(self, quiet=0, run=run_all_test):
    """ Create a session object and check if API (newContent) is properly working. 
        Check if storing objects is working as expected. """
    if not run:
      return
    if not quiet:
      message = '\nCreate of session object and assign attributes.'
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
      portal = self.getPortal()
      portal_sessions = portal.portal_sessions
      session = portal_sessions.newContent(
                        self.session_id, \
                        attr_1 = newTempOrder(portal_sessions, '1'), \
                        attr_2 = newTempOrder(portal_sessions, '2'), \
                        attr_3 = 1,
                        attr_4 = 0.1,
                        attr_5 = {},
                        attr_6 = 'string',)
      ## check temp (RAM based) attributes stored in session
      for i in range (1, 3):
        attr_name = 'attr_%s' %i
        self.assert_(attr_name in session.keys())
        attr = session[attr_name]
        self.assert_(str(i), attr.getId())
        self.assert_(0 == len(attr.objectIds()))
      ## check primitive stype storage
      self.assert_(1 == session['attr_3'])
      self.assert_(0.1 == session['attr_4'])
      self.assert_({} == session['attr_5'])
      self.assert_('string' == session['attr_6'])
        

  def test_03_DeleteSessionObjectAttributes(self, quiet=0, run=run_all_test):
    """ Delete session keys."""
    if not run:
      return
    if not quiet:
      message = '\nDelete some session keys.'
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
      portal = self.getPortal()
      portal_sessions = portal.portal_sessions
      session = portal_sessions[self.session_id]
      session.pop('attr_1')
      session.pop('attr_2')
      self.assert_(not 'attr_1' in session.keys())
      self.assert_(not 'attr_2' in session.keys())
      
  def test_04_DeleteSessionObject(self, quiet=0, run=run_all_test):
    """ Get session object and check keys stored in previous test. """
    if not run:
      return
    if not quiet:
      message = '\nDelete session object.'
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
      portal = self.getPortal()
      portal_sessions = portal.portal_sessions
      ## delete it 
      portal_sessions.manage_delObjects(self.session_id)
      session = portal_sessions[self.session_id]
      self.assert_(0 == len(session.keys()))

  def test_session_dict_interface(self):
    session = self.portal.portal_sessions[self.session_id]
    session['foo'] = 'Bar'
    self.assertTrue('foo' in session)
    self.assertEquals('Bar', session['foo'])
    self.assertEquals('Bar', session.get('foo'))
    self.assertFalse('bar' in session)
    self.assertEquals('Default', session.get('bar', 'Default'))
    self.assertRaises(KeyError, session.__getitem__, 'bar')

  def test_session_getattr(self):
    session = self.portal.portal_sessions[self.session_id]
    session['foo'] = 'Bar'
    self.assertEquals('Bar', session.foo)
    self.assertEquals('Default', getattr(session, 'bar', 'Default'))
    self.assertRaises(AttributeError, getattr, session, 'bar')

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestSessionTool))
  return suite

