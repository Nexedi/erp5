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

from AccessControl.SecurityManagement import setSecurityManager
from Products.CMFCore.utils import _checkConditionalGET, _setCacheHeaders, _ViewEmulator
from OFS.Image import File as OFSFile
from Products.ERP5.Document.Document import ConversionError, NotConvertedError
from Products.ERP5.mixin.base_extensible_traversable import BaseExtensibleTraversableMixin
from Products.ERP5.mixin.document_extensible_traversable import DocumentExtensibleTraversableMixin

# XXX: these duplicate ones in ERP5.Document
EMBEDDED_FORMAT = '_embedded'

class OOoDocumentExtensibleTraversableMixin(BaseExtensibleTraversableMixin):
  """
  This class provides a implementation of IExtensibleTraversable for OOoDocument classed based documents.
  """

  def getExtensibleContent(self, request, name):
    # Be sure that html conversion is done,
    # as it is required to extract extensible content
    old_manager, user = self._forceIdentification(request)
    web_cache_kw = {'name': name,
                    'format': EMBEDDED_FORMAT}
    try:
      self._convert(format='html')
      view = _ViewEmulator().__of__(self)
      # If we have a conditional get, set status 304 and return
      # no content
      if _checkConditionalGET(view, web_cache_kw):
        return ''
      # call caching policy manager.
      _setCacheHeaders(view, web_cache_kw)
      mime, data = self.getConversion(format=EMBEDDED_FORMAT, filename=name)
      document = OFSFile(name, name, data, content_type=mime).__of__(self.aq_parent)
    except (NotConvertedError, ConversionError, KeyError):
      document = DocumentExtensibleTraversableMixin.getExtensibleContent(self, request, name)
    # restore original security context if there's a logged in user
    if user is not None:
      setSecurityManager(old_manager)
    return document
