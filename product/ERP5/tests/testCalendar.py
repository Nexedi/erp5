##############################################################################
#
# Copyright (c) 2007 Nexedi SA and Contributors. All Rights Reserved.
#          Romain Courteaud <romain@nexedi.com>
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
import os, sys
if __name__ == '__main__':
  execfile(os.path.join(sys.path[0], 'framework.py'))

# Needed in order to have a log file inside the current folder
os.environ['EVENT_LOG_FILE'] = os.path.join(os.getcwd(), 'zLOG.log')
os.environ['EVENT_LOG_SEVERITY'] = '-300'

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from AccessControl.SecurityManagement import newSecurityManager, \
                                             noSecurityManager
from Products.ERP5Type.tests.Sequence import Sequence, SequenceList
from Products.ERP5Type.tests.utils import createZODBPythonScript
from Products.ERP5Type.tests.utils import removeZODBPythonScript
from DateTime import DateTime

class TestCalendar(ERP5TypeTestCase):

  run_all_test = 1
  person_portal_type = "Person"
  group_calendar_portal_type = "Group Calendar"
  leave_request_portal_type = "Leave Request"
  group_presence_period_portal_type = "Group Presence Period"
  leave_request_period_portal_type = "Leave Request Period"
  start_date = DateTime()
  stop_date = start_date + 0.5
  middle_date = start_date + 0.25
  periodicity_stop_date = start_date + 2

  def getTitle(self):
    return "Calendar"

  def getBusinessTemplateList(self):
    """
    """
    return ('erp5_base', 'erp5_calendar')

  def login(self, quiet=0, run=run_all_test):
    uf = self.getPortal().acl_users
    uf._doAddUser('rc', '', ['Manager', 'Author', 'Assignor', 
                             'Assignee', 'Auditor'], [])
    user = uf.getUserById('rc').__of__(uf)
    newSecurityManager(None, user)

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

  def createCategories(self):
    """
      Light install create only base categories, so we create
      some categories for testing them
    """
    cal_type_category_list = ['type1']
    if len(self.category_tool.calendar_period_type.contentValues()) == 0 :
      for category_id in cal_type_category_list:
        o = self.category_tool.calendar_period_type.newContent(
                         portal_type='Category',
                         id=category_id)

  def stepTic(self,**kw):
    self.tic()

  def afterSetUp(self, quiet=1, run=0):
    """
    Fake after setup
    """
    self.category_tool = self.getCategoryTool()
    self.createCategories()

  def stepCreatePerson(self, sequence=None, sequence_list=None, **kw):
    """
    Create an person
    """
    portal = self.getPortal()
    module = portal.getDefaultModule(self.person_portal_type)
    person = module.newContent(portal_type=self.person_portal_type)
    sequence.edit(
        person=person,
    )

  def stepGetLastCreatedPerson(self, sequence=None, sequence_list=None, **kw):
    """
    Create an person
    """
    portal = self.getPortal()
    module = portal.getDefaultModule(self.person_portal_type)
    id_list = module.contentIds()
    # More than last, random...
    person = getattr(module, id_list[-1])
    sequence.edit(
        person=person,
    )

  def stepCreateGroupCalendar(self, sequence=None, 
                                 sequence_list=None, **kw):
    """
    Create an personal calendar
    """
    portal = self.getPortal()
    module = portal.getDefaultModule(self.group_calendar_portal_type)
    pc = module.newContent(portal_type=self.group_calendar_portal_type)
    sequence.edit(
        group_calendar=pc,
    )

  def stepSetGroupCalendarSource(self, sequence=None, 
                                    sequence_list=None, **kw):
    """
    Set the source
    """
    group_calendar = sequence.get('group_calendar')
    person = sequence.get('person')
    assignment_list = person.contentValues(portal_type='Assignment')
    if len(assignment_list) != 0:
      assignment = assignment_list[0]
    else:
      assignment = person.newContent( 
        portal_type = 'Assignment',
      )
    assignment.setCalendarList(
        assignment.getCalendarList()+[group_calendar.getRelativeUrl()])

  def stepCreateGroupPresencePeriod(self, sequence=None, 
                                      sequence_list=None, **kw):
    """
    Create an personal calendar period
    """
    group_calendar = sequence.get('group_calendar')
    group_presence_period = group_calendar.newContent(
        portal_type=self.group_presence_period_portal_type,
        resource='calendar_period_type/type1',
    )
    sequence.edit(
        group_presence_period=group_presence_period,
    )

  def stepSetGroupPresencePeriodValues(self, sequence=None, 
                                         sequence_list=None, **kw):
    """
    Set values on personal calendar period
    """
    group_presence_period = sequence.get('group_presence_period')

  def stepSetGroupPresencePeriodDates(self, sequence=None, 
                                        sequence_list=None, **kw):
    """
    Set values on personal calendar period
    """
    group_presence_period = sequence.get('group_presence_period')
    group_presence_period.edit(
      start_date=self.start_date,
      stop_date=self.stop_date,
    )

  def stepSetGroupPresencePeriodPerStopDate(self, sequence=None, 
                                        sequence_list=None, **kw):
    """
    Set values on personal calendar period
    """
    group_presence_period = sequence.get('group_presence_period')
    group_presence_period.edit(
      periodicity_stop_date=self.periodicity_stop_date,
    )

  def stepSetGroupPresencePeriodToCheck(self, sequence=None, 
                                          sequence_list=None, **kw):
    """
    Set personal calendar period to check
    """
    group_presence_period = sequence.get('group_presence_period')
    sequence.edit(obj_to_check=group_presence_period)

  def stepSetGroupCalendarEventPerStopDate(self, sequence=None, 
                                        sequence_list=None, **kw):
    """
    Set values on personal calendar event
    """
    group_calendar_event = sequence.get('group_calendar_event')
    group_calendar_event.edit(
      periodicity_stop_date=self.periodicity_stop_date,
    )

  def stepConfirmGroupCalendar(self, sequence=None, 
                               sequence_list=None, **kw):
    """
    Confirm group calendar
    """
    group_calendar = sequence.get('group_calendar')
    self.portal.portal_workflow.doActionFor(
                          group_calendar,
                          'confirm_action',
                          'group_calendar_workflow')


  def stepCreateLeaveRequest(self, sequence=None, 
                                 sequence_list=None, **kw):
    """
    Create a personal calendar
    """
    portal = self.getPortal()
    module = portal.getDefaultModule(self.leave_request_portal_type)
    pc = module.newContent(portal_type=self.leave_request_portal_type)
    sequence.edit(
        leave_request=pc,
    )

  def stepSetLeaveRequestDestination(self, sequence=None, 
                                         sequence_list=None, **kw):
    """
    Set the destination
    """
    leave_request = sequence.get('leave_request')
    person = sequence.get('person')
    leave_request.setDestinationValue(person)

  def stepCreatePersonalLeavePeriod(self, sequence=None, 
                                    sequence_list=None, **kw):
    """
    Create an personal calendar period
    """
    leave_request = sequence.get('leave_request')
    personal_leave_period = leave_request.newContent(
        portal_type=self.leave_request_period_portal_type,
        resource='calendar_period_type/type1',
    )
    sequence.edit(
        personal_leave_period=personal_leave_period,
    )

  def stepSetPersonalLeavePeriodToCheck(self, sequence=None, 
                                        sequence_list=None, **kw):
    """
    Set personal leave period to check
    """
    personal_leave_period = sequence.get('personal_leave_period')
    sequence.edit(obj_to_check=personal_leave_period)

  def stepSetPersonalLeavePeriodValues(self, sequence=None, 
                                       sequence_list=None, **kw):
    """
    Set values on personal calendar event
    """
    personal_leave_period = sequence.get('personal_leave_period')

  def stepSetPersonalLeavePeriodDates(self, sequence=None, 
                                      sequence_list=None, **kw):
    """
    Set values on personal calendar
    """
    personal_leave_period = sequence.get('personal_leave_period')
    personal_leave_period.edit(
      start_date=self.start_date,
      stop_date=self.stop_date,
    )

  def stepSetPersonalLeavePeriodPerStopDate(self, sequence=None, 
                                            sequence_list=None, **kw):
    """
    Set values on personal calendar event
    """
    personal_leave_period = sequence.get('personal_leave_period')
    personal_leave_period.edit(
      periodicity_stop_date=self.periodicity_stop_date,
    )

  def stepPlanLeaveRequest(self, sequence=None, 
                               sequence_list=None, **kw):
    """
    Plan personal calendar
    """
    leave_request = sequence.get('leave_request')
    self.portal.portal_workflow.doActionFor(
                          leave_request,
                          'plan_action',
                          'leave_request_workflow')

  def stepConfirmLeaveRequest(self, sequence=None, 
                               sequence_list=None, **kw):
    """
    Confirm personal calendar
    """
    leave_request = sequence.get('leave_request')
    self.portal.portal_workflow.doActionFor(
                          leave_request,
                          'confirm_action',
                          'leave_request_workflow')

  def getSqlUidList(self):
    """
    Give the full list of path in the catalog
    """
    sql_connection = self.getSQLConnection()
    sql = 'select uid from stock'
    result = sql_connection.manage_test(sql)
    uid_list = [x.uid for x in result]
    return uid_list

  def getSqlMovementUidList(self):
    """
    Give the full list of path in the catalog
    """
    sql_connection = self.getSQLConnection()
    sql = 'select uid from movement'
    result = sql_connection.manage_test(sql)
    uid_list = [x.uid for x in result]
    return uid_list

  def stepCheckNotCatalogued(self, sequence=None, 
                             sequence_list=None, **kw):
    """
    Create an personal calendar period
    """
    uid_list = self.getSqlUidList()
    obj_to_check = sequence.get('obj_to_check')
    self.assertFalse(obj_to_check.getUid() in uid_list)

  def stepCheckCatalogued(self, sequence=None, 
                          sequence_list=None, **kw):
    """
    Create an personal calendar period
    """
    uid_list = self.getSqlUidList()
    obj_to_check = sequence.get('obj_to_check')
    self.assertTrue(obj_to_check.getUid() in uid_list)

