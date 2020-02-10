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

from Testing.ZopeTestCase import TestCase
from Products.ERP5Type.TransactionalVariable import getTransactionalVariable

class TestTransactionalVariable(TestCase):

    from transaction import abort, commit

    def test_01_DictInterface(self):
      """Check if a transaction variable behaves in the same way as a dict.  """

      tv = getTransactionalVariable()

      # Test frequently used dict methods. This does not cover everything,
      # but should be enough.
      tv.clear()
      self.assertEqual(len(tv), 0)
      with self.assertRaises(KeyError):
        tv['toto']

      tv['toto'] = 'titi'
      self.assertEqual(len(tv), 1)
      self.assertEqual(tv['toto'], 'titi')

      self.assertIsNone(tv.get('foo'))
      tv.setdefault('foo', 'bar')
      self.assertEqual(len(tv), 2)
      self.assertEqual(tv['foo'], 'bar')

      self.assertIn('foo', tv)
      del tv['foo']
      self.assertNotIn('foo', tv)
      self.assertEqual(len(tv), 1)

    def test_02_Expiration(self):
      """Check if a transaction variable does not persist over multiple
      transactions.
      """
      tv = getTransactionalVariable()
      tv.clear()
      self.assertEqual(len(tv), 0)

      # Commit and check.
      tv['toto'] = 'titi'
      self.assertEqual(tv['toto'], 'titi')
      self.commit()
      self.assertNotIn('toto', tv)

      # Abort and check.
      tv['toto'] = 'titi'
      self.assertEqual(tv['toto'], 'titi')
      self.abort()
      self.assertNotIn('toto', tv)

    def test_03_Durability(self):
      """Check if a transaction variable does not disappear within the same
      transaction.
      """
      tv = getTransactionalVariable()
      tv.clear()
      self.assertEqual(len(tv), 0)

      # Set both a transaction variable and a volatile attribute,
      # in order to detect the difference between their behaviors.
      tv['toto'] = 'titi'
      self.assertEqual(tv['toto'], 'titi')
      app = self.app
      vattr = '_v_erp5type_test_durability'
      setattr(app, vattr, 'dummy')
      self.assertEqual(getattr(app, vattr), 'dummy')

      # Force to minimize the connection cache so that volatile attributes
      # and unghostified objects are discarded.
      app._p_jar.cacheMinimize()
      self.assertIn('toto', tv)
      self.assertEqual(tv['toto'], 'titi')
      self.assertIsNone(getattr(app, vattr, None))
