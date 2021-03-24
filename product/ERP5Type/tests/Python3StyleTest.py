
# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010 Nexedi SA and Contributors. All Rights Reserved.
#          Jean-Paul Smets <jp@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly adviced to contract a Free Software
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

import os
import unittest
from glob import glob
from subprocess import check_output, CalledProcessError

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase


class Python3StyleTest(ERP5TypeTestCase):
  """ Check coding style against python3 in the dir
  defined by the TESTED_PRODUCT environment variable
  We run 2to3 for each fixer applied to check for diff which means
  that regression has been introduced
  """

  def getBusinessTemplateList(self):
    """
    No need to install anything
    """
    return ()

  def getTestedBusinessTemplateList(self):
    """
    Return the list of business templates to be
    checked for consistency. By default, return
    the last business template of the
    list of installed business templates.
    """
    return self.getBusinessTemplateList()[-1:]

  def _testFixer(self, fixer_name):
    """check fixer is applied on given path
    """
    HERE = os.path.dirname(__file__)
    if os.environ['TESTED_PRODUCT'] == "bt5":
        path = HERE + '/../../../'
    else:
        path = HERE + '/../../'
    path = os.path.normpath(glob(path + os.environ['TESTED_PRODUCT'])[0])
    error_list = []
    try:
        stdout = check_output(["2to3", "--fix", fixer_name, str(path)])
    except CalledProcessError, e:
        raise CalledProcessError('%r\n%r' % (os.environ, e))
    if stdout:
        error_list.append((path, stdout))
    if error_list:
         message = '\n'.join(["%s\n%s\n" % error for error in error_list])
         self.fail(message)

  def test_raiseFixApplied(self):
    self._testFixer('raise')

  def test_importFixApplied(self):
    self._testFixer('import')


def test_suite():
  suite = unittest.TestSuite()
  tested_product = os.environ['TESTED_PRODUCT']

  testclass = type(
      'Python3StyleTest %s' % tested_product,

      (Python3StyleTest,),
      {
          'tested_product': tested_product,
      },
  )


  suite.addTest(unittest.makeSuite(testclass))
  return suite