#     self.assertEquals(len(obj_to_check.getDatePeriodList()),
#                       uid_list.count(obj_to_check.getUid()))

  def stepCheckCataloguedAsMovement(self, sequence=None, 
                                    sequence_list=None, **kw):
    """
    Create an personal calendar period
    """
    uid_list = self.getSqlMovementUidList()
    obj_to_check = sequence.get('obj_to_check')
    self.assertTrue(obj_to_check.getUid() in uid_list)
#     self.assertEquals(len(obj_to_check.getDatePeriodList()),
#                       uid_list.count(obj_to_check.getUid()))

  def test_01_CatalogCalendarPeriod(self, quiet=0, run=run_all_test):
    """
    Test indexing
    """
    if not run: return
    
    sequence_list = SequenceList()
    sequence_string = '\
              CreatePerson \
              CreateGroupCalendar \
              SetGroupCalendarSource \
              CreateGroupPresencePeriod \
              SetGroupPresencePeriodValues \
              Tic \
              SetGroupPresencePeriodToCheck \
              CheckNotCatalogued \
              ConfirmGroupCalendar \
              Tic \
              CheckNotCatalogued \
              SetGroupPresencePeriodDates \
              Tic \
              CheckCatalogued \
              SetGroupPresencePeriodPerStopDate \
              Tic \
              CheckCatalogued \
              '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_02_CatalogLeaveRequest(self, quiet=0, run=run_all_test):
    """
    Test indexing
    """
    if not run: return
    
    sequence_list = SequenceList()
    sequence_string = '\
              CreatePerson \
              CreateLeaveRequest \
              SetLeaveRequestDestination \
              CreatePersonalLeavePeriod \
              SetPersonalLeavePeriodValues \
              Tic \
              SetPersonalLeavePeriodToCheck \
              CheckNotCatalogued \
              PlanLeaveRequest \
              ConfirmLeaveRequest \
              Tic \
              CheckNotCatalogued \
              SetPersonalLeavePeriodDates \
              Tic \
              CheckCatalogued \
              SetPersonalLeavePeriodPerStopDate \
              Tic \
              CheckCatalogued \
              '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def stepCheckGetTimeAvailability(self, sequence=None, 
                                   sequence_list=None, **kw):
    """
    Check getTimeAvailability
    """
    obj_to_check = sequence.get('obj_to_check')
    person = sequence.get('person')
    start_date = self.start_date
    stop_date = self.stop_date
    second_availability = int(stop_date) - int(start_date)
    date_period_list = obj_to_check._getDatePeriodList()

    # Check 1 period
    self.assertEquals(second_availability,
                      person.getAvailableTime(from_date=start_date, 
                                              to_date=stop_date))
    self.assertEquals(second_availability,
                      person.getAvailableTime(from_date=start_date, 
                                              to_date=stop_date))
    self.assertEquals(second_availability / 2,
                      person.getAvailableTime(from_date=start_date, 
                                              to_date=self.middle_date))
    self.assertEquals(second_availability / 2,
                      person.getAvailableTime(from_date=self.middle_date, 
                                                     to_date=stop_date))
    # Check 2 periods
    self.assertEquals(2 * second_availability,
                      person.getAvailableTime(
                                         from_date=start_date, 
                                         to_date=date_period_list[1][1]))
