##############################################################################
#
# Copyright (c) 2007 Nexedi SA and Contributors. All Rights Reserved.
#          Mikolaj Antoszkiewicz <mikolaj@erp5.pl>
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
from Products.ERP5Type.tests.Sequence import SequenceList
from testTask import TestTaskMixin
from Products.ERP5Type.tests.backportUnittest import expectedFailure
from Products.ERP5.tests.utils import newSimulationExpectedFailure

class TestTaskReportDivergenceMixin(TestTaskMixin):
  """
    Test business template erp5_project
  """

  def getTitle(self):
    return "Task Report Divergence"

  def stepCheckTaskReportIsCalculating(self, sequence=None, sequence_list=None, **kw):
    """
      Test if task report is calculating
    """
    task_report = sequence.get('task_report')
    self.assertEquals('calculating', task_report.getCausalityState())

  def stepCheckTaskReportIsDiverged(self, sequence=None, sequence_list=None, **kw):
    """
      Test if task report is in diverged state
    """
    task_report = sequence.get('task_report')
    self.assertEquals('diverged', task_report.getCausalityState())

  def stepCheckTaskReportIsSolved(self, sequence=None, sequence_list=None, **kw):
    """
      Test if task report is in solved state
    """
    task_report = sequence.get('task_report')
    self.assertEquals('solved', task_report.getCausalityState())

  def stepChangeTaskReportLineQuantity(self, sequence=None,
      sequence_list=None, **kw):
    """
      Set a decreased quantity on task report lines.
    """
    task_report = sequence.get('task_report')
    quantity = sequence.get('line_quantity',default=self.default_quantity)
    quantity = quantity - 1
    sequence.edit(line_quantity=quantity)
    for task_report_line in task_report.objectValues(
        portal_type=self.task_report_line_portal_type):
      task_report_line.edit(quantity=quantity)
    sequence.edit(last_delta = sequence.get('last_delta', 0.0) - 1.0)

  def stepChangeTaskReportDestination(self, sequence=None, 
                                                   sequence_list=None, **kw):
    """
      Set diffrent destination organisation on task report.
    """
    organisation3 = sequence.get('organisation_list')[2]
    task_report = sequence.get('task_report')
    task_report.edit(destination_value = organisation3)

  def stepChangeTaskReportStartDate(self, sequence=None, 
                                                    sequence_list=None, **kw):
    """
      Change the start_date of the task_report.
    """
    task_report = sequence.get('task_report')
    task_report.edit(start_date=self.datetime + 15)

  def stepSetStrictSecurity(self, sequence=None, sequence_list=None, **kw):
    portal = self.getPortal()
    simulation_tool = portal.portal_simulation
    rule_tool = portal.portal_rules
    uf = self.getPortal().acl_users
    if not uf.getUser('manager'):
      uf._doAddUser('manager', '', ['Manager'], [])
    self.login('manager')
    simulation_tool.Base_setDefaultSecurity()
    rule_tool.Base_setDefaultSecurity()
    self.logout()

  def stepChangeCommentOnTaskReport(self, sequence=None, **kw):
    task_report = sequence.get('task_report')
    task_report.edit(comment='foo')
    self.assertEquals('foo', task_report.getComment())

  def stepAcceptDateDecision(self, sequence=None, **kw):
    task_report = sequence.get('task_report')
    solver_process_tool = self.portal.portal_solver_processes
    solver_process = solver_process_tool.newSolverProcess(task_report)
    solver_decision, = [x for x in solver_process.contentValues()
      if x.getCausalityValue().getTestedProperty() == 'start_date']
    # use Quantity Accept Solver.
    solver_decision.setSolverValue(self.portal.portal_solvers['Accept Solver'])
    # configure for Accept Solver.
    solver_decision.updateConfiguration(tested_property_list=['start_date'], **kw)
    solver_process.buildTargetSolverList()
    solver_process.solve()

  def stepCheckCommentStillOnTaskReport(self, sequence=None, **kw):
    """
    It already happened that the action of solving divergence
    erased the comment on the delivery. We make sure that was is
    logical (the comment remains) is true
    """
    task_report = sequence.get('task_report')
    self.assertEquals('foo', task_report.getComment())

