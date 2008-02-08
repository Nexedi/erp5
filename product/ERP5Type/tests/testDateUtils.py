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

# Make it possible to use Globals.get_request
class DummyRequest(dict):
  __allow_access_to_unprotected_subobjects__ = 1
  def set(self, k, v):
    self[k] = v

global request
request = DummyRequest()

def get_request():
  global request
  return request

# apply patch (before it's imported by other modules)
import Globals
Globals.get_request = get_request


# Initialize ERP5Form Product to load monkey patches
from Testing import ZopeTestCase
ZopeTestCase.installProduct('ERP5Type')


from DateTime import DateTime
from Products.ERP5Type.DateUtils import addToDate

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

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestDateUtils))
  return suite