#     # Check all periods
#     self.assertEquals(len(date_period_list) * second_availability,
#                       person.getAvailableTime())

  def stepCheckDoubleGetTimeAvailability(self, sequence=None, 
                                         sequence_list=None, **kw):
    """
    Check getTimeAvailability
    """
    obj_to_check = sequence.get('obj_to_check')
    person = sequence.get('person')
    start_date = self.start_date
    stop_date = self.stop_date
    second_availability = int(stop_date) - int(start_date)
    # Hop, here is the trick
    second_availability = 2 * second_availability
    date_period_list = obj_to_check._getDatePeriodList()

    # Check 1 period
    self.assertEquals(second_availability,
                      person.getAvailableTime(from_date=start_date, 
                                                 to_date=stop_date))
    # Check 2 periods
    self.assertEquals(2 * second_availability,
                      person.getAvailableTime(
                                         from_date=start_date, 
                                         to_date=date_period_list[1][1]))
#     # Check all periods
#     self.assertEquals(len(date_period_list) * second_availability,
#                       person.getAvailableTime())

  def stepCheckPersonalTimeAvailability(self, sequence=None, 
                                   sequence_list=None, **kw):
    """
    Check getTimeAvailability
    """
    obj_to_check = sequence.get('obj_to_check')
    person = sequence.get('person')
    start_date = self.start_date
    stop_date = self.stop_date
    second_availability = 0
    date_period_list = obj_to_check._getDatePeriodList()

    # Check 1 period
    self.assertEquals(second_availability,
                      person.getAvailableTime(from_date=start_date, 
                                              to_date=stop_date))
    self.assertEquals(second_availability,
                      person.getAvailableTime(from_date=start_date, 
                                              to_date=stop_date))
    self.assertEquals(second_availability / 2,
                      person.getAvailableTime(from_date=start_date, 
                                              to_date=self.middle_date))
    self.assertEquals(second_availability / 2,
                      person.getAvailableTime(from_date=self.middle_date, 
                                                     to_date=stop_date))
    # Check 2 periods
    self.assertEquals(2 * second_availability,
                      person.getAvailableTime(
                                         from_date=start_date, 
                                         to_date=date_period_list[1][1]))
