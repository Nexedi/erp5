##############################################################################
#
# Copyright (c) 2006 Nexedi SARL and Contributors. All Rights Reserved.
#          Sebastien Robin <seb@nexedi.com>
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

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.UnrestrictedMethod import super_user
from AccessControl.SecurityManagement import newSecurityManager, \
        getSecurityManager, setSecurityManager
from AccessControl.users import nobody
from AccessControl import Unauthorized
from DateTime import DateTime
from erp5.component.module.DateUtils import addToDate


class AlarmTestCase(ERP5TypeTestCase):
  # year/month/day hour:minute:second
  date_format = '%i/%i/%i %i:%i:%d GMT+0100'

  def getBusinessTemplateList(self):
    return ('erp5_base',)

  def newAlarm(self, **kw):
    """
    Create an empty alarm, owned by system user, like when the alarm is
    installed from a business template.
    """
    sm = getSecurityManager()
    newSecurityManager(None, nobody)
    try:
      with super_user():
        return self.getAlarmTool().newContent(**kw)
    finally:
      setSecurityManager(sm)


class TestAlarm(AlarmTestCase):

  def test_01_HasEverything(self):
    # Test if portal_alarms was created
    self.assertNotEqual(self.portal._getOb('portal_alarms', None), None)
    self.assertNotEqual(self.portal.portal_types.getTypeInfo('Alarm Tool'), None)
    # ... and that it should be subscribed by default
    self.assertTrue(self.portal.portal_alarms.isSubscribed())

  def test_02_Initialization(self):
    """
    Test some basic things right after the creation
    """
    alarm = self.newAlarm()
    self.tic()
    now = DateTime()
    date = addToDate(now,day=1)
    alarm.setPeriodicityStartDate(date)
    self.assertEqual(alarm.getAlarmDate(), None)
    alarm.setEnabled(True)
    self.assertEqual(alarm.getAlarmDate(), date)
    alarm.setNextAlarmDate(current_date=now) # This should not do change the alarm date
    self.assertEqual(alarm.getAlarmDate(),date)

  def test_14_NewActiveProcess(self):
    alarm = self.newAlarm(enabled=True)
    active_process = alarm.newActiveProcess()
    self.assertEqual('Active Process', active_process.getPortalType())
    self.assertEqual(alarm, active_process.getCausalityValue())
    self.tic()
    self.assertEqual(active_process, alarm.getLastActiveProcess())

  def test_15_FailedAlarmsDoNotBlockFutureAlarms(self):
    sense_method_id = 'Alarm_testSenseMethod'
    skin_folder_id = 'custom'
    skin_folder = self.getPortal().portal_skins[skin_folder_id]
    skin_folder.manage_addProduct['PythonScripts'].manage_addPythonScript(id=sense_method_id)
    # Make the sense method fail
    skin_folder[sense_method_id].ZPythonScript_edit('*args,**kw', 'raise Exception')
    del skin_folder
    alarm = self.newAlarm(enabled=True)
    self.tic()
    alarm.setActiveSenseMethodId(sense_method_id)
    self.assertEqual(alarm.isActive(), 0)
    alarm.activeSense()
    try:
      self.tic()
    except RuntimeError:
      try:
        # Check that the alarm is not considered active, although there is a remaining activity.
        self.assertEqual(alarm.hasActivity(), 1)
        self.assertEqual(alarm.isActive(), 0)
        self.assertEqual(alarm.getLastActiveProcess(), None)
      finally:
        self.portal.portal_activities.manageClearActivities(keep=0)
    else:
      self.fail('Tic did not raise though activity was supposed to fail')
    # Make the sense method succeed and leave a trace
    self.getPortal().portal_skins[skin_folder_id][sense_method_id].ZPythonScript_edit('*args,**kw', 'context.newActiveProcess()')
    alarm.activeSense()
    self.tic()
    # Chen that the second alarm execution did happen
    self.assertNotEqual(alarm.getLastActiveProcess(), None)

  def test_16_uncatalog(self):
    """
    Check that deleting an alarm uncatalogs it.
    """
    alarm = self.newAlarm(enabled=True)
    self.tic()

    now = DateTime()
    date = addToDate(now, day=1)
    alarm.setPeriodicityStartDate(date)
    self.tic()
    self.assertEqual(alarm.getAlarmDate(), date)

    # This should not do change the alarm date
    alarm.setNextAlarmDate(current_date=now)
    self.tic()
    self.assertEqual(alarm.getAlarmDate(), date)

    # Delete the alarm
    a_tool = self.getAlarmTool()
    alarm_uid = alarm.getUid()
    a_tool.manage_delObjects(uids=[alarm_uid])
    self.tic()
    # Check that related entry was removed
    sql_connection = self.getSQLConnection()
    sql = 'select * from alarm where uid=%s' % alarm_uid
    result = sql_connection.manage_test(sql)
    self.assertEqual(0, len(result))

  def test_17_tic(self):
    """
    Make sure that the tic method on alarm is working
    """
    alarm = self.newAlarm()
    alarm.setEnabled(True)
    self.tic()

    sense_method_id = 'Alarm_testSenseMethodForTic'
    skin_folder_id = 'custom'
    skin_folder = self.getPortal().portal_skins[skin_folder_id]
    skin_folder.manage_addProduct['PythonScripts']\
        .manage_addPythonScript(id=sense_method_id)
    # Make the sense method fail
    skin_folder[sense_method_id].ZPythonScript_edit('*args,**kw',
          'context.setDescription("a")')
    del skin_folder
    alarm.setActiveSenseMethodId(sense_method_id)
    self.tic()
    alarm_tool = self.getPortal().portal_alarms
    # Nothing should happens yet
    alarm_tool.tic()
    self.tic()
    self.assertIn(alarm.getDescription(), (None, ''))
    now = DateTime()
    date = addToDate(now, day=-1)
    alarm.setPeriodicityStartDate(date)
    alarm.setPeriodicityMinuteFrequency(1)
    self.tic()
    alarm_tool.tic()
    self.tic()
    self.assertEqual(alarm.getDescription(), 'a')

  def test_automatic_solve(self):
    alarm = self.newAlarm()
    alarm.setEnabled(True)
    alarm.setAutomaticSolve(True)
    alarm.setPeriodicityStartDate(addToDate(DateTime(), day=-1))
    alarm.setPeriodicityMinuteFrequency(1)

    sense_method_id = 'Alarm_testSenseMethodWithAutomaticSolve'
    skin_folder_id = 'custom'
    skin_folder = self.getPortal().portal_skins[skin_folder_id]
    skin_folder.manage_addProduct['PythonScripts']\
        .manage_addPythonScript(id=sense_method_id)
    skin_folder[sense_method_id].ZPythonScript_edit('fixit=0, *args,**kw',
          'if fixit: context.setDescription("fixed")')
    alarm.setActiveSenseMethodId(sense_method_id)
    self.tic()

    self.portal.portal_alarms.tic()
    self.tic()

    self.assertEqual(alarm.getDescription(), 'fixed')

  def test_18_alarm_activities_execution_order(self):
    """
    Make sure active process created by an alarm get the right tag
    """
    alarm = self.newAlarm()
    # Create script that generate active process
    sense_method_id = 'Alarm_createActiveProcessSenseMethod'
    skin_folder_id = 'custom'
    skin_folder = self.getPortal().portal_skins[skin_folder_id]
    skin_folder.manage_addProduct['PythonScripts']\
        .manage_addPythonScript(id=sense_method_id)
    skin_folder[sense_method_id].ZPythonScript_edit('*args,**kw',
          'context.newActiveProcess()')
    # update alarm properties
    alarm.edit(alarm_notification_mode="always",
               active_sense_method_id=sense_method_id,
               enabled=True)
    self.tic()
    alarm.activeSense()
    self.commit()
    tag_set = set()
    def assertSingleTagAndMethodItemsEqual(expected_method_list):
      method_id_list = []
      for m in self.getActivityTool().getMessageList():
        method_id_list.append(m.method_id)
        if m.method_id == 'notify':
          tag_set.add(m.activity_kw.get('after_tag'))
        elif m.method_id in (sense_method_id, 'immediateReindexObject'):
          tag_set.add(m.activity_kw.get('tag'))
      self.assertCountEqual(method_id_list, expected_method_list)
      self.assertEqual(len(tag_set), 1, tag_set)
    # check tags after activeSense
    assertSingleTagAndMethodItemsEqual(['notify', sense_method_id])
    # execute alarm sense script and check tags
    self.getActivityTool().manageInvoke(alarm.getPhysicalPath(), sense_method_id)
    self.commit()
    assertSingleTagAndMethodItemsEqual(['notify', 'immediateReindexObject'])
    self.tic()

  def test_19_ManualInvocation(self):
    """
    test if an alarm can be invoked directly by the user securely,
    and if the results are identical when allowed.
    """
    alarm = self.newAlarm()
    # Create script that generate active process
    sense_method_id = 'Alarm_setBogusLocalProperty'
    skin_folder_id = 'custom'
    skin_folder = self.portal.portal_skins[skin_folder_id]
    skin_folder.manage_addProduct['PythonScripts']\
        .manage_addPythonScript(id=sense_method_id)
    skin_folder[sense_method_id].ZPythonScript_edit('*args,**kw',
          'context.setProperty("bogus", str(context.showPermissions()))')

    # update alarm properties
    alarm.edit(active_sense_method_id=sense_method_id,
               enabled=False)
    self.tic()

    # Make a normal user.
    uf = self.getPortal().acl_users
    uf._doAddUser('normal', '', ['Member', 'Auditor'], [])
    user = uf.getUserById('normal').__of__(uf)

    # Check the pre-conditions.
    self.assertEqual(alarm.getProperty('bogus', None), None)
    self.assertEqual(alarm.getEnabled(), False)
    sm = getSecurityManager()
    newSecurityManager(None, user)

    # Non-managers must not be able to invoke a disabled alarm.
    self.assertRaises(Unauthorized, alarm.activeSense)
    self.assertRaises(Unauthorized, alarm.activeSense, fixit=1)

    # Non-managers must not be able to invoke the automatic fixation.
    setSecurityManager(sm)
    alarm.setEnabled(True)
    self.assertEqual(alarm.getEnabled(), True)
    newSecurityManager(None, user)
    self.assertRaises(Unauthorized, alarm.activeSense, fixit=1)

    # Now, check that everybody can invoke an enabled alarm manually.
    setSecurityManager(sm)
    correct_answer = str(alarm.showPermissions())
    self.assertNotEqual(correct_answer, None)

    alarm.activeSense()
    self.tic()
    self.assertEqual(alarm.getProperty('bogus', None), correct_answer)
    alarm.setProperty('bogus', None)
    self.assertEqual(alarm.getProperty('bogus', None), None)

    newSecurityManager(None, user)
    alarm.activeSense()
    self.tic()
    self.assertEqual(alarm.getProperty('bogus', None), correct_answer)
    setSecurityManager(sm)
    alarm.setProperty('bogus', None)

    # Check that Manager can invoke an alarm freely.
    alarm.activeSense(fixit=1)
    self.tic()
    self.assertEqual(alarm.getProperty('bogus', None), correct_answer)
    alarm.setProperty('bogus', None)
    self.assertEqual(alarm.getProperty('bogus', None), None)

    alarm.setEnabled(False)
    self.assertEqual(alarm.getEnabled(), False)

    alarm.activeSense()
    self.tic()
    self.assertEqual(alarm.getProperty('bogus', None), correct_answer)
    alarm.setProperty('bogus', None)
    self.assertEqual(alarm.getProperty('bogus', None), None)

    alarm.activeSense(fixit=1)
    self.tic()
    self.assertEqual(alarm.getProperty('bogus', None), correct_answer)
    alarm.setProperty('bogus', None)
    self.assertEqual(alarm.getProperty('bogus', None), None)

  def test_20_UndefinedPeriodicityStartDate(self):
    """
    Test that getAlarmDate does not crash when PeriodicityStartDate is not set.
    """
    alarm = self.newAlarm(enabled=True)
    # Test sanity check.
    self.assertEqual(alarm.getPeriodicityStartDate(), None)
    # Actual test.
    self.assertEqual(alarm.getAlarmDate(), None)

  def test_21_AlarmCatalogPresence(self):
    """Check that alarm date is properly stored in catalog upon first reindexation"""
    date = DateTime().earliestTime()
    alarm = self.newAlarm(enabled=True, periodicity_start_date=date)
    self.tic()
    self.assertEqual(alarm.getAlarmDate(), date)
    alarm_list = alarm.Alarm_zGetAlarmDate(uid=alarm.getUid())
    self.assertEqual(1, len(alarm_list))
    catalog_alarm_date = alarm_list[0].alarm_date
    self.assertEqual(date.toZone('UTC'), catalog_alarm_date)

  def test_21a_AlarmCatalogPresenceDoubleReindex(self):
    """Check that alarm date is properly stored in catalog"""
    date = DateTime().earliestTime()
    alarm = self.newAlarm(enabled=True, periodicity_start_date=date)
    self.tic()
    alarm.recursiveReindexObject()
    self.tic()
    self.assertEqual(alarm.getAlarmDate(), date)
    alarm_list = alarm.Alarm_zGetAlarmDate(uid=alarm.getUid())
    self.assertEqual(1, len(alarm_list))
    catalog_alarm_date = alarm_list[0].alarm_date
    self.assertEqual(date.toZone('UTC'), catalog_alarm_date)

  def test_21b_AlarmCatalogPresenceWithInitialEmptyStartDate(self):
    """Check that alarm date is properly stored in catalog if
       initially the periodicity start date was not there and
       then set later"""
    date = DateTime().earliestTime()
    alarm = self.newAlarm(enabled=True, periodicity_start_date=None)
    self.tic()
    alarm_list = alarm.Alarm_zGetAlarmDate(uid=alarm.getUid())
    self.assertEqual(None, alarm_list[0].alarm_date)
    alarm.edit(periodicity_start_date=date)
    self.tic()
    alarm_list = alarm.Alarm_zGetAlarmDate(uid=alarm.getUid())
    self.assertEqual(date.toZone('UTC'), alarm_list[0].alarm_date)


