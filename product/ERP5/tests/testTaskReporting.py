#############################################################################
#
# Copyright  2008 Nexedi SA Contributors. All Rights Reserved.
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

class TestTaskReporting(ERP5ReportTestCase):
  """Test Task Reporting
  """
  def getTitle(self):
    return "Task Reporting"

  def getBusinessTemplateList(self):
    """Returns list of BT to be installed."""
    return ('erp5_base','erp5_pdm', 'erp5_trade', 'erp5_project',)

  @reindex
  def _makeOneTask(self, simulation_state='planned', **kw):
    """Create a task, support many options"""
    task_module = self.getPortalObject().task_module
    task = task_module.newContent(portal_type='Task', **kw)
    if simulation_state == 'planned':
      task.plan()
    if simulation_state == 'confirmed':
      task.confirm()

  def afterSetUp(self):
    """Setup the fixture.
    """
    self.portal = self.getPortal()

    for rule_id in ['default_order_rule', 'default_delivery_rule']:
      rule = getattr(self.portal.portal_rules, rule_id)
      if rule.getValidationState() == 'draft':
        rule.validate()

    # create organisations
    if not self.portal.organisation_module.has_key('Organisation_1'):
      org = self.portal.organisation_module.newContent(
                              portal_type='Organisation',
                              reference='Organisation_1',
                              title='Organisation_1',
                              id='Organisation_1')

    if not self.portal.organisation_module.has_key('Organisation_2'):
      org = self.portal.organisation_module.newContent(
                              portal_type='Organisation',
                              reference='Organisation_2',
                              title='Organisation_2',
                              id='Organisation_2')

    # create persons
    if not self.portal.organisation_module.has_key('Person_1'):
      org = self.portal.person_module.newContent(
                              portal_type='Person',
                              reference='Person_1',
                              title='Person_1',
                              id='Person_1')
    if not self.portal.organisation_module.has_key('Person_2'):
      org = self.portal.person_module.newContent(
                              portal_type='Person',
                              reference='Person_2',
                              title='Person_2',
                              id='Person_2')

    # create project
    if not self.portal.project_module.has_key('Project_1'):
      project = self.portal.project_module.newContent(
                              portal_type='Project',
                              reference='Project_1',
                              title='Project_1',
                              start_date=DateTime('2009/01/01'),
                              stop_date=DateTime('2009/12/31'),
                              id='Project_1')
      project.newContent(portal_type='Project Line',
                         id='Line_1',
                         title='Line_1')
      project.newContent(portal_type='Project Line',
                         id='Line_2',
                         title='Line_2')
    if not self.portal.organisation_module.has_key('Project_2'):
      project = self.portal.project_module.newContent(
                              portal_type='Project',
                              reference='Project_2',
                              title='Project_2',
                              start_date=DateTime('2009/01/01'),
                              stop_date=DateTime('2009/12/31'),
                              id='Project_2')

    # create unit categories
    for unit_id in ('day', 'hour',):
      if not self.portal.portal_categories['quantity_unit'].has_key(unit_id):
        self.portal.portal_categories.quantity_unit.newContent(
                                  portal_type='Category',
                                  title=unit_id.title(),
                                  reference=unit_id,
                                  id=unit_id)

    # Create resources
    module = self.portal.product_module
    if not module.has_key('development'):
      product = module.newContent(
          portal_type='Product',
          id='development',
          title='Development',
          reference='ref 1',
          quantity_unit='unit'
          )
    if not module.has_key('consulting'):
      product = module.newContent(
          portal_type='Product',
          id='consulting',
          title='Consulting',
          reference='ref 2',
          quantity_unit='unit'
          )

    # and all this available to catalog
    transaction.commit()
    self.tic()

  def beforeTearDown(self):
    """Remove all documents.
    """
    transaction.abort()

    portal = self.getPortal()
    portal.task_module.manage_delObjects(
                      list(portal.task_module.objectIds()))
    portal.task_report_module.manage_delObjects(
                      list(portal.task_report_module.objectIds()))
    portal.portal_simulation.manage_delObjects(
                      list(portal.portal_simulation.objectIds()))

    transaction.commit()
    self.tic()

  def testProjectMontlyReport(self):
    """
    Check monthly report available on project
    """
    # Create Tasks
    self._makeOneTask(
              title='Task 1',
              task_line_quantity=3,
              resource='product_module/development',
              source='person_module/Person_1',
              source_section='organisation_module/Organisation_1',
              destination='organisation_module/Organisation_2',
              destination_section='organisation_module/Organisation_2',
              source_project='project_module/Project_1/Line_1',
              start_date=DateTime('2009/07/23'),
              stop_date=DateTime('2009/07/26'),
              )

    request = self.portal.REQUEST
    request['from_date'] = DateTime('2009/07/01')
    request['at_date'] = DateTime('2009/07/31')
    request['report_depth'] = 5
    report_section_list = self.getReportSectionList(
        self.portal.project_module.Project_1,
        'Project_viewMonthlyReport')
    self.assertEquals(1, len(report_section_list))

    line_list = self.getListBoxLineList(report_section_list[0])
    data_line_list = [l for l in line_list if l.isDataLine()]
    self.assertEquals(2, len(data_line_list))
    self.checkLineProperties(data_line_list[0],
                   **{'person_module/Person_1': 3.0,
                      })
    self.checkLineProperties(data_line_list[1],
                   **{'person_module/Person_1': 3.0,
                      })

    request = self.portal.REQUEST
    request.form['from_date'] = DateTime('2009/07/01')
    request.form['at_date'] = DateTime('2009/07/30')
    request.form['report_depth'] = 5
    report_section_list = self.getReportSectionList(
        self.portal.project_module.Project_1,
        'Project_viewMonthlyReport')
    self.assertEquals(1, len(report_section_list))

    # We should have this result
    # month             Person1
    # 2009-07             3
    #   Project1/Line1    3
    line_list = self.getListBoxLineList(report_section_list[0])
    data_line_list = [l for l in line_list if l.isDataLine()]
    self.assertEquals(2, len(data_line_list))
    self.checkLineProperties(data_line_list[0],
                   **{'person_module/Person_1': 3.0,
                      })
    self.checkLineProperties(data_line_list[1],
                   **{'person_module/Person_1': 3.0,
                      })
    # Create Tasks
    self._makeOneTask(
              title='Task 2',
              task_line_quantity=5,
              resource='product_module/development',
              source='person_module/Person_1',
              source_section='organisation_module/Organisation_1',
              destination='organisation_module/Organisation_2',
              destination_section='organisation_module/Organisation_2',
              source_project='project_module/Project_1/Line_2',
              start_date=DateTime('2009/08/02'),
              stop_date=DateTime('2009/08/07'),
              )
    self._makeOneTask(
              title='Task 3',
              task_line_quantity=7,
              resource='product_module/development',
              source='person_module/Person_1',
              source_section='organisation_module/Organisation_1',
              destination='organisation_module/Organisation_2',
              destination_section='organisation_module/Organisation_2',
              source_project='project_module/Project_1/Line_2',
              start_date=DateTime('2009/08/20'),
              stop_date=DateTime('2009/08/30'),
              simulation_state='confirmed',
              )
    self._makeOneTask(
              title='Task 4',
              task_line_quantity=11,
              resource='product_module/development',
              source='person_module/Person_1',
              source_section='organisation_module/Organisation_1',
              destination='organisation_module/Organisation_2',
              destination_section='organisation_module/Organisation_2',
              source_project='project_module/Project_1/Line_1',
              start_date=DateTime('2009/08/20'),
              stop_date=DateTime('2009/08/30'),
              simulation_state='confirmed',
              )
    # And also a task splitted between two months
    self._makeOneTask(
              title='Task 5',
              task_line_quantity=13,
              resource='product_module/development',
              source='person_module/Person_2',
              source_section='organisation_module/Organisation_1',
              destination='organisation_module/Organisation_2',
              destination_section='organisation_module/Organisation_2',
              source_project='project_module/Project_1/Line_2',
              start_date=DateTime('2009/07/01'),
              stop_date=DateTime('2009/08/31'),
              )

    # We should have this result
    # month             Person1  Person2
    # 2009-07             3         6.5
    #   Project1/Line1    3         0
    #   Project1/Line2    0         6.5
    # 2009-08             23        6.5
    #   Project1/Line2    11        0
    #   Project1/Line2    12        6.5
    # 2009-09             0         0
    request = self.portal.REQUEST
    request['from_date'] = DateTime('2009/07/01')
    request['at_date'] = DateTime('2009/09/30')
    request['report_depth'] = 5
    request.form['month_dict'] = None
    report_section_list = self.getReportSectionList(
        self.portal.project_module.Project_1,
        'Project_viewMonthlyReport')
    self.assertEquals(1, len(report_section_list))

    line_list = self.getListBoxLineList(report_section_list[0])
    data_line_list = [l for l in line_list if l.isDataLine()]
    self.assertEquals(7, len(data_line_list))
    self.checkLineProperties(data_line_list[0],
                   **{'person_module/Person_1': 3.0,
                      'person_module/Person_2': 6.5,
                      })
    self.checkLineProperties(data_line_list[1],
                   **{'person_module/Person_1': 3.0,
                      'person_module/Person_2': None,
                      })
    self.checkLineProperties(data_line_list[2],
                   **{'person_module/Person_1': None,
                      'person_module/Person_2': 6.5,
                      })
    self.checkLineProperties(data_line_list[3],
                   **{'person_module/Person_1': 23,
                      'person_module/Person_2': 6.5,
                      })
    self.checkLineProperties(data_line_list[4],
                   **{'person_module/Person_1': 11,
                      'person_module/Person_2': None,
                      })
    self.checkLineProperties(data_line_list[5],
                   **{'person_module/Person_1': 12,
                      'person_module/Person_2': 6.5,
                      })
    self.checkLineProperties(data_line_list[6],
                   **{'person_module/Person_1': None,
                      'person_module/Person_2': None,
                      })
