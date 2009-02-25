##############################################################################
#
# Copyright (c) 2006 Nexedi SARL and Contributors. All Rights Reserved.
#                    Ivan Tyagov <ivan@nexedi.com>
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

from AccessControl import ClassSecurityInfo
from Globals import InitializeClass, DTMLFile
from Products.ERP5Type.Tool.BaseTool import BaseTool
from Products.ERP5Type import Permissions
from Products.ERP5 import _dtmldir
from Products.ERP5Type.ConnectionPlugin.XMLRPCConnection import XMLRPCConnection
from Products.ERP5Type.ConnectionPlugin.SOAPConnection import SOAPConnection


class WebServiceTool(BaseTool):
  """
  This tool can do all kinds of web services in all kinds of protocols.
  """

  id = 'portal_web_services'
  title = 'Web Service Tool'
  meta_type = 'ERP5 Web Service Tool'
  portal_type = 'Web Service Tool'
  allowed_content_types = ()

  security = ClassSecurityInfo()

  security.declareProtected(Permissions.ManagePortal, 'manage_overview')
  manage_overview = DTMLFile('explainWebServiceTool', _dtmldir )

  def connect(self, url, user_name=None, password=None, transport=None):
    """
    Connect to remote instances
    of any kind of web service (not only ERP5) with many
    different kinds of transport like 'xml-rpc' or 'soap'
    """
    # XXX: implement connection caching per zope thread
    if transport == 'xml-rpc':
      connection_handler = XMLRPCConnection(url, user_name, password)
    elif transport == 'soap':
      connection_handler = SOAPConnection(url, user_name, password)
    else:
      raise # XXX Which exception 
    connection_handler = connection_handler.connect()
    return connection_handler

InitializeClass(WebServiceTool)