class TestPeriodicity(AlarmTestCase):

  def checkDate(self,alarm,*args):
    """
    the basic test
    """
    for date in args[:-1]:
      self.assertEqual(alarm.getAlarmDate(),date)
      alarm.setNextAlarmDate(current_date=date)
    self.assertEqual(alarm.getAlarmDate(),args[-1])

  def test_03_EveryHour(self):
    alarm = self.newAlarm(enabled=True)
    now = DateTime()
    date = addToDate(now, day=2)
    alarm.setPeriodicityStartDate(date)
    alarm.setPeriodicityHourFrequency(1)
    self.tic()
    alarm.setNextAlarmDate(current_date=now)
    self.assertEqual(alarm.getAlarmDate(), date)
    now = addToDate(now,day=2)
    alarm.setNextAlarmDate(current_date=now)
    next_date = addToDate(date,hour=1)
    self.assertEqual(alarm.getAlarmDate(),next_date)
    now = addToDate(now,hour=1,minute=5)
    alarm.setNextAlarmDate(current_date=now)
    next_date = addToDate(next_date,hour=1)
    self.assertEqual(alarm.getAlarmDate(),next_date)
    # check if manual invoking does not break getAlarmDate() result.
    alarm.activeSense()
    self.assertEqual(alarm.getAlarmDate(),next_date)

  def test_04_Every3Hours(self):
    alarm = self.newAlarm(enabled=True)
    now = DateTime().toZone('UTC')
    hour_to_remove = now.hour() % 3
    now = addToDate(now,hour=-hour_to_remove)
    date = addToDate(now,day=2)
    alarm.setPeriodicityStartDate(date)
    alarm.setPeriodicityHourFrequency(3)
    self.tic()
    alarm.setNextAlarmDate(current_date=now)
    self.assertEqual(alarm.getAlarmDate(),date)
    now = addToDate(now,day=2)
    alarm.setNextAlarmDate(current_date=now)
    next_date = addToDate(date,hour=3)
    self.assertEqual(alarm.getAlarmDate(),next_date)
    now = addToDate(now,hour=3,minute=7,second=4)
    alarm.setNextAlarmDate(current_date=now)
    next_date = addToDate(next_date,hour=3)
    self.assertEqual(alarm.getAlarmDate(),next_date)

  def test_05_SomeHours(self):
    right_first_date = DateTime(self.date_format  % (2006,10,6,15,00,00))
    now = DateTime(self.date_format               % (2006,10,6,15,00,00))
    right_second_date = DateTime(self.date_format % (2006,10,6,21,00,00))
    right_third_date = DateTime(self.date_format  % (2006,10,7,6,00,00))
    right_fourth_date = DateTime(self.date_format % (2006,10,7,10,00,00))
    alarm = self.newAlarm(enabled=True)
    hour_list = (6,10,15,21)
    alarm.setPeriodicityStartDate(now)
    alarm.setPeriodicityHourList(hour_list)
    self.tic()
    self.assertEqual(alarm.getAlarmDate(),right_first_date)
    alarm.setNextAlarmDate(current_date=right_first_date)
    self.assertEqual(alarm.getAlarmDate(),right_second_date)
    alarm.setNextAlarmDate(current_date=right_second_date)
    self.assertEqual(alarm.getAlarmDate(),right_third_date)
    alarm.setNextAlarmDate(current_date=right_third_date)
    self.assertEqual(alarm.getAlarmDate(),right_fourth_date)

  def test_06_EveryDayOnce(self):
    now = DateTime(self.date_format               % (2006,10,6,10,00,00))
    right_first_date = DateTime(self.date_format  % (2006,10,6,10,00,00))
    right_second_date = DateTime(self.date_format % (2006,10,7,10,00,00))
    right_third_date = DateTime(self.date_format  % (2006,10,8,10,00,00))
    alarm = self.newAlarm(enabled=True)
    alarm.setPeriodicityStartDate(now)
    alarm.setPeriodicityDayFrequency(1)
    alarm.setPeriodicityHourList((10,))
    self.tic()
    self.assertEqual(alarm.getAlarmDate(),right_first_date)
    alarm.setNextAlarmDate(current_date=right_first_date)
    self.assertEqual(alarm.getAlarmDate(),right_second_date)
    alarm.setNextAlarmDate(current_date=right_second_date)
    self.assertEqual(alarm.getAlarmDate(),right_third_date)

  def test_07_Every3DaysSomeHours(self):
    """- every 3 days at 14 and 15 and 17"""
    right_first_date = DateTime(self.date_format % (2006,10,6,14,00,00))
    right_second_date = DateTime(self.date_format  % (2006,10,6,15,00,00))
    right_third_date = DateTime(self.date_format  % (2006,10,6,17,00,00))
    right_fourth_date = DateTime(self.date_format  % (2006,10,9,14,00,00))
    alarm = self.newAlarm(enabled=True)
    alarm.setPeriodicityStartDate(right_first_date)
    alarm.setPeriodicityDayFrequency(3)
    alarm.setPeriodicityHourList((14,15,17))
    self.tic()
    self.assertEqual(alarm.getAlarmDate(),right_first_date)
    alarm.setNextAlarmDate(current_date=right_first_date)
    self.assertEqual(alarm.getAlarmDate(),right_second_date)
    alarm.setNextAlarmDate(current_date=right_second_date)
    self.assertEqual(alarm.getAlarmDate(),right_third_date)
    alarm.setNextAlarmDate(current_date=right_third_date)
    self.assertEqual(alarm.getAlarmDate(),right_fourth_date)

  def test_07a_Every4DaysSomeHours(self):
    """- every 4 days at 14 and 15 and 17"""
    right_first_date = DateTime(self.date_format % (2006,10,7,13,00,00))
    right_second_date = DateTime(self.date_format  % (2006,10,8,14,00,00))
    right_third_date = DateTime(self.date_format  % (2006,10,8,15,00,00))
    right_fourth_date = DateTime(self.date_format  % (2006,10,8,17,00,00))
    right_fifth_date = DateTime(self.date_format  % (2006,10,12,14,00,00))
    alarm = self.newAlarm(enabled=True)
    alarm.setPeriodicityStartDate(right_first_date)
    alarm.setPeriodicityDayFrequency(4)
    alarm.setPeriodicityHourList((14,15,17))
    self.tic()
    self.assertEqual(alarm.getAlarmDate(),right_first_date)
    alarm.setNextAlarmDate(current_date=right_first_date)
    self.assertEqual(alarm.getAlarmDate(),right_second_date)
    alarm.setNextAlarmDate(current_date=right_second_date)
    self.assertEqual(alarm.getAlarmDate(),right_third_date)
    alarm.setNextAlarmDate(current_date=right_third_date)
    self.assertEqual(alarm.getAlarmDate(),right_fourth_date)
    alarm.setNextAlarmDate(current_date=right_fourth_date)
    self.assertEqual(alarm.getAlarmDate(),right_fifth_date)

  def test_08_SomeWeekDaysSomeHours(self):
    """- every monday and friday, at 6 and 15"""
    right_first_date = DateTime(self.date_format  % (2006,9,27,6,00,00))
    right_second_date = DateTime(self.date_format  % (2006,9,29,6,00,00))
    right_third_date = DateTime(self.date_format  % (2006,9,29,15,00,00))
    right_fourth_date = DateTime(self.date_format  % (2006,10,2,6,00,00))
    alarm = self.newAlarm(enabled=True)
    self.tic()
    alarm.setPeriodicityStartDate(right_first_date)
    alarm.setPeriodicityWeekDayList(('Monday','Friday'))
    alarm.setPeriodicityHourList((6,15))
    self.checkDate(alarm, right_first_date, right_second_date, right_third_date, right_fourth_date)

  def test_09_SomeMonthDaysSomeHours(self):
    """- every 1st and 15th every month, at 12 and 14"""
    right_first_date = DateTime(self.date_format  % (2006,10,1,12,00,00))
    right_second_date = DateTime(self.date_format  % (2006,10,1,14,00,00))
    right_third_date = DateTime(self.date_format  % (2006,10,15,12,00,00))
    right_fourth_date = DateTime(self.date_format  % (2006,10,15,14,00,00))
    alarm = self.newAlarm(enabled=True)
    alarm.setPeriodicityStartDate(right_first_date)
    alarm.setPeriodicityMonthDayList((1,15))
    alarm.setPeriodicityHourList((12,14))
    self.tic()
    self.checkDate(alarm, right_first_date, right_second_date, right_third_date, right_fourth_date)

  def test_10_OnceEvery2Month(self):
    """- every 1st day of every 2 month, at 6"""
    right_first_date = DateTime(self.date_format  % (2006,10,1,6,00,00))
    right_second_date = DateTime(self.date_format  % (2006,12,1,6,00,00))
    right_third_date = DateTime(self.date_format  % (2007,2,1,6,00,00))
    alarm = self.newAlarm(enabled=True)
    alarm.setPeriodicityStartDate(right_first_date)
    alarm.setPeriodicityMonthDayList((1,))
    alarm.setPeriodicityMonthFrequency(2)
    alarm.setPeriodicityHourList((6,))
    self.tic()
    self.checkDate(alarm, right_first_date, right_second_date, right_third_date)

  def test_11_EveryDayOnceWeek41And42(self):
    right_first_date = DateTime(self.date_format  % (2006,10,1,6,00,00))
    right_second_date = DateTime(self.date_format  % (2006,10,9,6,00,00))
    right_third_date = DateTime(self.date_format  % (2006,10,10,6,00,00))
    right_fourth_date = DateTime(self.date_format  % (2006,10,11,6,00,00))
    alarm = self.newAlarm(enabled=True)
    alarm.setPeriodicityStartDate(right_first_date)
    alarm.setPeriodicityHourList((6,))
    alarm.setPeriodicityWeekList((41,43))
    self.tic()
    self.checkDate(alarm, right_first_date, right_second_date, right_third_date,right_fourth_date)

  def test_week_and_month_impossible_combination(self):
    alarm = self.newAlarm(enabled=True)
    alarm.setPeriodicityStartDate(DateTime(2000, 1, 1))
    # week 41 can not be in January
    alarm.setPeriodicityWeekList((41, ))
    alarm.setPeriodicityMonthList((1, ))
    self.tic()
    # next alarm date never advance
    self.checkDate(alarm, DateTime(2000, 1, 1), DateTime(2000, 1, 1), DateTime(2000, 1, 1),)

  def test_12_Every5Minutes(self):
    alarm = self.newAlarm(enabled=True)
    now = DateTime()
    minute_to_remove = now.minute() % 5
    now = addToDate(now,minute=-minute_to_remove)
    date = addToDate(now,day=2)
    alarm.setPeriodicityStartDate(date)
    alarm.setPeriodicityMinuteFrequency(5)
    self.tic()
    alarm.setNextAlarmDate(current_date=now)
    self.assertEqual(alarm.getAlarmDate(),date)
    now = addToDate(now,day=2)
    alarm.setNextAlarmDate(current_date=now)
    next_date = addToDate(date,minute=5)
    self.assertEqual(alarm.getAlarmDate(),next_date)
    now = addToDate(now,minute=5,second=14)
    alarm.setNextAlarmDate(current_date=now)
    next_date = addToDate(next_date,minute=5)
    self.assertEqual(alarm.getAlarmDate(),next_date)

  def test_13_EveryMinute(self):
    alarm = self.newAlarm(enabled=True)
    now = DateTime()
    date = addToDate(now,hour=2)
    alarm.setPeriodicityStartDate(now)
    alarm.setPeriodicityMinuteFrequency(1)
    self.tic()
    alarm.setNextAlarmDate(current_date=date)
    self.assertEqual(alarm.getAlarmDate(),date)

  def test_week_day_item_list(self):
    alarm = self.newAlarm()
    self.assertEqual(
      [(label.message, label.domain, value)
       for (label, value) in alarm.getWeekDayItemList()],
      [
        ('Sunday', 'erp5_ui','Sunday'),
        ('Monday', 'erp5_ui', 'Monday'),
        ('Tuesday', 'erp5_ui', 'Tuesday'),
        ('Wednesday', 'erp5_ui', 'Wednesday'),
        ('Thursday', 'erp5_ui', 'Thursday'),
        ('Friday', 'erp5_ui', 'Friday'),
        ('Saturday', 'erp5_ui', 'Saturday'),
      ],
    )

  def test_month_item_list(self):
    alarm = self.newAlarm()
    self.assertEqual(
      [(label.message, label.domain, value)
      for (label, value) in alarm.getMonthItemList()],
      [
        ('January', 'erp5_ui', 1),
        ('February', 'erp5_ui', 2),
        ('March', 'erp5_ui', 3),
        ('April', 'erp5_ui', 4),
        ('May', 'erp5_ui', 5),
        ('June', 'erp5_ui', 6),
        ('July', 'erp5_ui', 7),
        ('August', 'erp5_ui', 8),
        ('September', 'erp5_ui', 9),
        ('October', 'erp5_ui', 10),
        ('November', 'erp5_ui', 11),
        ('December', 'erp5_ui', 12),
      ],
    )
