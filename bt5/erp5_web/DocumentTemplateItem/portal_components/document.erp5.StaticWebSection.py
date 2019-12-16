# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2016 Nexedi SA and Contributors. All Rights Reserved.
#                    Cédric Le Ninivin <cedric.leninivin@nexedi.com>
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
from Acquisition import aq_base
from OFS.Traversable import NotFound

from Products.ERP5.mixin.document_extensible_traversable import DocumentExtensibleTraversableMixin
from Products.ERP5.Document.WebSection import WebSection
from Products.ERP5Type import Permissions

from webdav.NullResource import NullResource

import urllib

MARKER = []

class StaticWebSection(WebSection):
  """
  This Web Section only get resource from the DMS.
  The standard acquisition is disabled here.
  """

  portal_type = 'Static Web Section'
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  def getExtensibleContent(self, request, name):
    stack = request['TraversalRequestNameStack']

    if isinstance(name, list):
      name = name[0]
    if not name or name in ("/",):
      url_list = []
    else:
      url_list = [name]
    while len(stack):
      if stack[-1] not in ('/', ''):
        url_list.append(stack.pop())
      else:
        stack.pop()

    # Drop the automatically added VirtualHostMonster object ID
    virtual_url_part_tuple = request.get('VIRTUAL_URL_PARTS', None)
    if (virtual_url_part_tuple is not None) and \
       (not urllib.unquote(virtual_url_part_tuple[1]).endswith("/".join(url_list))):
      url_list.pop(0)

    if request.get('ACTUAL_URL', '').endswith("/"): # or len(url_list) == 0:
      url_list.append("index.html")

    return DocumentExtensibleTraversableMixin.getExtensibleContent(self, request, "/".join(url_list))

  def _getStaticDocument(self, request, name):
    try:
      return self[name]
    except KeyError:
      pass
    document = self.getExtensibleContent(request, name)
    if document is not None:
      return aq_base(document).__of__(self)

    try:
      return getattr(self, name)
    except AttributeError:
      pass

    # Not found section
    method = request.get('REQUEST_METHOD', 'GET')
    if not method in ('GET', 'POST'):
      return NullResource(self, name, request).__of__(self)
    # Waaa. unrestrictedTraverse calls us with a fake REQUEST.
    # There is proabably a better fix for this.
    try:
      request.RESPONSE.notFoundError("%s\n%s" % (name, method))
    except AttributeError:
      raise KeyError, name


  security.declareProtected(Permissions.View, '__bobo_traverse__')
  def __bobo_traverse__(self, request, name):
    """
      Taken from WebSection Bobo Traverse, the difference is that
      __bobo_traverse__ from DocumentExtensibleTraversableMixin is not called
    """
    # Register current web site physical path for later URL generation
    if request.get(self.web_section_key, MARKER) is MARKER:
      request[self.web_section_key] = self.getPhysicalPath()
      # Normalize web parameter in the request
      # Fix common user mistake and transform '1' string to boolean
      for web_param in ['ignore_layout', 'editable_mode']:
        if hasattr(request, web_param):
          param = getattr(request, web_param, None)
          if isinstance(param, (list, tuple)):
            param = param[0]
          if param in ('1', 1, True):
            request.set(web_param, True)
          else:
            request.set(web_param, False)

    document = None
    try:
      document = self._getStaticDocument(request, name)
    except NotFound:
      not_found_page_ref = self.getLayoutProperty('layout_not_found_page_reference')
      if not_found_page_ref:
        document = DocumentExtensibleTraversableMixin.getDocumentValue(self, name=not_found_page_ref)
      if document is None:
        # if no document found, fallback on default page template
        document = DocumentExtensibleTraversableMixin.__bobo_traverse__(self, request,
          '404.error.page')
    return document
