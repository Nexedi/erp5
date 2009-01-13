##############################################################################
#
# Copyright (c) 2007 Nexedi SA and Contributors. All Rights Reserved.
#         Mikolaj Antoszkiewicz <mikolaj@erp5.pl> 
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
from AccessControl.SecurityManagement import newSecurityManager
from DateTime import DateTime
from zLOG import LOG
from Products.ERP5Type.tests.Sequence import SequenceList
from Products.CMFCore.utils import getToolByName
from Testing import ZopeTestCase
from Testing.ZopeTestCase.PortalTestCase import PortalTestCase

class TestTaskMixin:

  default_quantity = 99.99999999
  default_price = 555.88888888
  person_portal_type = 'Person'
  organisation_portal_type = 'Organisation'
  resource_portal_type = 'Service'
  project_portal_type = 'Project'
  requirement_portal_type = 'Requirement'
  requirement_document_portal_type = 'Requirement Document'
  task_portal_type = 'Task'
  task_description = 'Task Description %s'
  task_line_portal_type = 'Task Line'
  task_report_portal_type = 'Task Report'
  task_report_line_portal_type = 'Task Report Line'
  datetime = DateTime()
  task_workflow_id='task_workflow'

  default_task_sequence = '\
                       stepLogin \
                       stepCreateOrganisation \
                       stepCreateOrganisation \
                       stepCreateResource \
                       stepCreateProject \
                       stepCreateRequirement \
                       stepCreateSimpleTask \
                       stepCreateCurrency \
                       stepFillTaskWithData \
                       stepSetTaskPriceCurrency \
                       stepConfirmTask \
                       stepTic \
                       stepSetTaskReport '

  default_task_sequence_two_lines = '\
                       stepLogin \
                       stepCreateOrganisation \
                       stepCreateOrganisation \
                       stepCreateResource \
                       stepCreateResource \
                       stepCreateProject \
                       stepCreateSimpleTask \
                       stepCreateCurrency \
                       stepFillTaskWithData \
                       stepSetTaskPriceCurrency \
                       stepCreateTaskLine \
                       stepFillTaskLineWithData \
                       stepConfirmTask \
                       stepTic \
                       stepSetTaskReport '
                       
  default_task_report_sequence = '\
                       stepLogin \
                       stepCreateOrganisation \
                       stepCreateOrganisation \
                       stepCreateResource \
                       stepCreateSimpleTaskReport \
                       stepCreateCurrency \
                       stepFillTaskReportWithData \
                       stepSetTaskReportPriceCurrency \
                       stepCreateTaskReportLine '

  login = PortalTestCase.login

  def getBusinessTemplateList(self):
    """
    """
    return ('erp5_base','erp5_pdm', 'erp5_trade', 'erp5_project',)

