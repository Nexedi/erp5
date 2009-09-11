#############################################################################
#
# Copyright  2009 Nexedi SA Contributors. All Rights Reserved.
#             Rafael Monnerat <rafael@nexedi.com>
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


import unittest

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
import transaction
from DateTime import DateTime

class TestProject(ERP5TypeTestCase):
  """ Test for Project API and scripts and forms 
      used for Project Document.
  """
  def getTitle(self):
    return "Project"

  def getBusinessTemplateList(self):
    """Returns list of BT to be installed."""
    return ('erp5_base', 
            'erp5_pdm', 
            'erp5_trade', 
            'erp5_project',)

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
                              title='Organisation_1',
                              id='Organisation_1')

    # create organisations
    if not self.portal.organisation_module.has_key('Organisation_2'):
      org = self.portal.organisation_module.newContent(
                              title='Organisation_2',
                              id='Organisation_2')
    # create project
    if not self.portal.project_module.has_key('Project_1'):
      project = self.portal.project_module.newContent(
                              portal_type='Project',
                              reference='Project_1',
                              title='Project_1',
                              id='Project_1')

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

  def testProject_getSourceProjectRelatedTaskReportList(self):
    """
     Basic Test if the script behaviour as expected.
    """
    # Create Tasks
    task_module = self.getPortalObject().task_module
    project = self.getPortalObject().project_module.Project_1

    task = task_module.newContent(portal_type='Task',
              title='Task 1',
              task_line_quantity=3,
              resource='product_module/development',
              source='organisation_module/Organisation_1',
              source_section='organisation_module/Organisation_1',
              destination='organisation_module/Organisation_2',
              destination_section='organisation_module/Organisation_2',
              source_project='project_module/Project_1',
              start_date=DateTime('2009/07/23'),
              stop_date=DateTime('2009/07/26'),
              )

    self.stepTic()
    task.plan()
    
    self.stepTic()
    # Script Used for Task Tab
    task_line_list = project.Project_getSourceProjectRelatedTaskList()
    self.assertEquals(1, len(task_line_list))
    self.assertEquals(task_line_list[0], task.default_task_line)
 
    # Script Used for Task Report Tab
    # It shows planned tasks also.
    task_line_list = project.Project_getSourceProjectRelatedTaskReportList()
    self.assertEquals(1, len(task_line_list))
    self.assertEquals(task_line_list[0], task.default_task_line)

    task.confirm()
    self.stepTic()

    # Script Used for Task Tab keep only showing tasks.
    task_line_list = project.Project_getSourceProjectRelatedTaskList()
    self.assertEquals(1, len(task_line_list))
    self.assertEquals(task_line_list[0], task.default_task_line)
 
    # Script Used for Task Report Tab
    # It shows planned tasks also.
    task_line_list = project.Project_getSourceProjectRelatedTaskReportList()
    self.assertEquals(1, len(task_line_list))
    self.assertNotEquals(task_line_list[0], task.default_task_line)
    self.assertNotEquals(task_line_list[0].getCausalityRelatedValue(), 
                           task.default_task_line)

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestProject))
  return suite
