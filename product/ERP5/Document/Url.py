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
from Products.ERP5Type import Permissions, PropertySheet, Constraint, Interface
from Products.ERP5Type.Base import Base
from Products.ERP5.Document.Coordinate import Coordinate
from cStringIO import StringIO
from mimetypes import guess_type

from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEBase import MIMEBase
from email.Header import make_header
from email import Encoders

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
    protocol = self.getUrlProtocol()
    if not protocol:
      # A quick fix for all objects which did not
      # define protocol such as email addresses
      ptype = self.getPortalType()
      if default_protocol_dict.has_key(ptype):
        protocol = default_protocol_dict[ptype]
      else:
        protocol = 'http'
    url_string = self.getUrlString()
    if not url_string: return None
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
      protocol, url_string = url.split(':')
      if url_string.startswith('//'): url_string = url_string[2:]
      self._setUrlProtocol(protocol)
    else:
      url_string = url
    self.setUrlString(url_string)

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
    # get the mailhost object
    mailhost = getattr(self.getPortalObject(), 'MailHost', None)
    if mailhost is None:
      raise AttributeError, "Cannot find a MailHost object"
    else:
      if from_url is None:
        from_url = self.getUrlString(None)
      if to_url is None:
        to_url = self.getUrlString(None)
      if from_url is None or to_url is None:
        raise AttributeError, "No mail defined"

      if attachment_list == None:
        # Create non multi-part MIME message.
        message = MIMEText(msg, _charset='utf-8')
        attachment_list = []
      else:
        # Create multi-part MIME message.
        message = MIMEMultipart()
        message.preamble = "If you can read this, your mailreader\n" \
                           "can not handle multi-part messages!\n"
        message.attach(MIMEText(msg, _charset='utf-8'))
      
      if extra_headers:
        for k, v in extra_headers.items():
          message.add_header('X-%s' % k, v)

      message.add_header('Subject',
                         make_header([(subject, 'utf-8')]).encode())
      message.add_header('From', from_url)
      message.add_header('To', to_url)
      
      for attachment in attachment_list:
        if attachment.has_key('name'):
          attachment_name = attachment['name']
        else:
          attachment_name = ''
        # try to guess the mime type
        if not attachment.has_key('mime_type'):
          type, encoding = guess_type( attachment_name )
          if type != None:
            attachment['mime_type'] = type
          else:
            attachment['mime_type'] = 'application/octet-stream'

        # attach it
        if attachment['mime_type'] == 'text/plain':
          part = MIMEText(attachment['content'], _charset='utf-8')
        else:
          #  encode non-plaintext attachment in base64
          part = MIMEBase(*attachment['mime_type'].split('/', 1))
          part.set_payload(attachment['content'])
          Encoders.encode_base64(part)

        part.add_header('Content-Disposition',
                        'attachment; filename=%s' % attachment_name)
        message.attach(part)

      # send mail to user
      mailhost.send(message.as_string(), to_url, from_url)
