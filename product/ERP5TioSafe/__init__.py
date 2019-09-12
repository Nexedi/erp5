##############################################################################
#
# Copyright (c) 2002-2009 Nexedi SA and Contributors. All Rights Reserved.
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

# Update ERP5 Globals
from Products.ERP5Type.Utils import initializeProduct, updateGlobals
from Tool import IntegrationTool, OAuthTool
import sys, Permissions
this_module = sys.modules[ __name__ ]
document_classes = updateGlobals(this_module, globals(),
                                 permissions_module=Permissions)

# Finish installation
def initialize( context ):
  import Document
  initializeProduct(context, this_module, globals(),
                    document_module=Document,
                    document_classes=document_classes,
                    object_classes=(),
                    portal_tools=(IntegrationTool.IntegrationTool,
                                  OAuthTool.OAuthTool),
                    content_constructors=(),
                    content_classes=())

# Initialize Connection plugins
from Products.ERP5Type.Tool.WebServiceTool import registerConnectionPlugin
from zLOG import LOG, WARNING

handler_module_dict = {
  'http': 'HTTPConnection',
  'php_unit_test': 'PHPUnitTestConnection',
  'rest': 'RESTConnection',
  'oxatis': 'OxatisConnection',
  'oxatis_test': 'OxatisTestConnection',
  'ubercart_test': 'UbercartTestConnection',
  'virtuemart_test': 'VirtueMartTestConnection',
  'magento_xmlrpc': 'MagentoXMLRPCConnection',
  'document': 'DocumentConnection',
}

for handler_id, module_id in handler_module_dict.iteritems():
  # Ignore non-functionnal plugins.
  # This is done to avoid adding strict dependencies.
  # Code relying on the presence of a plugin will fail upon
  # WebServiceTool.connect .
  try:
    module = __import__(
      'Products.ERP5TioSafe.ConnectionPlugin.%s' % (module_id, ),
      globals(), {}, [module_id])
  except ImportError:
    LOG('ERP5TioSafe.__init__', WARNING,
        'Unable to import module %r. %r transport will not be available.' % \
        (module_id, handler_id),
        error=True)
  else:
    try:
      registerConnectionPlugin(handler_id, getattr(module, module_id))
    except ValueError, msg:
      LOG('ERP5TioSafe.ConnectionPlugin.__init__', WARNING,
          'Unable to register module %r. error is %r.' % \
          (module_id, msg),
          error=True)
