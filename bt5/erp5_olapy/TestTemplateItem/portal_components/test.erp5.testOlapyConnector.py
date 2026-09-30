##############################################################################
#
# Copyright (c) 2017 Nexedi SA and Contributors. All Rights Reserved.
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

from StringIO import StringIO
import xml.etree.ElementTree as ET

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase


class TestOlapy(ERP5TypeTestCase):

  def publish(self, *args, **kw):
    """ add (partial) support for publish in live tests.

     patch Zope.Testing.ZopeTestCase.functional publish, with support for request within a request

     TODO: integrate in live test class.
    """
    from zope.security.management import endInteraction
    from zope.security.management import restoreInteraction
    endInteraction()
    module_cache_set = getattr(self.portal.REQUEST, '_module_cache_set', None)
    try:
      return super(TestOlapy, self).publish(*args, **kw)
    finally:
      restoreInteraction()
      if module_cache_set is not None:
        self.portal.REQUEST._module_cache_set = module_cache_set

  def afterSetUp(self):
    self.olapy_connector = self.portal.portal_web_services.newContent(
        portal_type='Olapy Connector')

  def test_Execute(self):
    dummy_execute_message = """<?xml version="1.0" encoding="UTF-8"?>
    <SOAP-ENV:Envelope
      xmlns:ns0="http://schemas.xmlsoap.org/soap/envelope/"
      xmlns:ns1="urn:schemas-microsoft-com:xml-analysis"
      xmlns:ns2="olapy.core.services.models"
      xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
      xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/">
      <SOAP-ENV:Header/>
      <ns0:Body>
        <Execute xmlns="urn:schemas-microsoft-com:xml-analysis">
          <ns2:Command>
            <ns2:Statement>SELECT {[Dim].[Dim].[column0].[data1],
                                   [Dim].[Dim].[column0].[data2]} ON COLUMNS FROM ERP5</ns2:Statement>
          </ns2:Command>
          <ns2:Properties>
            <ns1:PropertyList>
              <ns1:AxisFormat>TupleFormat</ns1:AxisFormat>
              <ns1:Format>Multidimensional</ns1:Format>
            </ns1:PropertyList>
          </ns2:Properties>
        </Execute>
      </ns0:Body>
    </SOAP-ENV:Envelope>
    """
    ret = self.publish(
      self.olapy_connector.absolute_url_path(),
      request_method="POST",
      handle_errors=False,
      stdin=StringIO(dummy_execute_message))

    # this can be parsed
    tree = ET.fromstring(ret.getBody())

    # and looks like a SOAP/XMLA response
    response = tree.find('.//{urn:schemas-microsoft-com:xml-analysis}ExecuteResponse')
    self.assertIsNotNone(response)

    # returning two cells
    self.assertEqual(
      2,
      len(tree.findall('.//{urn:schemas-microsoft-com:xml-analysis:mddataset}Cell'
                       '/{urn:schemas-microsoft-com:xml-analysis:mddataset}Value')))

