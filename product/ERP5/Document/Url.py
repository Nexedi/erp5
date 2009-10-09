##############################################################################
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
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
from Products.CMFCore.utils import getToolByName
from Products.ERP5Type import Permissions, PropertySheet, Constraint, interfaces
from Products.ERP5Type.Base import Base
from Products.ERP5.Document.Coordinate import Coordinate
from Products.ERP5.Tool.NotificationTool import buildEmailMessage
from zLOG import LOG
import urllib

no_crawl_protocol_list = ['mailto', 'javascript', ]
no_host_protocol_list = ['mailto', 'news', 'javascript',]
default_protocol_dict = { 'Email' : 'mailto',
                        }

class UrlMixIn:

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
    if urllib.splittype(url_string)[0]:
      return url_string
    protocol = self.getUrlProtocol()
    if not protocol:
      # A quick fix for all objects which did not
      # define protocol such as email addresses
      ptype = self.getPortalType()
      if default_protocol_dict.has_key(ptype):
        protocol = default_protocol_dict[ptype]
      else:
        protocol = 'http'
    if protocol in no_host_protocol_list or url_string.startswith('//'):
      return '%s:%s' % (protocol, url_string)
    return '%s://%s' % (protocol, url_string)

  security.declareProtected(Permissions.ModifyPortalContent, 'fromText')
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

class Url(Coordinate, Base, UrlMixIn):
  """
  A Url is allows to represent in a standard way coordinates
  such as web sites, emails, ftp sites, etc.
  """

  meta_type = 'ERP5 Url'
  portal_type = 'Url'
  add_permission = Permissions.AddPortalContent
  isPortalContent = 1
  isRADContent = 1

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Default Properties
  property_sheets = (   PropertySheet.Base
                      , PropertySheet.SimpleItem
                      , PropertySheet.Url
                      , PropertySheet.SortIndex
                      )

  security.declareProtected(Permissions.AccessContentsInformation,
                            'asText')
  def asText(self):
    """
    Returns a text representation of the url_string a.k.a. scheme-specific-part
    This method is useful to handled emails, web pages of companies, etc.
    in the same way as for other coordinates (ex. telephones). Most
    users just enter www.erp5.com or info@erp5.com rather than
    http://www.erp5.com or mailto:info@erp5.com
    """
    return self.getUrlString()

  security.declareProtected(Permissions.ModifyPortalContent, 'fromText')
  def fromText(self, text):
    """
    Sets url_string a.k.a. scheme-specific-part of a URL
    """
    self.setUrlString(text)

  security.declareProtected(Permissions.AccessContentsInformation,
                            'standardTextFormat')
  def standardTextFormat(self):
    """
    Returns the standard text formats for urls. The purpose
    of this method is unknown.
    """
    return ("http://www.erp5.org", "mailto:info@erp5.org")

  security.declareProtected(Permissions.UseMailhostServices, 'send')
  def send(self, from_url=None, to_url=None, msg=None,
           subject=None, attachment_list=None, extra_headers=None):
    """
    This method was previously named 'SendMail' and is used to send email

    * attachment_list is a list of dictionnaries with those keys:
     - name : name of the attachment,
     - content: data of the attachment
     - mime_type: mime-type corresponding to the attachment
    * extra_headers is a dictionnary of custom headers to add to the email.
      "X-" prefix is automatically added to those headers.
    """
    LOG('ERP5/Document/Url.send',0, 
     'DEPRECATED Url.send should not be used, use portal_notifications instead.')

    if from_url is None:
      from_url = self.getUrlString(None)
    if to_url is None:
      to_url = self.getUrlString(None)
    if from_url is None or to_url is None:
      raise AttributeError, "No mail defined"

    portal_notifications = getToolByName(self, 'portal_notifications')

    portal_notifications._sendEmailMessage(from_url=from_url, to_url=to_url,
                                           body=msg, subject=subject,
                                           attachment_list=attachment_list,
                                           extra_headers=extra_headers)
