# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2002-2010 Nexedi SA and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
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
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

from AccessControl import ClassSecurityInfo
from Products.ERP5Type.Globals import InitializeClass
from Products.ERP5Type import Permissions
from Products.ERP5Type.Utils import normaliseUrl

no_crawl_protocol_list = ['mailto', 'javascript', ]
no_host_protocol_list = ['mailto', 'news', 'javascript',]
default_protocol_dict = { 'Email' : 'mailto',
                        }
class UrlMixin:

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  security.declareProtected(Permissions.AccessContentsInformation,
                            'asURL')
  def asURL(self):
    """
    Returns a text representation of the Url if defined
    or None else.
    """
    url_string = self.getUrlString()
    if not url_string:
      return None
    protocol = self.getUrlProtocol()
    if not protocol:
      # A quick fix for all objects which did not
      # define protocol such as email addresses
      ptype = self.getPortalType()
      if ptype in default_protocol_dict:
        protocol = default_protocol_dict[ptype]
      else:
        protocol = 'http'

    if protocol in no_host_protocol_list or url_string.startswith('//'):
      return '%s:%s' % (protocol, url_string)

    if url_string.startswith(protocol):
      return url_string

    return '%s://%s' % (protocol, url_string)

  security.declareProtected(Permissions.ModifyPortalContent, 'fromURL')
  def fromURL(self, url):
    """
    Analyses a URL and splits it into two parts. URLs
    normally follow RFC 1738. However, we accept URLs
    without the protocol a.k.a. scheme part (http, mailto, etc.). In this
    case only the url_string a.k.a. scheme-specific-part is taken
    into account. asURL will then generate the full URL.
    """
    if ':' in url:
      # This is the normal case (protocol specified in the URL)
      protocol, url_string = url.split(':', 1)
      if url_string.startswith('//'): url_string = url_string[2:]
      self._setUrlProtocol(protocol)
    else:
      url_string = url
    self.setUrlString(url_string)

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getURLServer')
  def getURLServer(self):
    """
    Returns the server part of a URL

    XXX - we must add here more consistency checking
    based on the protocol of the URL

    XXX - regular expressions would be better
    """
    url_string = self.getUrlString()
    return url_string.split('/')[0].split(':')[0]

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getURLPort')
  def getURLPort(self):
    """
    Returns the port part of a URL

    XXX - we must add here more consistency checking
    based on the protocol of the URL

    XXX - regular expressions would be better
    """
    url_string = self.getUrlString()
    server_part_list = url_string.split('/')[0].split(':')
    if len(server_part_list) > 1:
      return server_part_list[1]
    return None

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getURLPath')
  def getURLPath(self):
    """
    Returns the path part of a URL

    XXX - we must add here more consistency checking
    based on the protocol of the URL

    XXX - regular expressions would be better
    """
    url_string = self.getUrlString()
    return '/'.join(url_string.split('/')[1:])

  security.declareProtected(Permissions.AccessContentsInformation,
                            'asNormalisedURL')
  def asNormalisedURL(self, base_url=None):
    """
    call normaliseUrl with raw url
    """
    if self.hasUrlString():
      return normaliseUrl(self.asURL(), base_url=base_url)

InitializeClass(UrlMixin)
