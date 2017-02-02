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

import unittest
from unittest import skip

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5ReportTestCase
from AccessControl.SecurityManagement import newSecurityManager
from Products.ERP5Type.tests.Sequence import SequenceList
from DateTime import DateTime

class TestCalendar(ERP5ReportTestCase):

  run_all_test = 1
  person_portal_type = "Person"
  group_calendar_portal_type = "Group Calendar"
  leave_request_portal_type = "Leave Request"
  presence_request_portal_type = "Presence Request"
  group_presence_period_portal_type = "Group Presence Period"
  leave_request_period_portal_type = "Leave Request Period"
  presence_request_period_portal_type = "Presence Request Period"
  start_date = DateTime(DateTime().ISO8601())
  stop_date = start_date + 0.5
  middle_date = start_date + 0.25
  periodicity_stop_date = start_date + 2

  def getTitle(self):
    return "Calendar"

  def getBusinessTemplateList(self):
    """
    """
    return ('erp5_base', 'erp5_pdm', 'erp5_calendar', 'erp5_core_proxy_field_legacy')

  def login(self, quiet=0, run=run_all_test):
    uf = self.getPortal().acl_users
    uf._doAddUser('rc', '', ['Manager', 'Author', 'Assignor',
                             'Assignee', 'Auditor'], [])
    user = uf.getUserById('rc').__of__(uf)
    newSecurityManager(None, user)

  def createCategories(self):
    """
      Light install create only base categories, so we create
      some categories for testing them
    """
    cal_type_category_list = ['type1', 'type2', 'type3']
    if len(self.category_tool.calendar_period_type.contentValues()) == 0 :
      for category_id in cal_type_category_list:
        o = self.category_tool.calendar_period_type.newContent(
                         portal_type='Category',
                         id=category_id)

    if 'my_group' not in self.category_tool.group.contentIds():
      self.category_tool.group.newContent(portal_type='Category',
                                          id='my_group')

  def createService(self):
    """
    Create service that will be used to fill stock
    """
    module = self.portal.service_module
    if getattr(module, 'consulting_service', None) is None:
      module.newContent(id='consulting_service', title='Consulting Service')


  def afterSetUp(self):
    """
    Fake after setup
    """
    self.category_tool = self.getCategoryTool()
    self.createCategories()
    self.createService()
    # activate constraints
    self._addPropertySheet('Group Calendar', 'CalendarConstraint')
    self._addPropertySheet('Presence Request', 'CalendarConstraint')
    self._addPropertySheet('Leave Request', 'CalendarConstraint')

    self._addPropertySheet('Presence Request', 'IndividualCalendarConstraint')
    self._addPropertySheet('Leave Request', 'IndividualCalendarConstraint')

    self._addPropertySheet('Leave Request Period', 'CalendarPeriodConstraint')
    self._addPropertySheet('Presence Request Period', 'CalendarPeriodConstraint')
    self._addPropertySheet('Group Presence Period', 'CalendarPeriodConstraint')

    # regenerate accessors after category changes & portal type changes
    self.commit()

  def beforeTearDown(self):
    self.abort()
    for module in (self.portal.group_calendar_module,
                   self.portal.leave_request_module,
                   self.portal.presence_request_module,):
      module.manage_delObjects(list(module.objectIds()))
    self.tic()

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

  def stepSetGroupCalendarAssignment(self, sequence=None,
                                    sequence_list=None, **kw):
    """
    Set the source
    """
    group_calendar = sequence.get('group_calendar')
    person = sequence.get('person')
    assignment = self.portal.group_calendar_assignment_module.newContent(
                      destination_value=person,
                      resource_value=self.portal.service_module.consulting_service,
                      start_date=self.start_date,
                      stop_date=self.periodicity_stop_date,
                      specialise_value=group_calendar)
    assignment.confirm()
    sequence.edit(assignment=assignment)

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
    # XXX(Seb), replace by interaction workflow
    #sequence.get("assignment").reindexObject()

  def stepSetGroupPresencePeriodPerStopDate(self, sequence=None,
                                        sequence_list=None, **kw):
    """
    Set values on personal calendar period
    """
    group_presence_period = sequence.get('group_presence_period')
    group_presence_period.edit(
      periodicity_stop_date=self.periodicity_stop_date,
    )

  def stepSetGroupCalendarAssignmentToCheck(self, sequence=None,
                                          sequence_list=None, **kw):
    """
    Set personal calendar period to check
    """
    assignment = sequence.get('assignment')
    sequence.edit(obj_to_check=assignment)

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
    group_calendar.confirm()
    self.assertEqual('confirmed', group_calendar.getSimulationState())

  def stepConfirmActionGroupCalendar(self, sequence=None,
                               sequence_list=None, **kw):
    """
    Confirm group calendar with user interface transition
    """
    group_calendar = sequence.get('group_calendar')
    self.portal.portal_workflow.doActionFor(
                          group_calendar,
                          'confirm_action',
                          'group_calendar_workflow')
    self.assertEqual('confirmed', group_calendar.getSimulationState())


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
        resource_value=self.portal.service_module.consulting_service
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
    leave_request.plan()
    self.assertEqual('planned', leave_request.getSimulationState())

  def stepConfirmLeaveRequest(self, sequence=None,
                               sequence_list=None, **kw):
    """
    Confirm personal calendar
    """
    leave_request = sequence.get('leave_request')
    leave_request.confirm()
    self.assertEqual('confirmed', leave_request.getSimulationState())

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

#     self.assertEqual(len(obj_to_check.getDatePeriodList()),
#                       uid_list.count(obj_to_check.getUid()))

  def stepCheckCataloguedAsMovement(self, sequence=None,
                                    sequence_list=None, **kw):
    """
    Create an personal calendar period
    """
    uid_list = self.getSqlMovementUidList()
    obj_to_check = sequence.get('obj_to_check')
    self.assertTrue(obj_to_check.getUid() in uid_list)