#  def stepLogin(self, **kw):
#    portal = self.getPortal()
#    uf = portal.acl_users
#    if not uf.getUser('dummy'):
#      uf._doAddUser('manager', '', ['Manager'], [])
#      self.login('manager')
#      person_module = portal.getDefaultModule(self.person_portal_type)
#      person = person_module.newContent(id='dummy', title='dummy',
#                                        reference='dummy')
#      portal.portal_categories.group.newContent(id='dummy',
#                                                codification='DUMMY')
#      
#      assignment = person.newContent(title='dummy', group='dummy',
#                                     portal_type='Assignment',
#                                     start_date='1980-01-01',
#                                     stop_date='2099-12-31')
#      assignment.open()
#      get_transaction().commit()
#      self.tic()
#      module_list = []
#      portal_type_list = []
#      for portal_type in (self.resource_portal_type,
#                          self.project_portal_type,
#                          self.requirement_document_portal_type,
#                          self.organisation_portal_type,
#                          self.task_portal_type,
#                          self.task_report_portal_type,
#                          self.category_portal_type,):
#        module = portal.getDefaultModule(portal_type)
#        module_list.append(module)
#        portal_type_list.append(portal_type)
#        portal_type_list.append(module.getPortalType())
#
#      for portal_type in portal_type_list:
#        ti = portal.portal_types[portal_type]
#        ti.addRole('Auditor;Author;Assignee;Assignor', '', 'Dummy',
#                   '', 'group/dummy', 'ERP5Type_getSecurityCategoryFromAssignment',
#                   '')
#        ti.updateRoleMapping()
#
#      get_transaction().commit()
#      self.tic()
#      portal.portal_caches.clearAllCache()
#
#    self.login('dummy')
  def stepLogin(self, quiet=0, run=1, **kw):
    uf = self.getPortal().acl_users
    uf._doAddUser('alex', '', ['Manager', 'Assignee', 'Assignor',
                               'Associate', 'Auditor', 'Author'], [])
    user = uf.getUserById('alex').__of__(uf)
    newSecurityManager(None, user)

  def stepTic(self, **kw):
    self.tic()

  def stepCreateResource(self,sequence=None, sequence_list=None, \
                                    **kw):
    """
      Create a resource_list with no variation
    """
    resource_list = sequence.get('resource_list', [])
    portal = self.getPortal()
    resource_module = portal.getDefaultModule(self.resource_portal_type)
    resource = resource_module.newContent(
        portal_type=self.resource_portal_type,
        title = 'Resource%s' % len(resource_list),
    )
    resource_list.append(resource)
    sequence.edit(resource_list=resource_list)

  def stepCreateProject(self,sequence=None, sequence_list=None, \
                        **kw):
    """
    Create a project
    """
    portal = self.getPortal()
    module = portal.getDefaultModule(self.project_portal_type)
    obj = module.newContent(
        portal_type=self.project_portal_type,
        title = 'Project',
    )
    sequence.edit(project=obj)

  def stepCreateRequirement(self,sequence=None, sequence_list=None, \
                            **kw):
    """
    Create a requirement
    """
    portal = self.getPortal()
    module = portal.getDefaultModule(self.requirement_document_portal_type)
    obj = module.newContent(
        portal_type=self.requirement_document_portal_type,
        title = 'Requirement Document',
    )
    subobj = obj.newContent(
        portal_type=self.requirement_portal_type,
        title = 'Requirement',
    )
    sequence.edit(requirement=subobj)

  def stepCreateOrganisation(self, sequence=None, sequence_list=None, **kw):
    """
      Create a empty organisation
    """
    organisation_list = sequence.get('organisation_list', [])
    portal = self.getPortal()
    organisation_module = portal.getDefaultModule(
                                   portal_type=self.organisation_portal_type)
    organisation = organisation_module.newContent(
                        portal_type=self.organisation_portal_type,
                        title='Organization%s' % len(organisation_list),
    )
    organisation_list.append(organisation)
    sequence.edit(organisation_list=organisation_list)

  def stepCreateSimpleTask(self,sequence=None, sequence_list=None, **kw):
    """
      Create a task and fill it with dummy data.
    """
    portal = self.getPortal()
    task_module = portal.getDefaultModule(portal_type=self.task_portal_type)
    task = task_module.newContent(portal_type=self.task_portal_type)
    # Check if no task lines are created at the start
    self.assertEquals(len(task.contentValues()), 0)
    task.edit(
      title = "Task",
    )
    sequence.edit(task=task)

  def stepCreateCurrency(self, sequence, **kw) :
    """Create a default currency. """
    currency_module = self.getCurrencyModule()
    if len(currency_module.objectValues(id='EUR'))==0:
      currency = self.getCurrencyModule().newContent(
          portal_type='Currency',
          id="EUR",
          base_unit_quantity=0.01,
          )
    else:
      currency = currency_module.objectValues(id='EUR')[0]
    sequence.edit(currency=currency)
 
  def stepSetTaskPriceCurrency(self, sequence, **kw) :
    """Set the price currency of the task.

    This step is not necessary.
    TODO : - include a test without this step.
           - include a test with this step late.
    """
    currency = sequence.get('currency')
    task = sequence.get('task')
    task.setPriceCurrency(currency.getRelativeUrl())

  def stepSetTaskValues(self, sequence=None, sequence_list=None, **kw):
    """
    Fill created task with some necessary data.
    """
    task = sequence.get('task')
    project = sequence.get('project')
    resource = sequence.get('resource_list')[0]
    organisation_list = sequence.get('organisation_list')
    organisation1 = organisation_list[0]
    organisation2 = organisation_list[1]
    task.edit(source_value=organisation1,
              source_section_value=organisation1,
              destination_value=organisation2,
              destination_section_value=organisation2,
              source_project_value=project,
              description=self.task_description % task.getId(),
              start_date = self.datetime + 10,
              stop_date = self.datetime + 20,)
    sequence.edit( task = task)

  def stepFillTaskWithData(self, sequence=None, sequence_list=None, **kw):
    """
      Fill created task with some necessary data.
    """
    self.stepSetTaskValues(sequence=sequence, 
                           sequence_list=sequence_list, **kw)
    task = sequence.get('task')
    resource = sequence.get('resource_list')[0]
    requirement = sequence.get('requirement')
    task.edit(task_line_resource_value = resource,
              task_line_quantity = self.default_quantity,
              task_line_price = self.default_price,
              task_line_requirement_value = requirement,
    )

  def stepCloneTask(self, sequence=None, sequence_list=None, **kw):
    """
      Clone task from sequence
    """
    task = sequence.get('task')
    new_task = task.Base_createCloneDocument(batch_mode=1)
    sequence.set('task', new_task)

  def stepCreateSimpleTaskReport(self,sequence=None, sequence_list=None, **kw):
    """
      Create a task report.
    """
    portal = self.getPortal()
    task_report_module = portal.getDefaultModule(
                                    portal_type=self.task_report_portal_type)
    task_report = task_report_module.newContent(
                                    portal_type=self.task_report_portal_type)
    # Check if no task lines are created at the start
    self.assertEquals(len(task_report.contentValues()), 0)
    task_report.edit(
      title = "Task Report",
    )
    sequence.edit(task_report = task_report)

  def stepFillTaskReportWithData(self, sequence=None, sequence_list=None, **kw):
    """
      Fill created task report with some necessary data.
    """
    task_report = sequence.get('task_report')
    organisation_list = sequence.get('organisation_list')
    organisation1 = organisation_list[0]
    organisation2 = organisation_list[1]
    task_report.edit(source_value=organisation1,
                 source_section_value=organisation1,
                 destination_value=organisation1,
                 destination_section_value=organisation2,
                 start_date = self.datetime + 10,
                 stop_date = self.datetime + 20,)
    sequence.edit( task_report = task_report)

  def stepSetTaskReportPriceCurrency(self, sequence, **kw) :
    """Set the price currency of the task.

    This step is not necessary.
    TODO : - include a test without this step.
           - include a test with this step late.
    """
    currency = sequence.get('currency')
    task_report = sequence.get('task_report')
    task_report.setPriceCurrency(currency.getRelativeUrl())

  def stepCreateTaskReportLine(self, sequence=None, sequence_list=None, **kw):
    """
      Create task report line and fill with dummy data.
    """
    resource = sequence.get('resource_list')[0]
    portal = self.getPortal()
    task_report = sequence.get('task_report')
    task_report_line = task_report.newContent(
                             portal_type=self.task_report_line_portal_type)
    task_report_line.edit( title = 'New Task Report Line',
                    resource_value = resource,
                    quantity = self.default_quantity,
                    price = self.default_price)
    sequence.edit(task_report_line = task_report_line)

  def stepVerifyGeneratedByBuilderTaskReport(self, sequence=None,
                                                    sequence_list=None, **kw):
    """
    Verify that simulation generated report is correct.
    """
    task = sequence.get('task')
    task_report = sequence.get('task_report')
    self.assertEquals('confirmed', task_report.getSimulationState())
    self.assertEquals(task.getSource(), task_report.getSource())
    self.assertEquals(task.getSourceSection(), task_report.getSourceSection())
    self.assertEquals(task.getSourceProject(), task_report.getSourceProject())
    self.assertEquals(task.getDestination(), task_report.getDestination())
    self.assertEquals(task.getDestinationSection(),
                      task_report.getDestinationSection())
    self.assertEquals(task.getDestinationDecision(),
                      task_report.getDestinationDecision())
    self.assertEquals(task.getTitle(),
                      task_report.getTitle())
    self.assertEquals(task.getDescription(),
                      task_report.getDescription())
    self.assertEquals(task.getPredecessor(), task_report.getPredecessor())
    self.assertEquals(task.getDescription(), task_report.getDescription())
    self.assertEquals(task.getPriceCurrency(), task_report.getPriceCurrency())
    self.assertEquals(len(task_report.contentValues()), 1)
    task_report_line = task_report.contentValues()[0]
    self.assertEquals(task.getTaskLineResource(), task_report_line.getResource())
    self.assertEquals(task.getTaskLineQuantity(), task_report_line.getQuantity())
    self.assertEquals(task.getTaskLinePrice(), task_report_line.getPrice())
    self.assertEquals(task.getTaskLineRequirement(), 
                      task_report_line.getRequirement())


  def stepVerifyClonedGeneratedByBuilderTaskReport(self, sequence=None,
                                                    sequence_list=None, **kw):
    """
    Verify that simulation generated report is correct.
    """
    task = sequence.get('task')
    task_report = sequence.get('task_report')
    self.assertEquals('confirmed', task_report.getSimulationState())
    self.assertEquals(task.getSource(), task_report.getSource())
    self.assertEquals(task.getSourceSection(), task_report.getSourceSection())
    self.assertEquals(task.getSourceProject(), task_report.getSourceProject())
    self.assertEquals(task.getDestination(), task_report.getDestination())
    self.assertEquals(task.getDestinationSection(),
                      task_report.getDestinationSection())
    self.assertEquals(task.getDestinationDecision(),
                      task_report.getDestinationDecision())
    self.assertEquals(task.getTitle(),
                      task_report.getTitle())
    self.assertEquals(task.getDescription(),
                      task_report.getDescription())
    self.assertEquals(task.getPredecessor(), task_report.getPredecessor())
    self.assertEquals(task.getDescription(), task_report.getDescription())
    self.assertEquals(task.getPriceCurrency(), task_report.getPriceCurrency())
    self.assertEquals(len(task_report.contentValues()), 1)
    task_report_line = task_report.contentValues()[0]
    self.assertEquals(task.getTaskLineResource(), task_report_line.getResource())
    self.assertEquals(task.getTaskLineQuantity(), task_report_line.getQuantity()*2)
    self.assertEquals(task.getTaskLinePrice(), task_report_line.getPrice())
    self.assertEquals(task.getTaskLineRequirement(), 
                      task_report_line.getRequirement())

  def stepCreateTaskLine(self, sequence=None, sequence_list=None, **kw):
    """
      Create task line and fill with dummy data.
    """
    task = sequence.get('task')
    task_line = task.newContent(
        portal_type=self.task_line_portal_type,
        title='New Task Line')
    sequence.edit(task_line=task_line)

  def stepFillTaskLineWithData(self, sequence=None, sequence_list=None, **kw):
    """
    Fill task line with dummy data.
    """
    organisation = sequence.get('organisation_list')[0]
    resource1 = sequence.get('resource_list')[1]
    task_line = sequence.get('task_line')
    task_line.edit(
        source_value=organisation,
        resource_value=resource1,
        quantity=self.default_quantity,
        price=self.default_price)
  
  def stepVerifyGeneratedTaskReportLines(self, sequence=None,
                                         sequence_list=None, **kw):
    """
      Verify that simulation generated report is correct.
    """
    task = sequence.get('task')
    task_report = sequence.get('task_report') 
    task_content_list = task.contentValues()
    self.assertNotEquals(len(task_content_list), 0)
    self.assertEquals(len(task_report.contentValues()),
                      len(task_content_list))

    # Task report values not tested
    # XXX
    # Task line not precisely tested
    for task_line in task_content_list:
        task_report_resource_list = \
            [line.getResource() for line in task_report.contentValues()]
        task_report_quantity_list = \
            [line.getQuantity() for line in task_report.contentValues()]
        task_report_price_list = \
            [line.getPrice() for line in task_report.contentValues()]
        self.assertTrue(task_line.getResource() in task_report_resource_list)
        self.assertTrue(task_line.getQuantity() in task_report_quantity_list)
        self.assertTrue(task_line.getPrice() in task_report_price_list)

  def stepVerifyTaskReportCausalityState(self, sequence=None,
                                         sequence_list=None, **kw):
    """
      Verify that confirmed task report starts building and gets solved.
    """
    task_report = sequence.get('task_report')
    self.assertEqual(task_report.getCausalityState(), 'solved')

  def modifyState(self, object_name, transition_name, sequence=None,
                       sequence_list=None):
    object_value = sequence.get(object_name)
    workflow_method = getattr(object_value, transition_name)
    workflow_method()

  def stepConfirmTask(self, sequence=None, sequence_list=None, **kw):
    self.modifyState('task', 'confirm', sequence=sequence)
  
  def stepConfirmTaskReport(self, sequence=None, sequence_list=None, **kw):
    self.modifyState('task_report', 'confirm', sequence=sequence)
  
  def stepStartTaskReport(self, sequence=None, sequence_list=None, **kw):
    self.modifyState('task_report', 'start', sequence=sequence)

  def stepFinishTaskReport(self, sequence=None, sequence_list=None, **kw):
    self.modifyState('task_report', 'stop', sequence=sequence)

  def stepCloseTaskReport(self, sequence=None, sequence_list=None, **kw):
    self.modifyState('task_report', 'deliver', sequence=sequence)

  def stepRestartTaskReport(self, sequence=None, sequence_list=None, **kw):
    self.modifyState('task_report', 'restart', sequence=sequence)
  
  def stepSetTaskReport(self, sequence=None, sequence_list=None, **kw):
    """
      Set task report object in sequence.
    """
    task = sequence.get('task')
    task_report = task.getCausalityRelatedValueList(
                                                portal_type='Task Report')[0]
    sequence.edit(task_report=task_report)

  def stepVerifyMergedTaskLine(self, sequence=None,
                               sequence_list=None, **kw):
    """
    Verify that simulation generated report is correct.
    """
    task = sequence.get('task')
    task_report = sequence.get('task_report')
    self.assertEquals('confirmed', task_report.getSimulationState())
    self.assertEquals(task.getSource(), task_report.getSource())
    self.assertEquals(task.getSourceSection(), task_report.getSourceSection())
    self.assertEquals(task.getSourceProject(), task_report.getSourceProject())
    self.assertEquals(task.getDestination(), task_report.getDestination())
    self.assertEquals(task.getDestinationSection(),
                      task_report.getDestinationSection())
    self.assertEquals(task.getDestinationDecision(),
                      task_report.getDestinationDecision())
    self.assertEquals(task.getTitle(),
                      task_report.getTitle())
    self.assertEquals(task.getDescription(),
                      task_report.getDescription())
    self.assertEquals(task.getPredecessor(), task_report.getPredecessor())
    self.assertEquals(task.getDescription(), task_report.getDescription())
    self.assertEquals(len(task_report.contentValues()), 2)
    for task_report_line in task_report.contentValues():
      self.assertEquals(task.contentValues()[0].getResource(), 
                        task_report_line.getResource())
      self.assertEquals(task.contentValues()[0].getQuantity(), 
                        task_report_line.getQuantity())
      self.assertEquals(task.contentValues()[0].getPrice(), 
                        task_report_line.getPrice())
      self.assertEquals(task.contentValues()[0].getRequirement(), 
                        task_report_line.getRequirement())

