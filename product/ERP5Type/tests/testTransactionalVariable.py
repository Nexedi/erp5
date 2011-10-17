##############################################################################
#
# Copyright (c) 2007 Nexedi SARL and Contributors. All Rights Reserved.
#                    Yoshinori Okuji <yo@nexedi.com>
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

import transaction
import unittest

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.tests.utils import LogInterceptor
from Products.ERP5Type.TransactionalVariable import getTransactionalVariable

class TestTransactionalVariable(ERP5TypeTestCase, LogInterceptor):
    # Some helper methods

    def getTitle(self):
      return "Transactional Variable"

    def getBusinessTemplateList(self):
      """
        Return the list of business templates.
      """
      return ()

    def afterSetUp(self):
      self.login()

    def test_01_DictInterface(self):
      """Check if a transaction variable behaves in the same way as a dict.  """
   
      tv = getTransactionalVariable()
      self.failIfEqual(tv, None)

      # Test frequently used dict methods. This does not cover everything,
      # but should be enough.
      tv.clear()
      self.failUnlessEqual(len(tv), 0)
      self.failUnlessRaises(KeyError, tv.__getitem__, 'toto')

      tv['toto'] = 'titi'
      self.failUnlessEqual(len(tv), 1)
      self.failUnlessEqual(tv['toto'], 'titi')

      self.failUnlessEqual(tv.get('foo'), None)
      tv.setdefault('foo', 'bar')
      self.failUnlessEqual(len(tv), 2)
      self.failUnlessEqual(tv['foo'], 'bar')

      self.failUnless('foo' in tv)
      del tv['foo']
      self.failIf('foo' in tv)
      self.failUnlessEqual(len(tv), 1)

    def test_02_Expiration(self):
      """Check if a transaction variable does not persist over multiple
      transactions.
      """
      tv = getTransactionalVariable()
      self.failIfEqual(tv, None)

      tv.clear()
      self.failUnlessEqual(len(tv), 0)

      # Commit and check.
      tv['toto'] = 'titi'
      self.failUnlessEqual(tv['toto'], 'titi')
      transaction.commit()
      self.failIf('toto' in tv)

      # Abort and check.
      tv['toto'] = 'titi'
      self.failUnlessEqual(tv['toto'], 'titi')
      transaction.abort()
      self.failIf('toto' in tv)

    def test_03_Durability(self):
      """Check if a transaction variable does not disappear within the same
      transaction.
      """
      tv = getTransactionalVariable()
      self.failIfEqual(tv, None)

      tv.clear()
      self.failUnlessEqual(len(tv), 0)

      # Set both a transaction variable and a volatile attribute,
      # in order to detect the difference between their behaviors.
      tv['toto'] = 'titi'
      self.failUnlessEqual(tv['toto'], 'titi')
      portal = self.getPortal()
      vattr = '_v_erp5type_test_durability'
      setattr(portal, vattr, 'dummy')
      self.failUnlessEqual(getattr(portal, vattr), 'dummy')

      # Force to minimize the connection cache so that volatile attributes
      # and unghostified objects are discarded.
      portal._p_jar.cacheMinimize()
      self.failUnless('toto' in tv)
      self.failUnlessEqual(tv['toto'], 'titi')
      self.failUnlessEqual(getattr(portal, vattr, None), None)

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestTransactionalVariable))
  return suite
