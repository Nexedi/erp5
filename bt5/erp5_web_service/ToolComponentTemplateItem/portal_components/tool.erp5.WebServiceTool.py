##############################################################################
#
# Copyright (c) 2006-2009 Nexedi SA and Contributors. All Rights Reserved.
#                    Ivan Tyagov <ivan@nexedi.com>
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

from zLOG import LOG, WARNING
from AccessControl import ClassSecurityInfo
from Products.ERP5Type.Globals import InitializeClass
from Products.ERP5Type.Tool.BaseTool import BaseTool
from Products.ERP5Type import Permissions
import six


class WebServiceConnectionError(Exception):
  """Error when connecting
  """


connection_plugin_registry = {}

def registerConnectionPlugin(name, klass, ignore_duplicate=False):
  if not ignore_duplicate:
    if name in connection_plugin_registry:
      raise ValueError('The connection plugin %r has already been registered in the registry %r' % (name, connection_plugin_registry))
  connection_plugin_registry[name] = klass

# Import and register known connection plugins
# Others should call registerConnectionPlugin directly to register themselves.
handler_module_dict = {
  'xml-rpc': 'XMLRPCConnection',
  'soap': 'SOAPConnection',
  'soap_wsdl': 'SOAPWSDLConnection',
  'sftp' : "SFTPConnection",
  'sql' : "SQLConnection",
  'document' : "DocumentConnection",
}
for handler_id, module_id in six.iteritems(handler_module_dict):
  # Ignore non-functionnal plugins.
  # This is done to avoid adding strict dependencies.
  # Code relying on the presence of a plugin will fail upon
  # WebServiceTool.connect .
  try:
    module = __import__(
      'erp5.component.module.%s' % (module_id, ),
      globals(), {}, [module_id])
  except ImportError:
    LOG('WebServiceTool', WARNING,
        'Unable to import module %r. %r transport will not be available.' % \
        (module_id, handler_id),
        error=True)
  else:
    registerConnectionPlugin(handler_id, getattr(module, module_id))

class WebServiceTool(BaseTool):
  """
  This tool can do all kinds of web services in all kinds of protocols.
  """

  id = 'portal_web_services'
  title = 'Web Services'
  meta_type = 'ERP5 Web Service Tool'
  portal_type = 'Web Service Tool'
  allowed_content_types = ()

  security = ClassSecurityInfo()

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getConnectionPluginList')
  def getConnectionPluginList(self):
    """
    Return list of available connection plugins
    """
    return sorted(connection_plugin_registry.keys())

  security.declareProtected(Permissions.ManagePortal, 'connect')
  def connect(self, url, user_name=None, password=None, transport=None, transport_kw=None):
    """
    Connect to remote instances
    of any kind of web service (not only ERP5) with many
    different kinds of transport like 'xml-rpc' or 'soap'
    """
    if transport_kw is None:
      transport_kw = {}
    connection_handler_klass = connection_plugin_registry[transport]
    connection_handler = connection_handler_klass(url, user_name, password,
                                                  **transport_kw)
    return connection_handler.connect()

InitializeClass(WebServiceTool)