##############################################################################
#
# Copyright (c) 2026 Nexedi SA and Contributors. All Rights Reserved.
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

import io
import json

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase

from erp5.component.module.JsonRpc import (
  JsonRpcType,
)


# We essentially need to implement a MCP Client to test the server properly.
# With py3 we could just use the Py MCP SDK.
# - but we also need to test invalid requests and that they are handled correctly.

# response = self.initialize()
# self.assertEqual(response, ...)
# self.initialized()  # send notification
# 
# response = self.tool_list()
# self.assertEqual(response, ...)
#
# response = self.tool_call()
# self.assertEqual(response, ...)

# all these messages need to use something like
#   self.sendMCPMessage(...) -> reponse

class TestMCPService(ERP5TypeTestCase):
  def afterSetUp(self):
    self.document_to_remove_list = []
    portal_callables = self.portal.portal_callables
    self.tool_create_person = self.newContent(portal_callables, **TOOL_CREATE_PERSON)
    self.mcp_service = self.newContent(
      self.portal.portal_web_services,
      portal_type="MCP Service",
      reference="mcpTest",
      id="mcpTest",
      tool="Create a new Person | %s" % self.tool_create_person.getId(),
    )
    self.tic()

  def beforeTearDown(self):
    for document in self.document_to_remove_list:
      path = document.getRelativeUrl()
      container, _, object_id = path.rpartition('/')
      try:
        parent = self.portal.unrestrictedTraverse(container)
      except KeyError:
        continue
      else:
        if object_id in parent.objectIds():
          parent.manage_delObjects([object_id])
    self.commit()
 
  def newContent(self, parent, *args, **kwargs):
    document = parent.newContent(*args, **kwargs)
    self.document_to_remove_list.append(document)
    return document
  
  def sendJsonRpcMessage(self, msg_type):
    self.publish(
      self.mcp_service.getPath(),
      request_method="POST",
      user="ERP5TypeTestCase",
      stdin=io.BytesIO(json.dumps({}).encode()),
    )

  def test_sampleTest(self):
    self.assertEqual(self.tool_create_person.getId(), "mcptest_createPerson")


TOOL_CREATE_PERSON = dict(
  portal_type="MCP Tool",
  id="mcptest_createPerson",
  reference="mcptest_createPerson",
  parameter_signature="reference, first_name=None, last_name=None",
  input_signature="reference: str, first_name: str=None, last_name: str=None",
  output_signature="output: str",
  callable_type="script",
  body=r"""portal = context.getPortalObject()
try:
  person = portal.person_module.newContent(
    portal_type="Person", reference=reference, first_name=first_name, last_name=last_name
  )
except Exception as e:
  return "Could not create person: %s" % e
person.validate()
return "Succesfully created person %s" % reference"""
)