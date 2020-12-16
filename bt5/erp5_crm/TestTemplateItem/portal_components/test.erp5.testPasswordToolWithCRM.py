# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2004 Nexedi SARL and Contributors. All Rights Reserved.
#          Aurelien Calonne <aurel@nexedi.com>
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

from erp5.component.test.testPasswordTool import TestPasswordTool

class TestPasswordToolWithCRM(TestPasswordTool):
  """
  Test reset of password
  """
  def getBusinessTemplateList(self):
    return ('erp5_base', 'erp5_crm',)

  def getTitle(self):
    return "Password Tool with CRM"

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestPasswordToolWithCRM))
  return suite
