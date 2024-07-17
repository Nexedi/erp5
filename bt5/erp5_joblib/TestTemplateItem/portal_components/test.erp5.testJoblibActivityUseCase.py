##############################################################################
#
# Copyright (c) 2002-2012 Nexedi SA and Contributors. All Rights Reserved.
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

class Test(ERP5TypeTestCase):
  """
  Test joblib usecases with CMFActivity
  """

  def getTitle(self):
    return "TestJoblibUsecases"

  def test_randomForest(self):
    path = self.portal.Base_driverScriptRandomForest()
    self.tic()
    active_process = self.portal.portal_activities.unrestrictedTraverse(path)
    result = active_process.getResultList()
    self.assertAlmostEqual(0.9, result[0].result, 0)

  def test_UnderRootOfSquaresFunction(self):
    path = self.portal.Base_driverScriptSquareRoot()
    self.tic()
    active_process = self.portal.portal_activities.unrestrictedTraverse(path)
    result = active_process.getResultList()
    self.assertEqual([0.0, 1.0, 2.0, 3.0, 4.0], result[0].result)

