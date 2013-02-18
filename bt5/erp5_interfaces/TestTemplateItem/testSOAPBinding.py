# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2012 Nexedi SA and Contributors. All Rights Reserved.
#          Julien Muchembled <jm@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly advised to contract a Free Software
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
##############################################################################

import unittest
import SOAPpy
from Products.ERP5Type.tests.backportUnittest import expectedFailure
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5.Document.SOAPBinding import SOAPBinding
from spyne.service import ServiceBase
from spyne.decorator import srpc
from spyne.model.complex import Iterable
from spyne.model.primitive import Integer
from spyne.model.primitive import Unicode


class HelloWorldService(ServiceBase):
    @srpc(Unicode, Integer, _returns=Iterable(Unicode))
    def say_hello(name, times):
        '''
        Docstrings for service methods appear as documentation in the wsdl
        <b>what fun</b>
        @param name the name to say hello to
        @param the number of times to say hello
        @return the completed array
        '''

        for i in range(times):
            yield u'Hello, %s' % name

SOAPBinding.registerServiceClass(HelloWorldService)


class TestSoapBinding(ERP5TypeTestCase):

  def getBusinessTemplateList(self):
    return 'erp5_interfaces',

  def createBinding(self, target_namespace, service_class):
    return self.portal.portal_interfaces.newContent(
      self._testMethodName, 'SOAP Binding',
      target_namespace=target_namespace,
      service_class='%s.%s' % (service_class.__module__,
                               service_class.__name__))

  @expectedFailure
  def testSpyneHelloExample(self):
    tns = 'spyne.examples.hello.soap'
    binding = self.createBinding(tns, HelloWorldService)
    self.commit()
    result, = SOAPpy.SOAPProxy(binding.absolute_url()).say_hello(
      name=u'Jérôme', times=5)
    self.assertEqual(result, [u'Hello, Jérôme'] * 5)


def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestSoapBinding))
  return suite