class TestTask(TestTaskMixin, ERP5TypeTestCase):
  """
    Test task behaviour.
  """
  run_all_test = 1

  def getTitle(self):
    return "Task"

  def enableLightInstall(self):
    """
    You can override this.
    Return if we should do a light install (1) or not (0)
    """
    return 1

  def enableActivityTool(self):
    """
    You can override this.
    Return if we should create (1) or not (0) an activity tool.
    """
    return 1

  def test_01_testTaskBasicUseCase(self, quiet=0, run=run_all_test):
    """
      Test creation of task and (automatic) task_report
    """
    if not run: return
    sequence_list = SequenceList()
    sequence_string = self.default_task_sequence + '\
                       stepVerifyGeneratedByBuilderTaskReport \
                       stepStartTaskReport \
                       stepFinishTaskReport \
                       stepCloseTaskReport \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_02_testMultipleLineTaskBasicUseCase(self, quiet=0, run=run_all_test):
    """
      Test creation of task with multiple task lines \
      and (automatic) creation of task_report.
    """
    if not run: return
    sequence_list = SequenceList()
    sequence_string = self.default_task_sequence_two_lines + '\
                       stepVerifyGeneratedTaskReportLines \
                       stepStartTaskReport \
                       stepFinishTaskReport \
                       stepCloseTaskReport \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_03_testTaskReportBasicUseCase(self, quiet=0, run=run_all_test):
    """
      Test creation of task report and task report lines. 
    """
    if not run: return
    sequence_list = SequenceList()
    sequence_string = self.default_task_report_sequence + '\
                       stepConfirmTaskReport \
                       stepTic \
                       stepVerifyTaskReportCausalityState \
                       stepStartTaskReport \
                       stepFinishTaskReport \
                       stepCloseTaskReport \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_04_checkNotMergedTaskReportLine(self, quiet=0, run=run_all_test):
    """
    Check that a task report can not be the created from a merged of multiple
    task lines.
    """
    if not run: return
    sequence_list = SequenceList()
    sequence_string = 'stepLogin \
                       stepCreateOrganisation \
                       stepCreateOrganisation \
                       stepCreateResource \
                       stepCreateResource \
                       stepCreateSimpleTask \
                       stepSetTaskValues \
                       stepCreateTaskLine \
                       stepFillTaskLineWithData \
                       stepCreateTaskLine \
                       stepFillTaskLineWithData \
                       stepConfirmTask \
                       stepTic \
                       stepSetTaskReport \
                       stepVerifyMergedTaskLine \
                       stepStartTaskReport \
                       stepFinishTaskReport \
                       stepCloseTaskReport \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_05_testStrictSimulationSecurity(self, quiet=0, run=run_all_test):
    """Test creation of task and (automatic) task_report with strict
    security in the simulation.
    """
    if not run: return
    sequence_list = SequenceList()
    sequence_string = self.default_task_sequence + '\
                       stepVerifyGeneratedByBuilderTaskReport \
                       stepStartTaskReport \
                       stepFinishTaskReport \
                       stepCloseTaskReport \
                       '
    sequence_list.addSequenceString(sequence_string)

    simulation_tool = self.getPortal().portal_simulation
    uf = self.getPortal().acl_users
    if not uf.getUser('manager'):
      uf._doAddUser('manager', '', ['Manager'], [])
    self.login('manager')
    try:
      simulation_tool.Base_setDefaultSecurity()
      self.logout()
      sequence_list.play(self)
    finally:
      self.login('manager')
      for permission in simulation_tool.possible_permissions():
        simulation_tool.manage_permission(permission, roles=(), acquire=1)
      self.logout()

  def test_06_testCloneTaskUseCase(self, quiet=0, run=run_all_test):
    """
      Test creation of cloned task and (automatic) task_report
      Check if quantity is doubled
    """
    if not run: return
    sequence_list = SequenceList()
    sequence_string = self.default_task_sequence + '\
                       CloneTask \
                       ConfirmTask \
                       Tic \
                       SetTaskReport \
                       VerifyClonedGeneratedByBuilderTaskReport \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestTask))
  return suite
