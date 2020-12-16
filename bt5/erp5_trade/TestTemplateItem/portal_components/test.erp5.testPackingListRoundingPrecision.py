##############################################################################
#
# Copyright (c) 2007 Nexedi SARL and Contributors. All Rights Reserved.
#          Courteaud Romain <romain@nexedi.com>
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
from erp5.component.test.testPackingList import TestPackingList

class TestPackingListRoundingPrecision(TestPackingList):
  """
  Test that Order/Packing List haven't rounding issues with float values.
  The idea was contributed by Lukasz Nowak
  """
  default_quantity = 59.333333333333336

  def getTitle(self):
    return "Packing List Rounding Precision"

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestPackingListRoundingPrecision))
  return suite
