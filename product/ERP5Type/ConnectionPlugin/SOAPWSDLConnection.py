##############################################################################
#
# Copyright (c) 2009 Nexedi SA and Contributors. All Rights Reserved.
#                    Vincent Pelletier <vincent@nexedi.com>
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

import SOAPpy
from Products.AGProjects.patches import SOAPpy_WSDL as WSDL
from AccessControl.SecurityInfo import allow_class, allow_module

# Authentication classes.
#  These are SOAP authentication classes.
#  They are supposed to be instanciated and then transmited to WebServiceTool
#  in order to create a connection.

class AuthenticationBase(object):
  """
    Authentication API.

    As SOAP doens't provide a standard authentication method, authentication
    plugins must be written for virtualy each SOAP services.
    This API intends to provide hooks for authentication purposes.

    Overload the methods you need (default methods are NO-OPs).
  """

  def ProxyParameterDictHook(self):
    """
      Return a dictionary of extra parameters to provide to WSDL.Proxy .
    """
    return {}

  def AfterConnectionHook(self, connection):
    """
      This hook is called upon connection. It can be used to exchange
      credentials with remote server.
    """
    pass

class NullAuthentication(AuthenticationBase):
  """
    NO-OP authentication.
  """
  pass

class HeaderAuthentication(AuthenticationBase):
  """
    Authentication implementation for authentication mechanism based on known
    credentials. Those credentials are put in SOAP packet header, in "auth"
    XML block.
  """
  def __init__(self, auth):
    self._auth = auth

  def ProxyParameterDictHook(self):
    return {'auth': self._auth}

allow_class(HeaderAuthentication)

# Wrappers for SOAPpy objects.
#  These wrappers will be returned by the connector, and can be used in
#  restricted scripts.

class WSDLConnection(object):

  __allow_access_to_unprotected_subobjects__ = True

  def __init__(self, wsdl, credentials, service):
    self._wsdl = wsdl
    self._credentials = credentials
    self._service = service
    self._port_dict = {}

  def __getitem__(self, port_name):
    """
      Connect to requested port.
    """
    try:
      result = self._port_dict[port_name]
    except KeyError:
      kw = self._credentials.ProxyParameterDictHook()
      result = self._port_dict[port_name] = PortWrapper(WSDL.Proxy(
        self._wsdl, service=self._service, port=port_name, **kw))
      self._credentials.AfterConnectionHook(result)
    return result

class PortWrapper(object):

  __allow_access_to_unprotected_subobjects__ = True

  def __init__(self, port):
    self._port = port

  def __getattr__(self, method_id):
    return getattr(self._port, method_id)

class SOAPWSDLConnection:
  """
    Holds a SOAP connection described by a WSDL file.
    This uses a patch from NGNPro over SOAPpy's WSDL.py file, allowing the
    WSDL to describe multiple ports and adding support for authentication by
    header.

    Note: SOAP doesn't describe a standard way to handle authentication, so it
    might not fit your needs.
  """

  def __init__(self, url, user_name=None, password=None, credentials=None,
               service=None):
    """
      url (string)
        The url of the WSDL file describing an underlying SOAP interface.
      user_name (string or None)
      password (string is None)
        The transport-level (http) credentials to use.
      credentials (AuthenticationBase subclass instance or None)
        The interface-level (SOAP) credentials to use.
      service (string or None)
        The WSDL-described service to connect to.
    """
    self.url = url
    self._user_name = user_name
    self._password = password
    if credentials is None:
      credentials = NullAuthentication()
    self._credentials = credentials
    self._service = service

  def connect(self):
    # TODO: caching of wsdl parsing
    wsdl = SOAPpy.wstools.WSDLTools.WSDLReader().loadFromURL(self.url)
    # TODO: transport (http) level authentication using self._user_name and
    # self._password
    return WSDLConnection(wsdl, self._credentials, self._service)

