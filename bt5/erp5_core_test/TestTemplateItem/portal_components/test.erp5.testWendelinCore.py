# -*- coding:utf-8 -*-
##############################################################################
#
# Copyright (C) 2021 Nexedi SA and Contributors.
#                    Kirill Smelkov <kirr@nexedi.com>
#
# This program is free software: you can Use, Study, Modify and Redistribute
# it under the terms of the GNU General Public License version 3, or (at your
# option) any later version, as published by the Free Software Foundation.
#
# You can also Link and Combine this program with other software covered by
# the terms of any of the Free Software licenses or any of the Open Source
# Initiative approved licenses and Convey the resulting work. Corresponding
# source of such a combination shall include the source code for all other
# software used.
#
# This program is distributed WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
# See COPYING file for full licensing terms.
# See https://www.nexedi.com/licensing for rationale and options.
#
##############################################################################

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from wendelin.bigarray.array_zodb import ZBigArray
from numpy.testing import assert_array_equal
import transaction

# Minimal test to make sure that wendelin.core works at all.
class TestWendelinCoreBasic(ERP5TypeTestCase):

  def test(self):
    # create the array in temporary "root" placeholder.
    # NOTE we need created objects to enter ZODB for real, but
    # newContent(temp_object=True) creates an object with ._p_jar=None
    zroot  = self.portal.newContent()
    zroot.zarray = A = ZBigArray(shape=(4,), dtype=int)
    self.commit()
    self.assertIsNotNone(zroot._p_jar)  # zroot enters ZODB
    self.assertIsNotNone(A._p_jar)      # zarray ----//----

    # the array must initially read as all zeros
    a = A[:]
    assert_array_equal(a, [0,0,0,0])
    b = A[:]
    assert_array_equal(b, [0,0,0,0])

    # we can assign items in a view, and the assignment propagates to another view
    a[2] = 1
    assert_array_equal(a, [0,0,1,0])
    assert_array_equal(b, [0,0,1,0])

    # on abort local changes are reverted
    transaction.abort()
    assert_array_equal(a, [0,0,0,0])
    assert_array_equal(b, [0,0,0,0])

    # on commit local changes are saved into ZODB
    a[1] = 3
    b[2] = 4
    assert_array_equal(a, [0,3,4,0])
    assert_array_equal(b, [0,3,4,0])
    self.commit()
    transaction.abort() # just in case
    c = A[:]
    assert_array_equal(a, [0,3,4,0])
    assert_array_equal(b, [0,3,4,0])
    assert_array_equal(c, [0,3,4,0])