#     self.assertEqual(len(obj_to_check.getDatePeriodList()),
#                       uid_list.count(obj_to_check.getUid()))

  def stepCreatePresenceRequest(self, sequence=None,
                                 sequence_list=None, **kw):
    """
    Create a personal calendar
    """
    portal = self.getPortal()
    module = portal.getDefaultModule(self.presence_request_portal_type)
    pc = module.newContent(portal_type=self.presence_request_portal_type)
    sequence.edit(
        presence_request=pc,
    )

  def stepSetPresenceRequestDestination(self, sequence=None,
                                         sequence_list=None, **kw):
    """
    Set the destination
    """
    presence_request = sequence.get('presence_request')
    person = sequence.get('person')
    presence_request.setDestinationValue(person)

  def stepCreatePersonalPresencePeriod(self, sequence=None,
                                    sequence_list=None, **kw):
    """
    Create an personal calendar period
    """
    presence_request = sequence.get('presence_request')
    personal_presence_period = presence_request.newContent(
        portal_type=self.presence_request_period_portal_type,
        resource_value=self.portal.service_module.consulting_service
    )
    sequence.edit(
        personal_presence_period=personal_presence_period,
    )

  def stepSetPersonalPresencePeriodToCheck(self, sequence=None,
                                        sequence_list=None, **kw):
    """
    Set personal presence period to check
    """
    personal_presence_period = sequence.get('personal_presence_period')
    sequence.edit(obj_to_check=personal_presence_period)

  def stepSetPersonalPresencePeriodValues(self, sequence=None,
                                       sequence_list=None, **kw):
    """
    Set values on personal calendar event
    """
    personal_presence_period = sequence.get('personal_presence_period')

  def stepSetPersonalPresencePeriodDates(self, sequence=None,
                                      sequence_list=None, **kw):
    """
    Set values on personal calendar
    """
    personal_presence_period = sequence.get('personal_presence_period')
    personal_presence_period.edit(
      start_date=self.start_date,
      stop_date=self.stop_date,
    )

  def stepSetPersonalPresencePeriodPerStopDate(self, sequence=None,
                                            sequence_list=None, **kw):
    """
    Set values on personal calendar event
    """
    personal_presence_period = sequence.get('personal_presence_period')
    personal_presence_period.edit(
      periodicity_stop_date=self.periodicity_stop_date,
    )

  def stepPlanPresenceRequest(self, sequence=None,
                               sequence_list=None, **kw):
    """
    Plan personal calendar
    """
    presence_request = sequence.get('presence_request')
    presence_request.plan()
    self.assertEqual('planned', presence_request.getSimulationState())

  def stepConfirmPresenceRequest(self, sequence=None,
                               sequence_list=None, **kw):
    """
    Confirm personal calendar
    """
    presence_request = sequence.get('presence_request')
    presence_request.confirm()
    self.assertEqual('confirmed', presence_request.getSimulationState())

  def test_01_CatalogCalendarPeriod(self, quiet=0, run=run_all_test):
    """
    Test indexing
    """
    if not run: return

    sequence_list = SequenceList()
    sequence_string = '\
              CreatePerson \
              CreateGroupCalendar \
              SetGroupCalendarAssignment \
              CreateGroupPresencePeriod \
              SetGroupPresencePeriodValues \
              Tic \
              SetGroupCalendarAssignmentToCheck \
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

  def test_CatalogPresenceRequest(self, quiet=0, run=run_all_test):
    """
    Test indexing
    """
    if not run: return

    sequence_list = SequenceList()
    sequence_string = '''
              CreatePerson
              CreateLeaveRequest
              SetLeaveRequestDestination
              CreatePersonalLeavePeriod
              SetPersonalLeavePeriodValues
              Tic
              SetPersonalLeavePeriodToCheck
              CheckNotCatalogued
              PlanLeaveRequest
              ConfirmLeaveRequest
              Tic
              CheckNotCatalogued
              SetPersonalLeavePeriodDates
              Tic
              CheckCatalogued
              SetPersonalLeavePeriodPerStopDate
              Tic
              CheckCatalogued
              '''
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
    date_period_list = obj_to_check._getDatePeriodDataList()

    # Check 1 period
    self.assertEqual(second_availability,
                      person.getAvailableTime(from_date=start_date,
                                              to_date=stop_date))
    self.assertEqual(second_availability / 2,
                      person.getAvailableTime(from_date=start_date,
                                              to_date=self.middle_date))
    self.assertEqual(second_availability / 2,
                      person.getAvailableTime(from_date=self.middle_date,
                                                     to_date=stop_date))
    # Check 2 periods
    self.assertEqual(2 * second_availability,
                      person.getAvailableTime(
                                         from_date=start_date,
                                         to_date=date_period_list[1]['stop_date']))
#     # Check all periods
#     self.assertEqual(len(date_period_list) * second_availability,
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
    self.assertEqual(second_availability,
                      person.getAvailableTime(from_date=start_date,
                                                 to_date=stop_date))
    # Check 2 periods
    self.assertEqual(2 * second_availability,
                      person.getAvailableTime(
                                         from_date=start_date,
                                         to_date=date_period_list[1][1]))
#     # Check all periods
#     self.assertEqual(len(date_period_list) * second_availability,
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
    self.assertEqual(second_availability,
                      person.getAvailableTime(from_date=start_date,
                                              to_date=stop_date))
    self.assertEqual(second_availability,
                      person.getAvailableTime(from_date=start_date,
                                              to_date=stop_date))
    self.assertEqual(second_availability / 2,
                      person.getAvailableTime(from_date=start_date,
                                              to_date=self.middle_date))
    self.assertEqual(second_availability / 2,
                      person.getAvailableTime(from_date=self.middle_date,
                                                     to_date=stop_date))
    # Check 2 periods
    self.assertEqual(2 * second_availability,
                      person.getAvailableTime(
                                         from_date=start_date,
                                         to_date=date_period_list[1][1]))
#     # Check all periods
#     self.assertEqual(len(date_period_list) * second_availability,
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
    date_period_list = obj_to_check._getDatePeriodDataList()

    # Check 1 period
    self.assertEqual(0,
                      person.getAvailableTime(from_date=start_date,
                                              to_date=stop_date))
    # Check 2 periods
    self.assertEqual(second_availability,
                      person.getAvailableTime(
                                         from_date=start_date,
                                         to_date=date_period_list[1]['stop_date']))
