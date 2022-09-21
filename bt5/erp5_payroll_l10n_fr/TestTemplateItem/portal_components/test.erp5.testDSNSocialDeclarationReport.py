#############################################################################
#
# Copyright (c) 2002-2015 Nexedi SA and Contributors. All Rights Reserved.
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
import difflib
import os
import time

from DateTime import DateTime
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase

class TestDSNSocialDeclarationReport(ERP5TypeTestCase):
  """
  Test Suite for the generation of the French Social Declaration Report,
  the DSN (Declaration Sociale Nominative)
  """

  def getTitle(self):
    return "DSN Social Declaration Report"

  def afterSetUp(self):
    """
    This is ran before anything, used to set the environment
    """
    self.dsn_module = self.portal.getDefaultModuleValue("DSN Monthly Report")
    self.setTimeZoneToUTC()
    self.pinDateTime(DateTime(2015, 12, 1))
    # Create the id_group 'dsn_event_counter'
    self.portal.portal_ids.generateNewId(id_group='dsn_event_counter', id_generator='continuous_integer_increasing')

  def beforeTearDown(self):
    self.unpinDateTime()

  def test_01_makeMonthlyDSN(self):
    """
    Compute a DSN in a test environment, and check is the newly created
    document is exactly the same as a previously computed one.
    """
    test_dsn = self.dsn_module['test_model']
    test_dsn.DSNMonthlyReport_makeReport()
    reference_DSN = getattr(self.portal.portal_skins.erp5_payroll_l10n_fr_test, "test_model.dsn").data
    diff_list = []
    for unit_diff in difflib.unified_diff(reference_DSN.split('\n'), test_dsn.getTextContent().split('\n')):
      diff_list.append(unit_diff)
    self.assertEqual(reference_DSN, test_dsn.getTextContent(), msg='\n'.join(diff_list))
