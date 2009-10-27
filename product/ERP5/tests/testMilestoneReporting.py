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
from Products.ERP5Type.tests.utils import reindex
import transaction
from DateTime import DateTime

class TestMilestoneReporting(ERP5ReportTestCase):
  """Test Milestone Reporting

     This report is able to display all milestones from many projects,
     it supports start and stop dates parameters
  """
  def getTitle(self):
    return "Milestone Reporting"

  def getBusinessTemplateList(self):
    """Returns list of BT to be installed."""
    return ('erp5_base','erp5_pdm', 'erp5_trade', 'erp5_project',)

  @reindex
  def _makeOneMilestone(self, project_title, **kw):
    """Create a task, support many options"""
    project_module = self.portal.project_module
    project_list = [x for x in self.portal.portal_catalog(
                    portal_type='Project', title=project_title)]
    if len(project_list):
      project = project_list[0]
    else:
      project = project_module.newContent(portal_type='Project',
                  title=project_title)
    task = project.newContent(portal_type='Project Milestone', **kw)

  def afterSetUp(self):
    """Setup the fixture.
    """
    self.portal = self.getPortal()

  def getDataLineLineListByCallingMilestoneReport(self,
      from_date=None, at_date=None):
    request = self.portal.REQUEST
    request.form['from_date'] = from_date
    request.form['at_date'] = at_date
    # call the report first, it will set selection
    report_html = \
        self.portal.project_module.ProjectModule_generateMilestoneReport(
             from_date=from_date, at_date=at_date)
    self.failIf('Site Error' in report_html)

    line_list = self.portal.sale_order_module.\
        ProjectModule_viewMilestoneReport.listbox.\
        get_value('default',
                  render_format='list', REQUEST=request)
    data_line_list = [l for l in line_list if l.isDataLine()]
    return data_line_list

  def testMilestoneReport(self):
    """
    Check monthly report available on project
    """
    # Create Tasks
    self._makeOneMilestone(
              project_title='Foo',
              title='Foo Milestone A',
              start_date=DateTime('2009/10/01'),
              stop_date=DateTime('2009/10/27'),
              )


    # We should have this result
    # Project    Milestone         Stop Date
    # Foo        Foo Milestone A   2009/10/27
    data_line_list = self.getDataLineLineListByCallingMilestoneReport(
        from_date=DateTime('2009/10/01'), at_date=DateTime('2009/10/31'))
    self.assertEquals(1, len(data_line_list))
    self.checkLineProperties(data_line_list[0],
                             project_title='Foo',
                             milestone_title='Foo Milestone A',
                             stop_date=DateTime('2009/10/27'))

    # Add other tasks, some of them in another project
    self._makeOneMilestone(
              project_title='Foo',
              title='Foo Milestone B',
              start_date=DateTime('2009/09/01'),
              stop_date=DateTime('2009/09/27'),
              )
    self._makeOneMilestone(
              project_title='Bar',
              title='Bar Milestone A',
              start_date=DateTime('2009/05/01'),
              stop_date=DateTime('2009/05/27'),
              )
    self._makeOneMilestone(
              project_title='Bar',
              title='Bar Milestone B',
              start_date=DateTime('2009/07/01'),
              stop_date=DateTime('2009/07/27'),
              )

    # if we keep same dates as first call, the result should not change
    # (this checks that dates are well taken into account)
    data_line_list = self.getDataLineLineListByCallingMilestoneReport(
        from_date=DateTime('2009/10/01'), at_date=DateTime('2009/10/31'))
    self.assertEquals(1, len(data_line_list))
    self.checkLineProperties(data_line_list[0],
                             project_title='Foo',
                             milestone_title='Foo Milestone A',
                             stop_date=DateTime('2009/10/27'))

    # No use larger range of dates in order to check all milestones
    # This will check that milestones are well ordered by dates and
    # project names
    data_line_list = self.getDataLineLineListByCallingMilestoneReport(
        from_date=DateTime('2009/01/01'), at_date=DateTime('2009/12/31'))
    self.assertEquals(4, len(data_line_list))
    self.checkLineProperties(data_line_list[0],
                             project_title='Bar',
                             milestone_title='Bar Milestone A',
                             stop_date=DateTime('2009/05/27'))
    self.checkLineProperties(data_line_list[1],
                             project_title='Bar',
                             milestone_title='Bar Milestone B',
                             stop_date=DateTime('2009/07/27'))
    self.checkLineProperties(data_line_list[2],
                             project_title='Foo',
                             milestone_title='Foo Milestone B',
                             stop_date=DateTime('2009/09/27'))
    self.checkLineProperties(data_line_list[3],
                             project_title='Foo',
                             milestone_title='Foo Milestone A',
                             stop_date=DateTime('2009/10/27'))