class TestTaskReportDivergence(TestTaskReportDivergenceMixin, ERP5TypeTestCase) :

  run_all_test = 1
  quiet = 0

  def afterSetUp(self):
    self.validateRules()

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

  def test_01_TestReportLineChangeQuantity(self, quiet=quiet, run=run_all_test):
    """
      Change the quantity on an delivery line, then
      see if the task report is divergent
    """
    if not run: return
    sequence_list = SequenceList()

    sequence_string = '\
                      stepSetStrictSecurity \
                      ' + \
                      self.default_task_sequence + '\
                      stepCheckTaskReportIsSolved \
                      stepChangeTaskReportLineQuantity \
                      stepCheckTaskReportIsCalculating \
                      stepTic \
                      stepCheckTaskReportIsDiverged \
                      '
    sequence_list.addSequenceString(sequence_string)

    sequence_list.play(self, quiet=quiet)

  def test_02_TestReportListChangeDestination(self, quiet=quiet, run=run_all_test):
    """
      Test generation of delivery list
    """
    if not run: return
    sequence_list = SequenceList()

    # Test with a simply order without cell
    sequence_string = '\
                      stepSetStrictSecurity \
                      stepLogin \
                      stepCreateOrganisation ' + \
                      self.default_task_sequence + '\
                      stepCheckTaskReportIsSolved \
                      stepChangeTaskReportDestination \
                      stepCheckTaskReportIsCalculating \
                      stepTic \
                      stepCheckTaskReportIsDiverged \
                      '
    sequence_list.addSequenceString(sequence_string)

    sequence_list.play(self, quiet=quiet)

  def test_03_TaskReportChangeStartDate(self, quiet=quiet, run=run_all_test):
    """
      Test generation of delivery list
    """
    if not run: return
    sequence_list = SequenceList()

    # Test with a simply order without cell
    sequence_string = '\
                      stepSetStrictSecurity \
                      ' + self.default_task_sequence + '\
                      stepCheckTaskReportIsSolved \
                      stepChangeCommentOnTaskReport \
                      stepChangeTaskReportStartDate \
                      stepCheckTaskReportIsCalculating \
                      stepTic \
                      stepCheckTaskReportIsDiverged \
                      stepAcceptDateDecision \
                      stepTic \
                      stepCheckTaskReportIsSolved \
                      stepCheckCommentStillOnTaskReport \
                      '
    sequence_list.addSequenceString(sequence_string)

    sequence_list.play(self, quiet=quiet)

  def stepCloneTaskReportLine(self, sequence=None, **kw):
    """
    Create a second task report line by cloning the existing one.
    """
    task_report = sequence.get('task_report')
    task_report.contentValues()[0].Base_createCloneDocument(batch_mode=1)

  def stepChangeFirstTaskReportLineDate(self, sequence=None, **kw):
    """
    Change the start and stop dates on the first task report line.
    """
    task_report = sequence.get('task_report')
    task_line = task_report.contentValues()[0]
    task_line.edit(
        start_date=task_line.getStartDate()+1,
        stop_date=task_line.getStopDate()+1,
        )
    sequence.edit(
        task_report_start_date=task_report.getStartDate(),
        task_report_stop_date=task_report.getStopDate(),
        task_report_line_1_start_date=task_line.getStartDate(),
        task_report_line_1_stop_date=task_line.getStopDate(),
        )

  def stepChangeSecondTaskReportLineDate(self, sequence=None, **kw):
    """
    Change the start and stop dates on the second task report line.
    """
    task_report = sequence.get('task_report')
    task_line = task_report.contentValues()[1]
    task_line.edit(
        start_date=task_line.getStartDate()+2,
        stop_date=task_line.getStopDate()+2,
        )
    sequence.edit(
        task_report_line_2_start_date=task_line.getStartDate(),
        task_report_line_2_stop_date=task_line.getStopDate(),
        )

  def stepAcceptLineDateDecision(self, sequence=None, **kw):
    """
    Use the divergence API to adopt the decision.
    """
    task_report = sequence.get('task_report')
    # XXX Check task report solver proposition in UI

  def stepCheckTaskReportDates(self, sequence=None, **kw):
    """
    Check that the task report and task report lines's dates were not modified
    by the divergence solving process.
    """
    task_report = sequence.get('task_report')
    task_line_1 = task_report.contentValues()[0]
    task_line_2 = task_report.contentValues()[1]
    self.assertEquals(
        sequence.get('task_report_start_date'), task_report.getStartDate())
    self.assertEquals(
        sequence.get('task_report_stop_date'), task_report.getStopDate())
    self.assertEquals(
        sequence.get('task_report_line_1_start_date'), task_line_1.getStartDate())
    self.assertEquals(
        sequence.get('task_report_line_1_stop_date'), task_line_1.getStopDate())
    self.assertEquals(
        sequence.get('task_report_line_2_start_date'), task_line_2.getStartDate())
    self.assertEquals(
        sequence.get('task_report_line_2_stop_date'), task_line_2.getStopDate())

  @expectedFailure
  def test_04_TaskReportChangeStartDate(self, quiet=quiet, run=run_all_test):
    """
    Check that it is possible to solve date's divergence on the task report 
    line level.
    """
    if not run: return
    sequence_list = SequenceList()

    # Test with a simply order without cell
    sequence_string = '\
                      stepSetStrictSecurity \
                      ' + self.default_task_sequence + '\
                      stepCheckTaskReportIsSolved \
                      \
                      stepCloneTaskReportLine \
                      stepChangeFirstTaskReportLineDate \
                      stepChangeSecondTaskReportLineDate \
                      stepCheckTaskReportIsCalculating \
                      stepTic \
                      stepCheckTaskReportIsDiverged \
                      stepAcceptLineDateDecision \
                      stepTic \
                      stepCheckTaskReportIsSolved \
                      stepCheckTaskReportDates \
                      '
    sequence_list.addSequenceString(sequence_string)

    sequence_list.play(self, quiet=quiet)

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestTaskReportDivergence))
  return suite