#     # Check all periods
#     self.assertEqual(len(date_period_list) * second_availability,
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
              SetGroupCalendarAssignment \
              CreateGroupPresencePeriod \
              SetGroupPresencePeriodValues \
              Tic \
              SetGroupCalendarAssignmentToCheck \
              SetGroupPresencePeriodDates \
              SetGroupPresencePeriodPerStopDate \
              ConfirmActionGroupCalendar \
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
              SetGroupCalendarAssignment \
              CreateGroupPresencePeriod \
              SetGroupPresencePeriodValues \
              Tic \
              SetGroupCalendarAssignmentToCheck \
              SetGroupPresencePeriodDates \
              SetGroupPresencePeriodPerStopDate \
              ConfirmActionGroupCalendar \
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
              SetGroupCalendarAssignment \
              CreateGroupPresencePeriod \
              SetGroupPresencePeriodValues \
              Tic \
              SetGroupCalendarAssignmentToCheck \
              PlanGroupCalendar \
              SetGroupPresencePeriodDates \
              SetGroupPresencePeriodPerStopDate \
              ConfirmActionGroupCalendar \
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
              SetGroupCalendarAssignment \
              CreateGroupPresencePeriod \
              SetGroupPresencePeriodValues \
              Tic \
              SetGroupCalendarAssignmentToCheck \
              SetGroupPresencePeriodDates \
              SetGroupPresencePeriodPerStopDate \
              ConfirmActionGroupCalendar \
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
    raise NotImplementedError

    # Test that calendar group increase time availability
    sequence_list = SequenceList()
    sequence_string = '\
              CreatePerson \
              CreateGroupCalendar \
              SetGroupCalendarAssignment \
              CreateGroupPresencePeriod \
              SetGroupPresencePeriodValues \
              Tic \
              SetGroupCalendarAssignmentToCheck \
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
              SetGroupCalendarAssignment \
              CreateGroupPresencePeriod \
              SetGroupPresencePeriodValues \
              Tic \
              SetGroupCalendarAssignmentToCheck \
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
              SetGroupCalendarAssignment \
              CreateGroupPresencePeriod \
              SetGroupPresencePeriodValues \
              Tic \
              SetGroupCalendarAssignmentToCheck \
              ConfirmGroupCalendar \
              SetGroupPresencePeriodDates \
              SetGroupPresencePeriodPerStopDate \
              Tic \
              CheckCatalogued \
              CheckDoubleGetTimeAvailability \
              '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_GroupCalendarConstraint(self):
    group_calendar = self.portal.group_calendar_module.newContent(
                                  portal_type='Group Calendar')
    # no lines
    self.assertEqual(1, len(group_calendar.checkConsistency()))
    group_calendar_period = group_calendar.newContent(
                                  portal_type='Group Presence Period')
    # invalid line (no dates, no resource)
    self.assertEqual(3, len(group_calendar.checkConsistency()))
    group_calendar_period.setStartDate(self.start_date)
    group_calendar_period.setStopDate(self.stop_date)
    self.assertEqual(1, len(group_calendar.checkConsistency()))
    group_calendar_period.setResourceValue(
          self.portal.portal_categories.calendar_period_type.type1)
    self.assertEqual(0, len(group_calendar.checkConsistency()))

  def test_LeaveRequestCalendarConstraint(self):
    leave_request = self.portal.leave_request_module.newContent(
                                  portal_type='Leave Request')
    # no lines, no person
    self.assertEqual(2, len(leave_request.checkConsistency()))
    leave_request_period = leave_request.newContent(
                                  portal_type='Leave Request Period')
    # no person, invalid line (no dates, no resource)
    self.assertEqual(4, len(leave_request.checkConsistency()))
    leave_request_period.setStartDate(self.start_date)
    leave_request_period.setStopDate(self.stop_date)
    self.assertEqual(2, len(leave_request.checkConsistency()))
    leave_request_period.setResourceValue(
          self.portal.portal_categories.calendar_period_type.type1)
    self.assertEqual(1, len(leave_request.checkConsistency()))
    person = self.portal.person_module.newContent(portal_type='Person')
    leave_request.setDestinationValue(person)
    self.assertEqual(0, len(leave_request.checkConsistency()))

  def test_PresenceRequestCalendarConstraint(self):
    presence_request = self.portal.presence_request_module.newContent(
                                  portal_type='Presence Request')
    # no lines, no person
    self.assertEqual(2, len(presence_request.checkConsistency()))
    presence_request_period = presence_request.newContent(
                                  portal_type='Presence Request Period')
    # no person, invalid line (no dates, no resource)
    self.assertEqual(4, len(presence_request.checkConsistency()))
    presence_request_period.setStartDate(self.start_date)
    presence_request_period.setStopDate(self.stop_date)
    self.assertEqual(2, len(presence_request.checkConsistency()))
    presence_request_period.setResourceValue(
          self.portal.portal_categories.calendar_period_type.type1)
    self.assertEqual(1, len(presence_request.checkConsistency()))
    person = self.portal.person_module.newContent(portal_type='Person')
    presence_request.setDestinationValue(person)
    self.assertEqual(0, len(presence_request.checkConsistency()))

  def test_SimpleLeaveRequestWithSameDateAsGroupCalendar(self):
    group_calendar = self.portal.group_calendar_module.newContent(
                                  portal_type='Group Calendar')
    group_calendar_period = group_calendar.newContent(
                                  portal_type='Group Presence Period')
    group_calendar_period.setStartDate(self.start_date)
    group_calendar_period.setStopDate(self.stop_date)
    group_calendar_period.setResourceValue(
          self.portal.portal_categories.calendar_period_type.type1)
    group_calendar.confirm()

    person = self.portal.person_module.newContent(portal_type='Person')
    assignment = self.portal.group_calendar_assignment_module.newContent(
                      specialise_value=group_calendar,
                      resource_value=self.portal.service_module.consulting_service,
                      start_date=self.start_date,
                      stop_date=self.stop_date,
                      destination_value=person)
    assignment.confirm()
    self.tic()

    # there is 43200 seconds between self.start_date and self.stop_date
    total_time = 43200

    self.assertEqual(total_time, person.getAvailableTime(
                                from_date=self.start_date-1,
                                to_date=self.stop_date+1))
    self.assertEqual([total_time], [x.total_quantity for x in
                              person.getAvailableTimeSequence(
                                year=1,
                                from_date=self.start_date-1,
                                to_date=self.stop_date+1)])

    available_time_movement_list = person.Person_getAvailableTimeMovementList(
                                            from_date=self.start_date-1,
                                            to_date=self.stop_date+1)
    self.assertEqual(1, len(available_time_movement_list))
    self.assertEqual([(self.start_date.ISO(), self.stop_date.ISO())],
                      [(x.getStartDate().ISO(), x.getStopDate().ISO()) for x in
                          available_time_movement_list])


    leave_request = self.portal.leave_request_module.newContent(
                                  portal_type='Leave Request')
    leave_request_period = leave_request.newContent(
                                  portal_type='Leave Request Period')
    leave_request_period.setStartDate(self.start_date)
    leave_request_period.setStopDate(self.stop_date)
    leave_request_period.setResourceValue(
          self.portal.portal_categories.calendar_period_type.type1)
    leave_request.setDestinationValue(person)
    leave_request.confirm()

    self.tic()

    self.assertEqual(0, person.getAvailableTime(
                                from_date=self.start_date-1,
                                to_date=self.stop_date+1))
    self.assertEqual([0], [x.total_quantity for x in
                              person.getAvailableTimeSequence(
                                year=1,
                                from_date=self.start_date-1,
                                to_date=self.stop_date+1)])

    available_time_movement_list = person.Person_getAvailableTimeMovementList(
                                            from_date=self.start_date-1,
                                            to_date=self.stop_date+1)
    self.assertEqual(0, len(available_time_movement_list))


  @skip("Need to check if we want later to support this again. Drop support for now")
  def test_LeaveRequestWithSameDateAsGroupCalendar(self):
    group_calendar = self.portal.group_calendar_module.newContent(
                                  portal_type='Group Calendar')
    group_calendar_period_am = group_calendar.newContent(
                                  portal_type='Group Presence Period')
    group_calendar_period_am.setStartDate('2008/01/01 08:00')
    group_calendar_period_am.setStopDate('2008/01/01 12:00')
    group_calendar_period_am.setResourceValue(
          self.portal.portal_categories.calendar_period_type.type1)
    group_calendar_period_pm = group_calendar.newContent(
                                  portal_type='Group Presence Period')
    group_calendar_period_pm.setStartDate('2008/01/01 14:00')
    group_calendar_period_pm.setStopDate('2008/01/01 18:00')
    group_calendar_period_pm.setResourceValue(
          self.portal.portal_categories.calendar_period_type.type1)

    group_calendar.confirm()

    person = self.portal.person_module.newContent(portal_type='Person')
    assignment = self.portal.group_calendar_assignment_module.newContent(
                      specialise_value=group_calendar,
                      resource_value=self.portal.service_module.consulting_service,
                      start_date=DateTime(2008, 1, 1).earliestTime(),
                      stop_date=DateTime(2008, 1, 1).latestTime(),
                      destination_value=person)
    assignment.confirm()
    self.tic()

    self.assertEqual((18 - 14 + 12 - 8) * 60 * 60, person.getAvailableTime(
                            from_date=DateTime(2008, 1, 1).earliestTime(),
                            to_date=DateTime(2008, 1, 1).latestTime()))

    self.assertEqual([(18 - 14 + 12 - 8) * 60 * 60],
      [x.total_quantity for x in person.getAvailableTimeSequence(
                  day=1,
                  from_date=DateTime(2008, 1, 1).earliestTime(),
                  to_date=DateTime(2008, 1, 1).latestTime())])

    available_time_movement_list = person.Person_getAvailableTimeMovementList(
                  from_date=DateTime(2008, 1, 1).earliestTime(),
                  to_date=DateTime(2008, 1, 1).latestTime())
    self.assertEqual(2, len(available_time_movement_list))
    self.assertEqual(
        [(DateTime('2008/01/01 08:00'), DateTime('2008/01/01 12:00')),
         (DateTime('2008/01/01 14:00'), DateTime('2008/01/01 18:00'))],
        [(m.getStartDate(), m.getStopDate()) for m in
          available_time_movement_list])

    leave_request = self.portal.leave_request_module.newContent(
                                  portal_type='Leave Request')
    leave_request_period = leave_request.newContent(
                                  portal_type='Leave Request Period')
    leave_request_period.setStartDate('2008/01/01 08:00')
    leave_request_period.setStopDate('2008/01/01 18:00')
    leave_request_period.setResourceValue(
          self.portal.portal_categories.calendar_period_type.type1)
    leave_request.setDestinationValue(person)
    leave_request.confirm()

    self.tic()

    self.assertEqual(0, person.getAvailableTime(
                            from_date=DateTime(2008, 1, 1).earliestTime(),
                            to_date=DateTime(2008, 1, 1).latestTime()))

    self.assertEqual([0],
      [x.total_quantity for x in person.getAvailableTimeSequence(
                  day=1,
                  from_date=DateTime(2008, 1, 1).earliestTime(),
                  to_date=DateTime(2008, 1, 1).latestTime())])

    available_time_movement_list = person.Person_getAvailableTimeMovementList(
                  from_date=DateTime(2008, 1, 1).earliestTime(),
                  to_date=DateTime(2008, 1, 1).latestTime())
    self.assertEqual(0, len(available_time_movement_list))


  @skip("Need to check if we want later to support this again. Drop support for now")
  def test_LeaveRequestWithSameDateAsRepeatedGroupCalendar(self):
    group_calendar = self.portal.group_calendar_module.newContent(
                                  portal_type='Group Calendar')
    group_calendar_period = group_calendar.newContent(
                                  portal_type='Group Presence Period')
    # note that 2008/01/01 was a Tuesday
    group_calendar_period.setStartDate('2008/01/01 08:00')
    group_calendar_period.setStopDate('2008/01/01 18:00')
    group_calendar_period.setResourceValue(
          self.portal.portal_categories.calendar_period_type.type1)
    group_calendar_period.setPeriodicityStopDate('2008/01/30')
    group_calendar_period.setPeriodicityWeekDayList(['Monday'])

    group_calendar.confirm()

    person = self.portal.person_module.newContent(portal_type='Person')
    assignment = self.portal.group_calendar_assignment_module.newContent(
                      specialise_value=group_calendar,
                      resource_value=self.portal.service_module.consulting_service,
                      start_date=DateTime(2008, 1, 1).earliestTime(),
                      stop_date=DateTime(2008, 1, 10).latestTime(),
                      destination_value=person)
    assignment.confirm()
    self.tic()

    # 2008/01/07 was a Monday
    self.assertEqual((18 - 8) * 60 * 60, person.getAvailableTime(
                            from_date=DateTime(2008, 1, 6).earliestTime(),
                            to_date=DateTime(2008, 1, 7).latestTime()))

    self.assertEqual([(18 - 8) * 60 * 60],
      [x.total_quantity for x in person.getAvailableTimeSequence(
                  day=2,
                  from_date=DateTime(2008, 1, 6).earliestTime(),
                  to_date=DateTime(2008, 1, 7).latestTime())])

    available_time_movement_list = person.Person_getAvailableTimeMovementList(
                  from_date=DateTime(2008, 1, 6).earliestTime(),
                  to_date=DateTime(2008, 1, 7).latestTime())
    self.assertEqual(1, len(available_time_movement_list))
    self.assertEqual(
        [(DateTime('2008/01/07 08:00'), DateTime('2008/01/07 18:00'))],
        [(m.getStartDate(), m.getStopDate()) for m in
          available_time_movement_list])

    leave_request = self.portal.leave_request_module.newContent(
                                  portal_type='Leave Request')
    leave_request_period = leave_request.newContent(
                                  portal_type='Leave Request Period')

    leave_request_period.setStartDate('2008/01/06 08:00')
    leave_request_period.setStopDate('2008/01/07 18:00')
    leave_request_period.setResourceValue(
          self.portal.portal_categories.calendar_period_type.type1)
    leave_request.setDestinationValue(person)
    leave_request.confirm()

    self.tic()

    self.assertEqual(0, person.getAvailableTime(
                            from_date=DateTime(2008, 1, 6).earliestTime(),
                            to_date=DateTime(2008, 1, 7).latestTime()))

    self.assertEqual([0],
      [x.total_quantity for x in person.getAvailableTimeSequence(
                  day=2,
                  from_date=DateTime(2008, 1, 6).earliestTime(),
                  to_date=DateTime(2008, 1, 7).latestTime())])
    available_time_movement_list = person.Person_getAvailableTimeMovementList(
                  from_date=DateTime(2008, 1, 6).earliestTime(),
                  to_date=DateTime(2008, 1, 7).latestTime())
    self.assertEqual(0, len(available_time_movement_list))

  def test_LeaveRequestOverlappingGroupCalendar(self):
    group_calendar = self.portal.group_calendar_module.newContent(
                                  portal_type='Group Calendar')
    group_calendar_period = group_calendar.newContent(
                                  portal_type='Group Presence Period')
    group_calendar_period.setStartDate('2008/01/01 08:00')
    group_calendar_period.setStopDate('2008/01/01 18:00')
    group_calendar_period.setResourceValue(
          self.portal.portal_categories.calendar_period_type.type1)
    group_calendar.confirm()

    person = self.portal.person_module.newContent(portal_type='Person')
    assignment = self.portal.group_calendar_assignment_module.newContent(
                      specialise_value=group_calendar,
                      resource_value=self.portal.service_module.consulting_service,
                      start_date=DateTime(2008, 1, 1).earliestTime(),
                      stop_date=DateTime(2008, 1, 1).latestTime(),
                      destination_value=person)
    assignment.confirm()
    self.tic()

    self.assertEqual((18 - 8) * 60 * 60, person.getAvailableTime(
                            from_date=DateTime(2008, 1, 1).earliestTime(),
                            to_date=DateTime(2008, 1, 1).latestTime()))

    self.assertEqual([(18 - 8) * 60 * 60],
      [x.total_quantity for x in person.getAvailableTimeSequence(
                  day=1,
                  from_date=DateTime(2008, 1, 1).earliestTime(),
                  to_date=DateTime(2008, 1, 1).latestTime())])

    available_time_movement_list = person.Person_getAvailableTimeMovementList(
                  from_date=DateTime(2008, 1, 1).earliestTime(),
                  to_date=DateTime(2008, 1, 1).latestTime())
    self.assertEqual(1, len(available_time_movement_list))
    self.assertEqual(
        [(DateTime('2008/01/01 08:00'), DateTime('2008/01/01 18:00'))],
        [(m.getStartDate(), m.getStopDate()) for m in
          available_time_movement_list])

    leave_request = self.portal.leave_request_module.newContent(
                                  portal_type='Leave Request')
    leave_request_period = leave_request.newContent(
                                  portal_type='Leave Request Period')
    leave_request_period.setStartDate('2008/01/01 09:00')
    leave_request_period.setStopDate('2008/01/01 17:00')
    leave_request_period.setResourceValue(
          self.portal.portal_categories.calendar_period_type.type1)
    leave_request.setDestinationValue(person)
    leave_request.confirm()

    self.tic()

    self.assertEqual((9-8 + 18-17) * 60 * 60, person.getAvailableTime(
                            from_date=DateTime(2008, 1, 1).earliestTime(),
                            to_date=DateTime(2008, 1, 1).latestTime()))

    self.assertEqual([(9-8 + 18-17) * 60 * 60],
      [x.total_quantity for x in person.getAvailableTimeSequence(
                  day=1,
                  from_date=DateTime(2008, 1, 1).earliestTime(),
                  to_date=DateTime(2008, 1, 1).latestTime())])

    available_time_movement_list = person.Person_getAvailableTimeMovementList(
                  from_date=DateTime(2008, 1, 1).earliestTime(),
                  to_date=DateTime(2008, 1, 1).latestTime())
    self.assertEqual(2, len(available_time_movement_list))
    self.assertEqual(
        [(DateTime('2008/01/01 08:00'),
          DateTime('2008/01/01 09:00')),
         (DateTime('2008/01/01 17:00'),
          DateTime('2008/01/01 18:00'))],
        [(m.getStartDate(), m.getStopDate()) for m in
                        available_time_movement_list])

  @skip("Need to check if we want later to support this again. Drop support for now")
  def test_LeaveRequestOverlappingBeforeGroupCalendar(self):
    group_calendar = self.portal.group_calendar_module.newContent(
                                  portal_type='Group Calendar')
    group_calendar_period = group_calendar.newContent(
                                  portal_type='Group Presence Period')
    group_calendar_period.setStartDate('2008/01/01 08:00')
    group_calendar_period.setStopDate('2008/01/01 18:00')
    group_calendar_period.setResourceValue(
          self.portal.portal_categories.calendar_period_type.type1)
    group_calendar.confirm()

    person = self.portal.person_module.newContent(portal_type='Person')
    assignment = self.portal.group_calendar_assignment_module.newContent(
                      specialise_value=group_calendar,
                      resource_value=self.portal.service_module.consulting_service,
                      start_date=DateTime(2008, 1, 1).earliestTime(),
                      stop_date=DateTime(2008, 1, 1).latestTime(),
                      destination_value=person)
    assignment.confirm()
    self.tic()
    leave_request = self.portal.leave_request_module.newContent(
                                  portal_type='Leave Request')
    leave_request_period = leave_request.newContent(
                                  portal_type='Leave Request Period')
    leave_request_period.setStartDate('2008/01/01 07:00')
    leave_request_period.setStopDate('2008/01/01 09:00')
    leave_request_period.setResourceValue(
          self.portal.portal_categories.calendar_period_type.type1)
    leave_request.setDestinationValue(person)
    leave_request.confirm()

    self.tic()

    self.assertEqual((18-9) * 60 * 60, person.getAvailableTime(
                            from_date=DateTime(2008, 1, 1).earliestTime(),
                            to_date=DateTime(2008, 1, 1).latestTime()))

    self.assertEqual([(18-9) * 60 * 60],
      [x.total_quantity for x in person.getAvailableTimeSequence(
                  day=1,
                  from_date=DateTime(2008, 1, 1).earliestTime(),
                  to_date=DateTime(2008, 1, 1).latestTime())])

    available_time_movement_list = person.Person_getAvailableTimeMovementList(
                  from_date=DateTime(2008, 1, 1).earliestTime(),
                  to_date=DateTime(2008, 1, 1).latestTime())
    self.assertEqual(
        [(DateTime('2008/01/01 09:00'),
          DateTime('2008/01/01 18:00'),)],
        [(m.getStartDate(), m.getStopDate()) for m in
                        available_time_movement_list])

  @skip("Need to check if we want later to support this again. Drop support for now")
  def test_LeaveRequestOverlappingAfterGroupCalendar(self):
    group_calendar = self.portal.group_calendar_module.newContent(
                                  portal_type='Group Calendar')
    group_calendar_period = group_calendar.newContent(
                                  portal_type='Group Presence Period')
    group_calendar_period.setStartDate('2008/01/01 08:00')
    group_calendar_period.setStopDate('2008/01/01 18:00')
    group_calendar_period.setResourceValue(
          self.portal.portal_categories.calendar_period_type.type1)
    group_calendar.confirm()

    person = self.portal.person_module.newContent(portal_type='Person')
    assignment = self.portal.group_calendar_assignment_module.newContent(
                      specialise_value=group_calendar,
                      resource_value=self.portal.service_module.consulting_service,
                      start_date=DateTime(2008, 1, 1).earliestTime(),
                      stop_date=DateTime(2008, 1, 1).latestTime(),
                      destination_value=person)
    assignment.confirm()
    self.tic()
    leave_request = self.portal.leave_request_module.newContent(
                                  portal_type='Leave Request')
    leave_request_period = leave_request.newContent(
                                  portal_type='Leave Request Period')
    leave_request_period.setStartDate('2008/01/01 17:00')
    leave_request_period.setStopDate('2008/01/01 19:00')
    leave_request_period.setResourceValue(
          self.portal.portal_categories.calendar_period_type.type1)
    leave_request.setDestinationValue(person)
    leave_request.confirm()

    self.tic()

    self.assertEqual((17-8) * 60 * 60, person.getAvailableTime(
                            from_date=DateTime(2008, 1, 1).earliestTime(),
                            to_date=DateTime(2008, 1, 1).latestTime()))

    self.assertEqual([(17-8) * 60 * 60],
      [x.total_quantity for x in person.getAvailableTimeSequence(
                  day=1,
                  from_date=DateTime(2008, 1, 1).earliestTime(),
                  to_date=DateTime(2008, 1, 1).latestTime())])

    available_time_movement_list = person.Person_getAvailableTimeMovementList(
                  from_date=DateTime(2008, 1, 1).earliestTime(),
                  to_date=DateTime(2008, 1, 1).latestTime())
    self.assertEqual(
        [(DateTime('2008/01/01 08:00'),
          DateTime('2008/01/01 17:00'),)],
        [(m.getStartDate(), m.getStopDate()) for m in
                        available_time_movement_list])

  def test_2LeaveRequestOverlappingAfterGroupCalendar(self):
    group_calendar = self.portal.group_calendar_module.newContent(
                                  portal_type='Group Calendar')
    group_calendar_period = group_calendar.newContent(
                                  portal_type='Group Presence Period')
    group_calendar_period.setStartDate('2008/01/01 08:00')
    group_calendar_period.setStopDate('2008/01/01 18:00')
    group_calendar_period.setResourceValue(
          self.portal.portal_categories.calendar_period_type.type1)
    group_calendar.confirm()

    person = self.portal.person_module.newContent(portal_type='Person')
    assignment = self.portal.group_calendar_assignment_module.newContent(
                      specialise_value=group_calendar,
                      resource_value=self.portal.service_module.consulting_service,
                      start_date=DateTime(2008, 1, 1).earliestTime(),
                      stop_date=DateTime(2008, 1, 1).latestTime(),
                      destination_value=person)
    assignment.confirm()
    self.tic()
    leave_request = self.portal.leave_request_module.newContent(
                                  portal_type='Leave Request')
    leave_request_period_1 = leave_request.newContent(
                                  portal_type='Leave Request Period')
    leave_request_period_1.setStartDate('2008/01/01 09:00')
    leave_request_period_1.setStopDate('2008/01/01 10:00')
    leave_request_period_1.setResourceValue(
          self.portal.portal_categories.calendar_period_type.type1)
    leave_request_period_2 = leave_request.newContent(
                                  portal_type='Leave Request Period')
    leave_request_period_2.setStartDate('2008/01/01 12:00')
    leave_request_period_2.setStopDate('2008/01/01 13:00')
    leave_request_period_2.setResourceValue(
          self.portal.portal_categories.calendar_period_type.type1)
    leave_request.setDestinationValue(person)
    leave_request.confirm()

    self.tic()

    self.assertEqual((18-13 + 12-10 + 9-8) * 60 * 60, person.getAvailableTime(
                            from_date=DateTime(2008, 1, 1).earliestTime(),
                            to_date=DateTime(2008, 1, 1).latestTime()))

    self.assertEqual([(18-13 + 12-10 + 9-8) * 60 * 60],
      [x.total_quantity for x in person.getAvailableTimeSequence(
                  day=1,
                  from_date=DateTime(2008, 1, 1).earliestTime(),
                  to_date=DateTime(2008, 1, 1).latestTime())])

    available_time_movement_list = person.Person_getAvailableTimeMovementList(
                  from_date=DateTime(2008, 1, 1).earliestTime(),
                  to_date=DateTime(2008, 1, 1).latestTime())
    self.assertEqual(
        [(DateTime('2008/01/01 08:00'),
          DateTime('2008/01/01 09:00'),),
         (DateTime('2008/01/01 10:00'),
          DateTime('2008/01/01 12:00'),),
         (DateTime('2008/01/01 13:00'),
          DateTime('2008/01/01 18:00'),)],
        [(m.getStartDate(), m.getStopDate()) for m in
                        available_time_movement_list])

  def test_2ConsecutiveLeaveRequestOverlappingAfterGroupCalendar(self):
    group_calendar = self.portal.group_calendar_module.newContent(
                                  portal_type='Group Calendar')
    group_calendar_period = group_calendar.newContent(
                                  portal_type='Group Presence Period')
    group_calendar_period.setStartDate('2008/01/01 08:00')
    group_calendar_period.setStopDate('2008/01/01 18:00')
    group_calendar.confirm()

    person = self.portal.person_module.newContent(portal_type='Person')
    assignment = self.portal.group_calendar_assignment_module.newContent(
                      specialise_value=group_calendar,
                      resource_value=self.portal.service_module.consulting_service,
                      start_date=DateTime(2008, 1, 1).earliestTime(),
                      stop_date=DateTime(2008, 1, 1).latestTime(),
                      destination_value=person)
    assignment.confirm()
    self.tic()
    leave_request = self.portal.leave_request_module.newContent(
                                  portal_type='Leave Request')
    leave_request_period_1 = leave_request.newContent(
                                  portal_type='Leave Request Period')
    leave_request_period_1.setStartDate('2008/01/01 09:00')
    leave_request_period_1.setStopDate('2008/01/01 10:00')
    leave_request_period_1.setResourceValue(
          self.portal.service_module.consulting_service)
    leave_request_period_2 = leave_request.newContent(
                                  portal_type='Leave Request Period')
    leave_request_period_2.setStartDate('2008/01/01 10:00')
    leave_request_period_2.setStopDate('2008/01/01 11:00')
    leave_request_period_2.setResourceValue(
          self.portal.service_module.consulting_service)
    leave_request.setDestinationValue(person)
    leave_request.confirm()

    self.tic()

    self.assertEqual((18-11 + 9-8) * 60 * 60, person.getAvailableTime(
                            from_date=DateTime(2008, 1, 1).earliestTime(),
                            to_date=DateTime(2008, 1, 1).latestTime()))

    self.assertEqual([(18-11 + 9-8) * 60 * 60],
      [x.total_quantity for x in person.getAvailableTimeSequence(
                  day=1,
                  from_date=DateTime(2008, 1, 1).earliestTime(),
                  to_date=DateTime(2008, 1, 1).latestTime())])

    available_time_movement_list = person.Person_getAvailableTimeMovementList(
                  from_date=DateTime(2008, 1, 1).earliestTime(),
                  to_date=DateTime(2008, 1, 1).latestTime())
    self.assertEqual(
        [(DateTime('2008/01/01 08:00'),
          DateTime('2008/01/01 09:00'),),
         (DateTime('2008/01/01 11:00'),
          DateTime('2008/01/01 18:00'),),],
        [(m.getStartDate(), m.getStopDate()) for m in
                        available_time_movement_list])

  @skip("Need to check if we want later to support this again. Drop support for now")
  def test_2OverlappedLeaveRequestOverlappingAfterGroupCalendar(self):
    group_calendar = self.portal.group_calendar_module.newContent(
                                  portal_type='Group Calendar')
    group_calendar_period = group_calendar.newContent(
                                  portal_type='Group Presence Period')
    group_calendar_period.setStartDate('2008/01/01 08:00')
    group_calendar_period.setStopDate('2008/01/01 18:00')
    group_calendar_period.setResourceValue(
          self.portal.portal_categories.calendar_period_type.type1)
    group_calendar.confirm()

    person = self.portal.person_module.newContent(portal_type='Person')
    assignment = self.portal.group_calendar_assignment_module.newContent(
                      specialise_value=group_calendar,
                      resource_value=self.portal.service_module.consulting_service,
                      start_date=DateTime(2008, 1, 1).earliestTime(),
                      stop_date=DateTime(2008, 1, 1).latestTime(),
                      destination_value=person)
    assignment.confirm()
    self.tic()
    leave_request = self.portal.leave_request_module.newContent(
                                  portal_type='Leave Request')
    leave_request_period_1 = leave_request.newContent(
                                  portal_type='Leave Request Period')
    leave_request_period_1.setStartDate('2008/01/01 09:00')
    leave_request_period_1.setStopDate('2008/01/01 10:00')
    leave_request_period_1.setResourceValue(
          self.portal.portal_categories.calendar_period_type.type1)
    leave_request_period_2 = leave_request.newContent(
                                  portal_type='Leave Request Period')
    leave_request_period_2.setStartDate('2008/01/01 09:30')
    leave_request_period_2.setStopDate('2008/01/01 11:00')
    leave_request_period_2.setResourceValue(
          self.portal.portal_categories.calendar_period_type.type1)
    leave_request.setDestinationValue(person)
    leave_request.confirm()

    self.tic()

    self.assertEqual((18-11 + 9-8) * 60 * 60, person.getAvailableTime(
                            from_date=DateTime(2008, 1, 1).earliestTime(),
                            to_date=DateTime(2008, 1, 1).latestTime()))

    self.assertEqual([(18-11 + 9-8) * 60 * 60],
      [x.total_quantity for x in person.getAvailableTimeSequence(
                  day=1,
                  from_date=DateTime(2008, 1, 1).earliestTime(),
                  to_date=DateTime(2008, 1, 1).latestTime())])

    available_time_movement_list = person.Person_getAvailableTimeMovementList(
                  from_date=DateTime(2008, 1, 1).earliestTime(),
                  to_date=DateTime(2008, 1, 1).latestTime())
    self.assertEqual(
        [(DateTime('2008/01/01 08:00'),
          DateTime('2008/01/01 09:00'),),
         (DateTime('2008/01/01 11:00'),
          DateTime('2008/01/01 18:00'),),],
        [(m.getStartDate(), m.getStopDate()) for m in
                        available_time_movement_list])

  def test_GroupCalendarRepeatUntilPeriodicity(self):
    """Test that when group presence period is repeated until periodicity stop date.
    """
    node = self.portal.organisation_module.newContent(portal_type='Organisation',)

    group_calendar = self.portal.group_calendar_module.newContent(
       portal_type='Group Calendar')
    group_calendar_period = group_calendar.newContent(
       portal_type='Group Presence Period')

    # 2008/01/01 was a Tuesday
    group_calendar_period.setStartDate('2008/01/01 08:00:00 UTC')
    group_calendar_period.setStopDate('2008/01/01 18:00:00 UTC')
    group_calendar_period.setQuantity(10)
    group_calendar_period.setResourceValue(
       self.portal.portal_categories.calendar_period_type.type1)
    group_calendar_period.setPeriodicityWeekDayList(['Tuesday'])
    # Repeat for two weeks only
    group_calendar_period.setPeriodicityStopDate(DateTime('2008/01/09 00:00:00 UTC'))
    self.tic()

    assignment = self.portal.group_calendar_assignment_module.newContent(
       specialise_value=group_calendar,
       resource_value=self.portal.portal_categories.calendar_period_type.type1,
       start_date=DateTime('2008/01/01 08:00:00 UTC'),
       stop_date=DateTime('2008/01/31 20:00:00 UTC'), # repeat for 1 month
       destination_value=node)
    assignment.confirm()
    self.tic()

    # group calendar assignments is for one month, but since the presence period
    # is only for two weeks, this assignment only repeat twice.
    self.assertEqual([
      ( DateTime('2008/01/01 08:00:00 UTC'), DateTime('2008/01/01 18:00:00 UTC') ),
      ( DateTime('2008/01/08 08:00:00 UTC'), DateTime('2008/01/08 18:00:00 UTC') ), ],
      [ (m.getStopDate(), m.getStartDate()) for m in assignment.asMovementList() ] )

  def test_GroupCalendarWithoutPeriodicityStopDateRepeatUntilGroupCalendarAssignmentStopDate(self):
    """Test that when group presence period does not define periodicity stop date,
    the group calendar assignment repeats until the stop date of the group calendar assignment.
    """
    node = self.portal.organisation_module.newContent(portal_type='Organisation',)

    group_calendar = self.portal.group_calendar_module.newContent(
       portal_type='Group Calendar')
    group_calendar_period = group_calendar.newContent(
       portal_type='Group Presence Period')

    # 2008/01/01 was a Tuesday
    group_calendar_period.setStartDate('2008/01/01 08:00:00 UTC')
    group_calendar_period.setStopDate('2008/01/01 18:00:00 UTC')
    group_calendar_period.setQuantity(10)
    group_calendar_period.setResourceValue(
       self.portal.portal_categories.calendar_period_type.type1)
    group_calendar_period.setPeriodicityWeekDayList(['Tuesday'])
    self.tic()

    assignment = self.portal.group_calendar_assignment_module.newContent(
       specialise_value=group_calendar,
       resource_value=self.portal.portal_categories.calendar_period_type.type1,
       start_date=DateTime('2008/01/01 08:00:00 UTC'),
       stop_date=DateTime('2008/01/31 20:00:00 UTC'), # repeat for 1 month
       destination_value=node)
    assignment.confirm()
    self.tic()

    # in 2008/01 the Tuesday were:
    self.assertEqual([
      ( DateTime('2008/01/01 08:00:00 UTC'), DateTime('2008/01/01 18:00:00 UTC') ),
      ( DateTime('2008/01/08 08:00:00 UTC'), DateTime('2008/01/08 18:00:00 UTC') ),
      ( DateTime('2008/01/15 08:00:00 UTC'), DateTime('2008/01/15 18:00:00 UTC') ),
      ( DateTime('2008/01/22 08:00:00 UTC'), DateTime('2008/01/22 18:00:00 UTC') ),
      ( DateTime('2008/01/29 08:00:00 UTC'), DateTime('2008/01/29 18:00:00 UTC') ), ],
      [ (m.getStopDate(), m.getStartDate()) for m in assignment.asMovementList() ] )

  def test_GroupCalendarWithoutPeriodicityStopDateAndGroupCalendarAssignmentWithoutStopDateDoNotRepeat(self):
    """Test that when group presence period does not define periodicity stop
    date and group calendar assignment does not define stop date either the
    periodicity does not repeat.

    """
    node = self.portal.organisation_module.newContent(portal_type='Organisation',)

    group_calendar = self.portal.group_calendar_module.newContent(
       portal_type='Group Calendar')
    group_calendar_period = group_calendar.newContent(
       portal_type='Group Presence Period')

    group_calendar_period.setStartDate('2008/01/01 08:00:00 UTC')
    group_calendar_period.setStopDate('2008/01/01 18:00:00 UTC')
    group_calendar_period.setQuantity(10)
    group_calendar_period.setResourceValue(
       self.portal.portal_categories.calendar_period_type.type1)
    self.tic()

    assignment = self.portal.group_calendar_assignment_module.newContent(
       specialise_value=group_calendar,
       resource_value=self.portal.portal_categories.calendar_period_type.type1,
       start_date=DateTime('2008/01/01 08:00:00 UTC'),
       destination_value=node)
    assignment.confirm()
    self.tic()

    self.assertEqual([], assignment.asMovementList())


  def test_PersonModule_viewLeaveRequestReport(self):
    # in this test, type1 is the type for presences, type2 & type3 are types
    # for leaves.
    organisation = self.portal.organisation_module.newContent(
                                portal_type='Organisation',
                                group='my_group')

    group_calendar = self.portal.group_calendar_module.newContent(
                                  portal_type='Group Calendar')
    group_calendar_period = group_calendar.newContent(
                                  portal_type='Group Presence Period')
    group_calendar_period.setStartDate('2008/01/01 08:00')
    group_calendar_period.setStopDate('2008/01/01 18:00')
    group_calendar_period.setResourceValue(
          self.portal.portal_categories.calendar_period_type.type1)
    group_calendar.confirm()

    person1 = self.portal.person_module.newContent(
                                portal_type='Person',
                                title='Person 1',
                                career_reference='1',
                                subordination_value=organisation)
    assignment = self.portal.group_calendar_assignment_module.newContent(
                      specialise_value=group_calendar,
                      resource_value=self.portal.portal_categories.calendar_period_type.type1,
                      start_date=DateTime(2008, 1, 1).earliestTime(),
                      stop_date=DateTime(2008, 1, 1).latestTime(),
                      destination_value=person1)
    assignment.confirm()
    self.tic()
    leave_request1 = self.portal.leave_request_module.newContent(
                                  portal_type='Leave Request',
                                  destination_value=person1)
    leave_request1_period = leave_request1.newContent(
                                  portal_type='Leave Request Period')
    leave_request1_period.setStartDate('2008/01/01 09:00')
    leave_request1_period.setStopDate('2008/01/01 10:00')
    leave_request1_period.setResourceValue(
          self.portal.portal_categories.calendar_period_type.type2)
    leave_request1.confirm()

    person2 = self.portal.person_module.newContent(
                                portal_type='Person',
                                title='Person 2',
                                career_reference='2',
                                subordination_value=organisation)
    assignment = self.portal.group_calendar_assignment_module.newContent(
                      specialise_value=group_calendar,
                      resource_value=self.portal.portal_categories.calendar_period_type.type1,
                      start_date=DateTime(2008, 1, 1).earliestTime(),
                      stop_date=DateTime(2008, 1, 1).latestTime(),
                      destination_value=person2)
    assignment.confirm()
    self.tic()
    leave_request2 = self.portal.leave_request_module.newContent(
                                  portal_type='Leave Request',
                                  destination_value=person2)
    leave_request2_period1 = leave_request2.newContent(
                                  portal_type='Leave Request Period')
    leave_request2_period1.setStartDate('2008/01/01 09:00')
    leave_request2_period1.setStopDate('2008/01/01 10:00')
    leave_request2_period1.setResourceValue(
          self.portal.portal_categories.calendar_period_type.type2)
    leave_request2_period2 = leave_request2.newContent(
                                  portal_type='Leave Request Period')
    leave_request2_period2.setStartDate('2008/01/01 10:00')
    leave_request2_period2.setStopDate('2008/01/01 11:30')
    leave_request2_period2.setResourceValue(
          self.portal.portal_categories.calendar_period_type.type3)
    leave_request2.confirm()

    self.tic()

    # set request variables and render
    request_form = self.portal.REQUEST
    request_form['from_date'] = DateTime(2008, 1, 1)
    request_form['to_date'] = DateTime(2009, 1, 1)
    request_form['node_category'] = 'group/my_group'

    report_section_list = self.getReportSectionList(
                             self.portal.person_module,
                             'PersonModule_viewLeaveRequestReport')
    self.assertEqual(1, len(report_section_list))

    line_list = self.getListBoxLineList(report_section_list[0])
    data_line_list = [l for l in line_list if l.isDataLine()]
    self.assertEqual(2, len(data_line_list))

    self.assertEqual(data_line_list[0].column_id_list,
        ['person_career_reference', 'person_title',
         'calendar_period_type/type2', 'calendar_period_type/type3', 'total'])

    self.checkLineProperties(data_line_list[0],
                             person_career_reference='1',
                             person_title='Person 1',
                             total=1.0,
                             **{'calendar_period_type/type2': 1.0,})
    self.checkLineProperties(data_line_list[1],
                             person_career_reference='2',
                             person_title='Person 2',
                             total=2.5,
                             **{'calendar_period_type/type2': 1.0,
                                'calendar_period_type/type3': 1.5,})

    self.assertTrue(line_list[-1].isStatLine())
    self.checkLineProperties(line_list[-1],
                             total=3.5,
                             **{'calendar_period_type/type2': 2.0,
                                'calendar_period_type/type3': 1.5,})


def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestCalendar))
  return suite
