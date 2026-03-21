##############################################################################
# coding:utf-8
# Copyright (c) 2026 Nexedi SA and Contributors. All Rights Reserved.
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

from AccessControl import ModuleSecurityInfo


class JsonRpcError(Exception):
  def __init__(self, code, message, data=None, request_id=None):
    Exception.__init__(self, message)
    self.code = code
    self.message = message
    self.data = data
    self.request_id = request_id
  
  def asdict(self):
    err = {"code": self.code, "message": self.message}
    if self.data is not None:
      err['data'] = self.data
    return err
  
  def asjsonrpc(self):
    return {"jsonrpc": "2.0", "error": self.asdict(), "id": self.request_id}


class JsonRpcParseError(JsonRpcError):
  """Invalid JSON was received by the server.
  An error occurred on the server while parsing the JSON text"""

  def __init__(self, *args, **kw):
    JsonRpcError.__init__(self, -32700, "Parse error", *args, **kw)


class JsonRpcInvalidRequestError(JsonRpcError):
  """The JSON sent is not a valid Request object."""

  def __init__(self, *args, **kw):
    JsonRpcError.__init__(self, -32600, "Invalid Request", *args, **kw)


class JsonRpcMethodNotFoundError(JsonRpcError):
  """The method does not exist / is not available."""

  def __init__(self, *args, **kw):
    JsonRpcError.__init__(self, -32601, "Method not found", *args, **kw)


class JsonRpcInvalidParamsError(JsonRpcError):
  """Invalid method parameter(s)."""

  def __init__(self, *args, **kw):
    JsonRpcError.__init__(self, -32602, "Invalid params", *args, **kw)


class JsonRpcInternalError(JsonRpcError):
  """Internal JSON-RPC error."""

  def __init__(self, *args, **kw):
    JsonRpcError.__init__(self, -32603, "Internal error", *args, **kw)


# TODO Add URL_ELICITATION_REQUIRED error
#   https://github.com/modelcontextprotocol/modelcontextprotocol/blob/bb676f3/schema/2025-11-25/schema.ts#L183C14-L183C38


ModuleSecurityInfo(__name__).declarePublic(
  JsonRpcError.__name__,
  JsonRpcParseError.__name__,
  JsonRpcInvalidRequestError.__name__,
  JsonRpcMethodNotFoundError.__name__,
  JsonRpcInvalidParamsError.__name__,
  JsonRpcInternalError.__name__,
)


class JsonRpcType(object):
  REQUEST = "request"
  RESPONSE = "response"
  NOTIFICATION = "notification"

  @staticmethod
  def classify(message):
    if "method" in message:
      if "id" in message:
        return JsonRpcType.REQUEST
      else:
        return JsonRpcType.NOTIFICATION
    if "id" in message:
      return JsonRpcType.RESPONSE
    raise ValueError("Invalid JSON-RPC message")