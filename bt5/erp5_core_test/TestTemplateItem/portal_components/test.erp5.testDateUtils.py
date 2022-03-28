# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2007 Nexedi SARL and Contributors. All Rights Reserved.
#          Jerome Perrin <jerome@nexedi.com>
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

from DateTime import DateTime
from erp5.component.module.DateUtils import addToDate, getIntervalListBetweenDates, \
    atTheEndOfPeriod, getClosestDate
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase

class TestDateUtils(unittest.TestCase):
  """
  Tests DateUtils
  """

  timezone = 'GMT+7'

  def getTitle(self):
    return "Date Utils"

  def test_integer_add_to_date(self):
    date = DateTime('2000/01/01 %s' % self.timezone)
    self.assertEqual(DateTime('2000/01/01 00:01:30 %s' % self.timezone).toZone('UTC').ISO(),
                              addToDate(date, second=90).toZone('UTC').ISO())
    self.assertEqual(DateTime('2000/01/01 01:30:00 %s' % self.timezone).toZone('UTC').ISO(),
                              addToDate(date, minute=90).toZone('UTC').ISO())
    self.assertEqual(DateTime('2000/01/04 18:00:00 %s' % self.timezone).toZone('UTC').ISO(),
                              addToDate(date, hour=90).toZone('UTC').ISO())
    self.assertEqual(DateTime('2000/03/31 %s' % self.timezone).toZone('UTC').ISO(),
                              addToDate(date, day=90).toZone('UTC').ISO())
    self.assertEqual(DateTime('2007/07/01 %s' % self.timezone).toZone('UTC').ISO(),
                              addToDate(date, month=90).toZone('UTC').ISO())
    self.assertEqual(DateTime('2090/01/01 %s' % self.timezone).toZone('UTC').ISO(),
                              addToDate(date, year=90).toZone('UTC').ISO())

  def test_negative_add_to_date(self):
    date = DateTime('2000/01/01 %s' % self.timezone)
    self.assertEqual(DateTime('1999/12/31 23:59:59 %s' % self.timezone).toZone('UTC').ISO(),
                              addToDate(date, second=-1).toZone('UTC').ISO())
    self.assertEqual(DateTime('1999/12/31 23:59:00 %s' % self.timezone).toZone('UTC').ISO(),
                              addToDate(date, minute=-1).toZone('UTC').ISO())
    self.assertEqual(DateTime('1999/12/31 23:00:00 %s' % self.timezone).toZone('UTC').ISO(),
                              addToDate(date, hour=-1).toZone('UTC').ISO())
    self.assertEqual(DateTime('1999/12/31 00:00:00 %s' % self.timezone).toZone('UTC').ISO(),
                              addToDate(date, day=-1).toZone('UTC').ISO())
    self.assertEqual(DateTime('1999/12/01 00:00:00 %s' % self.timezone).toZone('UTC').ISO(),
                              addToDate(date, month=-1).toZone('UTC').ISO())
    self.assertEqual(DateTime('1999/01/01 %s' % self.timezone).toZone('UTC').ISO(),
                              addToDate(date, year=-1).toZone('UTC').ISO())

  def test_float_add_to_date(self):
    date = DateTime('2000/01/01 %s' % self.timezone)
    self.assertEqual(DateTime('2000/01/01 %s' % self.timezone).toZone('UTC').ISO(),
                              addToDate(date, second=0.5).toZone('UTC').ISO())
    self.assertEqual(DateTime('2000/01/01 00:00:30 %s' % self.timezone).toZone('UTC').ISO(),
                              addToDate(date, minute=0.5).toZone('UTC').ISO())
    self.assertEqual(DateTime('2000/01/01 00:30:00 %s' % self.timezone).toZone('UTC').ISO(),
                              addToDate(date, hour=0.5).toZone('UTC').ISO())
    self.assertEqual(DateTime('2000/01/01 12:00:00 %s' % self.timezone).toZone('UTC').ISO(),
                              addToDate(date, day=0.5).toZone('UTC').ISO())
    self.assertEqual(DateTime('2000/01/16 12:00:00 %s' % self.timezone).toZone('UTC').ISO(),
                              addToDate(date, month=0.5).toZone('UTC').ISO())
    self.assertEqual(DateTime('2000/07/01 %s' % self.timezone).toZone('UTC').ISO(),
                              addToDate(date, year=0.5).toZone('UTC').ISO())

  def test_complex_float_add_to_date(self):
    complex_date = DateTime('2004/03/16 01:23:54 %s' % self.timezone)
    self.assertEqual(DateTime('2004/03/16 01:23:54 %s' % self.timezone).toZone('UTC').ISO(),
                   addToDate(complex_date, second=0.5).toZone('UTC').ISO())
    self.assertEqual(DateTime('2004/03/16 01:24:24 %s' % self.timezone).toZone('UTC').ISO(),
                   addToDate(complex_date, minute=0.5).toZone('UTC').ISO())
    self.assertEqual(DateTime('2004/03/16 01:53:54 %s' % self.timezone).toZone('UTC').ISO(),
                   addToDate(complex_date, hour=0.5).toZone('UTC').ISO())
    self.assertEqual(DateTime('2004/03/16 13:23:54 %s' % self.timezone).toZone('UTC').ISO(),
                   addToDate(complex_date, day=0.5).toZone('UTC').ISO())
    self.assertEqual(DateTime('2004/03/31 13:23:54 %s' % self.timezone).toZone('UTC').ISO(),
                   addToDate(complex_date, month=0.5).toZone('UTC').ISO())
    self.assertEqual(DateTime('2004/09/16 01:23:54 %s' % self.timezone).toZone('UTC').ISO(),
                   addToDate(complex_date, year=0.5).toZone('UTC').ISO())

  def test_interval_list_between_dates(self):
    from_date = DateTime('2008/10/23')
    to_date = DateTime('2008/11/03')
    aggregation_level = 'day'
    interval_list_dict = getIntervalListBetweenDates(from_date=from_date,
                                        to_date=to_date,
                                        keys={aggregation_level:True})
    date_list = interval_list_dict.get(aggregation_level)
    self.assertEqual(len(date_list), 12)
    for index, date in enumerate(date_list):
      if index == 0:
        self.assertEqual(date, '2008-10-23')
      elif index == 1:
        self.assertEqual(date, '2008-10-24')
      elif index == 2:
        self.assertEqual(date, '2008-10-25')
      elif index == 3:
        self.assertEqual(date, '2008-10-26')
      elif index == 4:
        self.assertEqual(date, '2008-10-27')
      elif index == 5:
        self.assertEqual(date, '2008-10-28')
      elif index == 6:
        self.assertEqual(date, '2008-10-29')
      elif index == 7:
        self.assertEqual(date, '2008-10-30')
      elif index == 8:
        self.assertEqual(date, '2008-10-31')
      elif index == 9:
        self.assertEqual(date, '2008-11-01')
      elif index == 10:
        self.assertEqual(date, '2008-11-02')
      elif index == 11:
        self.assertEqual(date, '2008-11-03')

  def test_atTheEndOfPeriod(self):
    date = DateTime('2008/01/01 00:00:00 Universal')
    self.assertEqual(atTheEndOfPeriod(date, 'year').pCommonZ(), 'Jan. 1, 2009 12:00 am Universal')
    self.assertEqual(atTheEndOfPeriod(date, 'month').pCommonZ(), 'Feb. 1, 2008 12:00 am Universal')
    self.assertEqual(atTheEndOfPeriod(date, 'week').pCommonZ(), 'Jan. 7, 2008 12:00 am Universal')
    self.assertEqual(atTheEndOfPeriod(date, 'day').pCommonZ(), 'Jan. 2, 2008 12:00 am Universal')
    # Switch to summer time
    self.assertEqual('Apr. 6, 2008 12:00 am US/Eastern',
      atTheEndOfPeriod(DateTime('2008/04/05 23:59:59 US/Eastern'), 'day').pCommonZ())
    self.assertEqual('Apr. 7, 2008 12:00 am US/Eastern',
      atTheEndOfPeriod(DateTime('2008/04/06 00:00:00 US/Eastern'), 'day').pCommonZ())
    self.assertEqual('Apr. 7, 2008 12:00 am US/Eastern',
      atTheEndOfPeriod(DateTime('2008/04/06 23:59:59 US/Eastern'), 'day').pCommonZ())
    self.assertEqual('May 1, 2008 12:00 am US/Eastern',
      atTheEndOfPeriod(DateTime('2008/04/01 US/Eastern'), 'month').pCommonZ())
    # Switch to winter time
    self.assertEqual('Oct. 26, 2008 12:00 am US/Eastern',
      atTheEndOfPeriod(DateTime('2008/10/25 23:59:59 US/Eastern'), 'day').pCommonZ())
    self.assertEqual('Oct. 27, 2008 12:00 am US/Eastern',
      atTheEndOfPeriod(DateTime('2008/10/26 00:00:00 US/Eastern'), 'day').pCommonZ())
    self.assertEqual('Oct. 27, 2008 12:00 am US/Eastern',
      atTheEndOfPeriod(DateTime('2008/10/26 23:59:59 US/Eastern'), 'day').pCommonZ())
    self.assertEqual('Nov. 1, 2008 12:00 am US/Eastern',
      atTheEndOfPeriod(DateTime('2008/10/01 US/Eastern'), 'month').pCommonZ())

  def test_getClosestDate(self):
    target_date = DateTime('2008/08/15 00:00:00 GMT+2')
    self.assertEqual('Aug. 1, 2008 12:00 am GMT+2',
      getClosestDate(target_date=target_date, precision='month', before=True).pCommonZ())
    self.assertEqual('Sep. 1, 2008 12:00 am GMT+2',
      getClosestDate(target_date=target_date, precision='month', before=False).pCommonZ())
    date = DateTime('2008/01/10 00:00:00 GMT-2')
    self.assertEqual('Aug. 10, 2008 12:00 am GMT-2',
      getClosestDate(date=date, target_date=target_date, precision='month', before=True).pCommonZ())
    self.assertEqual('Sep. 10, 2008 12:00 am GMT-2',
      getClosestDate(date=date, target_date=target_date, precision='month', before=False).pCommonZ())


class TestPinDateTime(ERP5TypeTestCase):
  def test_pinDateTime(self):
    actual_begin_date = DateTime()
    datetime = DateTime('2001/01/01 01:01:01')
    fixed_date_with_timezone = DateTime('2002/02/02 02:02:02 GMT+2')

    self.pinDateTime(datetime)
    self.assertEqual(DateTime(), datetime)
    self.assertEqual(DateTime('2002/02/02 02:02:02 GMT+2'), fixed_date_with_timezone)

    self.unpinDateTime()
    self.assertGreaterEqual(DateTime(), actual_begin_date)

  def test_pinDateTime_context_manager(self):
    actual_begin_date = DateTime()
    datetime = DateTime('2001/01/01 01:01:01')

    with self.pinDateTime(datetime):
      self.assertEqual(DateTime(), datetime)
    self.assertGreaterEqual(DateTime(), actual_begin_date)


def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestDateUtils))
  suite.addTest(unittest.makeSuite(TestPinDateTime))
  return suite
