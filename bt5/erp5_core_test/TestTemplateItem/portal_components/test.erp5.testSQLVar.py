##############################################################################
#
# Copyright (c) 2002-2023 Nexedi SA and Contributors. All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly adviced to contract a Free Software
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
##############################################################################

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase

class TestSQLVar(ERP5TypeTestCase):

  def test_sqlvar(self):
    """
    Make sure that sqlvar patch does not break sqlvar type="nb".
    """
    sqlmethod = self.portal.newContent(portal_type='SQL Method',
                                       temp_object=True,
                                       connection_id='erp5_sql_connection',
                                       arguments_src='value',
                                       src='<dtml-sqlvar value type="string">')
    self.assertEqual(sqlmethod(value='', src__=1), b"''")
    self.assertEqual(sqlmethod(value=None, src__=1), b'null')

    sqlmethod.edit(src='<dtml-sqlvar value type="string" optional>')
    self.assertEqual(sqlmethod(value='', src__=1), b"''")
    self.assertEqual(sqlmethod(value=None, src__=1), b'null')

    sqlmethod.edit(src='<dtml-sqlvar value type="nb">')
    self.assertRaises(ValueError, sqlmethod, value='', src__=1)
    self.assertEqual(sqlmethod(value=None, src__=1), b'null')

    sqlmethod.edit(src='<dtml-sqlvar value type="nb" optional>')
    self.assertEqual(sqlmethod(value='', src__=1), b'null')
    self.assertEqual(sqlmethod(value=None, src__=1), b'null')
