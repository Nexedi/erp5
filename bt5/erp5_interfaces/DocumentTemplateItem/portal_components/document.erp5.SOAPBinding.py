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

from AccessControl import ClassSecurityInfo
from Products.ERP5Type import PropertySheet
from Products.ERP5Type.Permissions import AccessContentsInformation
from Products.ERP5Type.Base import Base
import six
try:
  from spyne import MethodContext
except ImportError:
  pass
else:
  from spyne.application import Application
  from spyne.interface.wsdl import Wsdl11
  from spyne.protocol.soap import Soap11
  from spyne.server.http import HttpBase


class SOAPBinding(Base):

  meta_type = 'ERP5 SOAP Binding'
  portal_type = 'SOAP Binding'

  security = ClassSecurityInfo()
  security.declareObjectProtected(AccessContentsInformation)

  property_sheets = ( PropertySheet.CategoryCore
                    , PropertySheet.DublinCore
                    , PropertySheet.SOAPBinding
                    )

  _service_class_dict = {}

  security.declarePrivate('registerServiceClass')
  @classmethod
  def registerServiceClass(cls, service_class):
    path = '%s.%s' % (service_class.__module__, service_class.__name__)
    cls._service_class_dict[path] = service_class

  @classmethod
  def getRegisteredServiceClassItemList(cls):
    return sorted(('%s (%s)' % (v.__name__, v.__module__), k)
                  for k, v in six.iteritems(cls._service_class_dict))

  security.declarePrivate('getListItemUrl')
  def getListItemUrl(self, *args):
    return self.getId() + '/view'

  def _getServer(self):
    try:
      serial, server = self._v_server # pylint: disable=access-member-before-definition
      if serial == self._p_serial:
        return server
    except AttributeError:
      pass
    server = HttpBase(Application(
      map(self._service_class_dict.__getitem__, self.getServiceClassList()),
      self.getTargetNamespace(),
      in_protocol=Soap11(), out_protocol=Soap11()))
    self._v_server = self._p_serial, server
    return server

  def __call__(self, REQUEST): # pylint: disable=arguments-differ
    server = self._getServer()
    if REQUEST.method == 'GET':
      wsdl = Wsdl11(server.app.interface)
      wsdl.build_interface_document(self.absolute_url())
      return wsdl.get_interface_document()
    REQUEST.stdin.seek(0)
    if hasattr(MethodContext, 'SERVER'):
      ctx = MethodContext(server, MethodContext.SERVER)
    else: # BBB spyne < 2.12
      ctx = MethodContext(server) # pylint: disable=no-value-for-parameter
    ctx.in_string = REQUEST.stdin
    ctx, = server.generate_contexts(ctx)
    ctx.udc = self
    server.get_in_object(ctx)
    server.get_out_object(ctx)
    server.get_out_string(ctx)
    return ''.join(ctx.out_string)

try:
  from spyne.service import ServiceBase
  from spyne.decorator import rpc
  from spyne.model.complex import Iterable
  from spyne.model.primitive import Integer
  from spyne.model.primitive import Unicode
except ImportError:
  pass
else:
  class HelloWorldService(ServiceBase):
    @rpc(Unicode, Integer, _returns=Iterable(Unicode))
    def say_hello(ctx, name, times): # pylint: disable=no-self-argument
      '''
      Docstrings for service methods appear as documentation in the wsdl
      <b>what fun</b>
      @param name the name to say hello to
      @param the number of times to say hello
      @return the completed array
      '''
      return [u'Hello, %s' % name] * times

  SOAPBinding.registerServiceClass(HelloWorldService)