#     # Check all periods
#     self.assertEquals(len(date_period_list) * second_availability,
#                       person.getAvailableTime())

  def stepCheckCumulativeTimeAvailability(self, sequence=None, 
                                          sequence_list=None, **kw):
    """
    Check getTimeAvailability
    """
    obj_to_check = sequence.get('obj_to_check')
    person = sequence.get('person')
    start_date = self.start_date
    stop_date = self.stop_date
    second_availability = int(stop_date) - int(start_date)
    date_period_list = obj_to_check._getDatePeriodList()

    # Check 1 period
    self.assertEquals(0,
                      person.getAvailableTime(from_date=start_date, 
                                              to_date=stop_date))
    # Check 2 periods
    self.assertEquals(second_availability,
                      person.getAvailableTime(
                                         from_date=start_date, 
                                         to_date=date_period_list[1][1]))
#     # Check all periods
#     self.assertEquals(len(date_period_list) * second_availability,
#                       person.getAvailableTime())

  def test_03_getAvailableTime(self, quiet=0, run=run_all_test):
    """
    Test indexing
    """
    if not run: return
    
    # Test that calendar group increase time availability
    sequence_list = SequenceList()
    sequence_string = '\
              CreatePerson \
              CreateGroupCalendar \
              SetGroupCalendarSource \
              CreateGroupPresencePeriod \
              SetGroupPresencePeriodValues \
              Tic \
              SetGroupPresencePeriodToCheck \
              ConfirmGroupCalendar \
              SetGroupPresencePeriodDates \
              SetGroupPresencePeriodPerStopDate \
              Tic \
              CheckCatalogued \
              CheckGetTimeAvailability \
              '
    sequence_list.addSequenceString(sequence_string)
    
    # Test getTimeAvailability does not interfere with other documents
    sequence_list = SequenceList()
    sequence_string = '\
              CreatePerson \
              CreateGroupCalendar \
              SetGroupCalendarSource \
              CreateGroupPresencePeriod \
              SetGroupPresencePeriodValues \
              Tic \
              SetGroupPresencePeriodToCheck \
              ConfirmGroupCalendar \
              SetGroupPresencePeriodDates \
              SetGroupPresencePeriodPerStopDate \
              Tic \
              CheckCatalogued \
              CheckGetTimeAvailability \
              '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)
    
    # Test getTimeAvailability is cumulative
    sequence_list = SequenceList()
    sequence_string = '\
              GetLastCreatedPerson \
              CreateGroupCalendar \
              SetGroupCalendarSource \
              CreateGroupPresencePeriod \
              SetGroupPresencePeriodValues \
              Tic \
              SetGroupPresencePeriodToCheck \
              PlanGroupCalendar \
              ConfirmGroupCalendar \
              SetGroupPresencePeriodDates \
              SetGroupPresencePeriodPerStopDate \
              Tic \
              CheckCatalogued \
              CheckDoubleGetTimeAvailability \
              '
    sequence_list.addSequenceString(sequence_string)
    
    # Test that leave period decrease time availability
    sequence_list = SequenceList()
    sequence_string = '\
              CreatePerson \
              CreateLeaveRequest \
              SetLeaveRequestDestination \
              CreatePersonalLeavePeriod \
              SetPersonalLeavePeriodValues \
              Tic \
              SetPersonalLeavePeriodToCheck \
              PlanLeaveRequest \
              ConfirmLeaveRequest \
              SetPersonalLeavePeriodDates\
              SetPersonalLeavePeriodPerStopDate\
              Tic \
              CheckCatalogued \
              CheckPersonalTimeAvailability \
              '
    sequence_list.addSequenceString(sequence_string)
    
    # Combine object
    sequence_list = SequenceList()
    sequence_string = '\
              CreatePerson \
              CreateGroupCalendar \
              SetGroupCalendarSource \
              CreateGroupPresencePeriod \
              SetGroupPresencePeriodValues \
              Tic \
              SetGroupPresencePeriodToCheck \
              ConfirmGroupCalendar \
              SetGroupPresencePeriodDates \
              SetGroupPresencePeriodPerStopDate \
              Tic \
              CheckCatalogued \
              CheckGetTimeAvailability \
              \
              CreateLeaveRequest \
              SetLeaveRequestDestination \
              CreatePersonalLeavePeriod \
              SetPersonalLeavePeriodValues \
              Tic \
              PlanLeaveRequest \
              ConfirmLeaveRequest \
              SetPersonalLeavePeriodDates\
              Tic \
              CheckCumulativeTimeAvailability \
              '
    sequence_list.addSequenceString(sequence_string)

    sequence_list.play(self)

  def test_04_getCapacityAvailability(self, quiet=0, run=0):
    """
    Test getCapacityAvailability
    """
    if not run: return
    raise "NotImplementedYet"
    
    # Test that calendar group increase time availability
    sequence_list = SequenceList()
    sequence_string = '\
              CreatePerson \
              CreateGroupCalendar \
              SetGroupCalendarSource \
              CreateGroupPresencePeriod \
              SetGroupPresencePeriodValues \
              Tic \
              SetGroupPresencePeriodToCheck \
              ConfirmGroupCalendar \
              SetGroupPresencePeriodDates \
              SetGroupPresencePeriodPerStopDate \
              Tic \
              CheckCatalogued \
              CheckGetTimeAvailability \
              '
    sequence_list.addSequenceString(sequence_string)
    
    # Test getTimeAvailability does not interfere with other documents
    sequence_list = SequenceList()
    sequence_string = '\
              CreatePerson \
              CreateGroupCalendar \
              SetGroupCalendarSource \
              CreateGroupPresencePeriod \
              SetGroupPresencePeriodValues \
              Tic \
              SetGroupPresencePeriodToCheck \
              ConfirmGroupCalendar \
              SetGroupPresencePeriodDates \
              SetGroupPresencePeriodPerStopDate \
              Tic \
              CheckCatalogued \
              CheckGetTimeAvailability \
              '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)
    
    # Test getTimeAvailability is cumulative
    sequence_list = SequenceList()
    sequence_string = '\
              GetLastCreatedPerson \
              CreateGroupCalendar \
              SetGroupCalendarSource \
              CreateGroupPresencePeriod \
              SetGroupPresencePeriodValues \
              Tic \
              SetGroupPresencePeriodToCheck \
              ConfirmGroupCalendar \
              SetGroupPresencePeriodDates \
              SetGroupPresencePeriodPerStopDate \
              Tic \
              CheckCatalogued \
              CheckDoubleGetTimeAvailability \
              '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

if __name__ == '__main__':
  framework()
else:
  import unittest
  def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestCalendar))
    return suite
