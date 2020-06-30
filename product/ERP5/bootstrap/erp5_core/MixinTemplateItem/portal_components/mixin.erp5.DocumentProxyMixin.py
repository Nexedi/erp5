# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009 Nexedi SA and Contributors. All Rights Reserved.
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
from Products.ERP5Type.Globals import InitializeClass
from Products.ERP5Type import Permissions
from warnings import warn

class DocumentProxyError(Exception):pass

class DocumentProxyMixin:
  """
  This class provides a generic implementation of IDocumentProxy and IDownloadable.
  """

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  security.declareProtected(Permissions.AccessContentsInformation, 'index_html')
  def index_html(self, REQUEST, *args, **kw):
    """ Only a proxy method """
    return self.getProxiedDocument().index_html(REQUEST, *args, **kw)

  security.declareProtected(Permissions.AccessContentsInformation, \
                            'getProxiedDocument' )
  def getProxiedDocument(self):
    """
    Try to retrieve the original document
    """
    warn("getProxiedDocument() function is deprecated. Use getProxiedDocumentValue() instead.", \
          DeprecationWarning, stacklevel=2)
    return self.getProxiedDocumentValue()

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getProxiedDocumentValue')
  def getProxiedDocumentValue(self):
    """
    Try to retrieve the original document
    """
    proxied_document = self.getDocumentProxyValue()
    if proxied_document is None:
      raise DocumentProxyError("Unable to find a proxied document")
    return proxied_document

InitializeClass(DocumentProxyMixin)
