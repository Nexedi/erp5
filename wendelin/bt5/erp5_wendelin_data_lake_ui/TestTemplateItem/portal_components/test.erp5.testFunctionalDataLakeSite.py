##############################################################################
#
# Copyright (c) 2002-2020 Nexedi SA and Contributors. All Rights Reserved.
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
import unittest

from Products.ERP5Type.tests.ERP5TypeFunctionalTestCase import ERP5TypeFunctionalTestCase

class TestDataLakeSite(ERP5TypeFunctionalTestCase):
  foreground = 0
  run_only = "wendelin_data_lake_ui_zuite"

  def getBusinessTemplateList(self):
    return (
      'erp5_wendelin_data_lake_ui',
      'erp5_ui_test_core',
      'erp5_accounting',
      'erp5_test_result',
    )

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestDataLakeSite))
  return suite
