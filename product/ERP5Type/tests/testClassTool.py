##############################################################################
#
# Copyright (c) 2002-2007 Nexedi SARL and Contributors. All Rights Reserved.
#                     Jean-Paul Smets <jp@nexedi.com>
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

from Testing import ZopeTestCase
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from AccessControl.SecurityManagement import newSecurityManager
from Products.ERP5Type.tests.utils import installRealClassTool
from zLOG import LOG
import time

try:
  from transaction import get as get_transaction
except ImportError:
  pass

class TestClassTool(ERP5TypeTestCase):

  run_all_test = 1
  quiet = 1
  
  def getTitle(self):
    return "Class Tool"
  
  def afterSetUp(self):
    self.login()
    installRealClassTool(self.getPortal())
    
  def login(self, quiet=0, run=run_all_test):
    uf = self.getPortal().acl_users
    uf._doAddUser('seb', '', ['Manager'], [])
    uf._doAddUser('ERP5TypeTestCase', '', ['Manager'], [])
    user = uf.getUserById('seb').__of__(uf)
    newSecurityManager(None, user)

  def test_01_CheckClassTool(self, quiet=quiet, run=run_all_test):
    """
      Make sure that portal_classes exists
    """
    if not run:
      return
    if not quiet:
      message = '\nCheck ClassTool '
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
      
    portal = self.getPortal()
    self.assertNotEqual(None,getattr(portal,'portal_classes',None))
    get_transaction().commit()


  def test_02_CheckFileWriteIsTransactional(self, quiet=quiet,
                                            run=run_all_test):
    if not run:
      return
    if not quiet:
      message = '\nCheck File Transaction'
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
      
    portal = self.getPortal()
    portal_classes = portal.portal_classes
    
    portal_classes.newDocument('Toto')
    get_transaction().abort()
    self.assertNotEqual(portal_classes.getLocalDocumentList(), ['Toto'])

    portal_classes.newDocument('Toto')
    get_transaction().commit()
    self.assertEqual(portal_classes.getLocalDocumentList(), ['Toto'])


import unittest
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestClassTool))
    return suite

