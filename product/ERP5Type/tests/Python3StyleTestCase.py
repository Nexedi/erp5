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

from future.utils import raise_
import tarfile
import os
from glob import glob
from subprocess import Popen, PIPE

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Testing import ZopeTestCase
from Acquisition import aq_base

class Python3StyleTestCase(ERP5TypeTestCase):
  """Test case to test coding style in products.

  Subclasses must override:
    * getTestedBusinessTemplateList to list business templates to test.
  """
  def getBusinessTemplateList(self):
    """
    Return the list of required business templates.
    Override this method in implementation class.
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

  def afterSetUp(self):
    self.login()

  def test_raiseFixApplied(self):
    """check fixer is applied on products
    """
    HERE = os.path.dirname(__file__)
    path = os.path.normpath(glob('%s/../../%s' %(HERE, os.environ['TESTED_PRODUCT']))[0])
    error_list = []
    try:
        stdout = Popen(["2to3", "--fix", "raise", str(path)], stdout=PIPE).communicate()
    except OSError, e:
        raise_(OSError, '%r\n%r' % (os.environ, e))
    if stdout[0]:
        error_list.append((path, stdout[0]))
    if error_list:
         message = '\n'.join(["%s\n%s\n" % error for error in error_list])
         self.fail(message)

  def test_importFixApplied(self):
    """check fixer is applied on products
    """
    HERE = os.path.dirname(__file__)
    path = os.path.normpath(glob('%s/../../%s' %(HERE, os.environ['TESTED_PRODUCT']))[0])
    error_list = []
    try:
        stdout = Popen(["2to3", "--fix", "import", str(path)], stdout=PIPE).communicate()
    except OSError, e:
        raise_(OSError, '%r\n%r' % (os.environ, e))
    if stdout[0]:
        error_list.append((path, stdout[0]))
    if error_list:
         message = '\n'.join(["%s\n%s\n" % error for error in error_list])
         self.fail(message)


