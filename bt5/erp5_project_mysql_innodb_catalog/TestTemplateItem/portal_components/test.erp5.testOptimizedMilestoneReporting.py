#############################################################################
#
# Copyright  2009 Nexedi SA Contributors. All Rights Reserved.
#              Sebastien Robin <seb@nexedi.com>
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

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5ReportTestCase
from erp5.component.test.testMilestoneReporting import MilestoneReportingMixin

class TestOptimisedMilestoneReporting(MilestoneReportingMixin, ERP5ReportTestCase):
  """Same as above, with additionnal business template adding extra
     tables in order to do optimisations
  """
  def getTitle(self):
    return "Optimised Milestone Reporting"

  def getBusinessTemplateList(self):
    """Returns list of BT to be installed."""
    return self.business_template_list + ('erp5_project_mysql_innodb_catalog',)

  def testMilestoneReport(self):
    self.checkMilestoneReport(optimised=True)