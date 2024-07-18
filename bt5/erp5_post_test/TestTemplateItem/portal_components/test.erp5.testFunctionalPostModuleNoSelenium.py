##############################################################################
#
# Copyright (c) 2002-2017 Nexedi SA and Contributors. All Rights Reserved.
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
##############################################################################
import unittest
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase

class TestHTMLPostLogic(ERP5TypeTestCase):
  """
  A Sample Test Class
  """

  def getTitle(self):
    return "SampleTest"

  def getBusinessTemplateList(self):
    """
    Tuple of Business Templates we need to install
    """
    return ('erp5_base',)

  def afterSetUp(self):
    """
    This is ran before anything, used to set the environment

    # here, you can create the categories and objects your test will depend on
    """

  def test_01_sampleTest(self):
    """
    A Sample Test

    For the method to be called during the test,
    its name must start with 'test'.
    The '_01_' part of the name is not mandatory,
    it just allows you to define in which order the tests are to be launched.
    Tests methods (self.assert... and self.failIf...)
    are defined in /usr/lib/python/unittest.py.
    """
    portal = self.getPortal()
    post_module = portal.post_module

    post_1 = post_module.newContent(portal_type='HTML Post', id="post_1")
    post_2 = post_module.newContent(portal_type='HTML Post', id="post_2")
    post_3 = post_module.newContent(portal_type='HTML Post', id="post_3")

    post_1.setFollowUpValue(post_3)
    post_2.setFollowUpValue(post_3)
    post_2.setPredecessorValue(post_1)

    post_2_predecessor = post_2.getPredecessorValueList()[0]
    post_2_follow_up = post_2.getFollowUpValueList()[0]
    self.assertEqual(post_2_predecessor.getTitle(), post_1.getTitle())
    self.assertEqual(post_2_follow_up.getTitle(), post_3.getTitle())

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestHTMLPostLogic))
  return suite