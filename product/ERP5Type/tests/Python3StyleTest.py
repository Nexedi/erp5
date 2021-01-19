
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

from Products.ERP5Type.tests.utils import addUserToDeveloperRole
from Products.ERP5Type.tests.Python3StyleTestCase import Python3StyleTestCase


class Python3StyleTest(Python3StyleTestCase):
  """Run a coding style test for product defined by
  TESTED_PRODUCT environment variable, that is set by
  ERP5BusinessTemplateCodingStyleTestSuite in test/__init__.py
  """
  pass

def test_suite():
  suite = unittest.TestSuite()
  tested_product = os.environ['TESTED_PRODUCT']

  testclass = type(
      'Python3StyleTest %s' % tested_product,

      (Python3StyleTest,),
      {
          'tested_product': tested_product,
          # currently, jsl based test_javascript_lint report too many false positives.
          'test_javascript_lint': None,
      },
  )


  # required to create content in portal_components
  addUserToDeveloperRole('ERP5TypeTestCase')

  suite.addTest(unittest.makeSuite(testclass))
  return suite
