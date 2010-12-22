##############################################################################
#
# Copyright (c) 2007 Nexedi SA and Contributors. All Rights Reserved.
#                     Jerome Perrin <jerome@nexedi.com>
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

import unittest
import xmlrpclib

from Products.ERP5Wizard.Tool.WizardTool import GeneratorCall


class TestGeneratorCall(unittest.TestCase):
  """Tests Generator Call
  """

  def test_dump(self):
    call = GeneratorCall()
    dumped = call.dump()
    self.failUnless(isinstance(dumped, str))
    load = xmlrpclib.loads(dumped)
    self.failUnless(isinstance(load, tuple))
    self.assertEquals(len(load), 2)
    self.assertEquals(load[1], 'GeneratorAnswer')

    self.failUnless(isinstance(load[0], tuple))
    self.assertEquals(len(load[0]), 1)
    server_response_dict = load[0][0]
    self.failUnless(isinstance(server_response_dict, dict))


  def test_dump_load(self):
    call = GeneratorCall(data='Foo')
    self.assertEquals(call['data'], 'Foo')
    dumped = call.dump()
    self.failUnless(isinstance(dumped, str))

    # reread it in a new call
    read = GeneratorCall()
    read.load(dumped)
    self.assertEquals(read['data'], 'Foo')


def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestGeneratorCall))
  return suite

