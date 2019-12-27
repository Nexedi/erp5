
# -*- coding: utf-8 -*-
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
from Products.ERP5Type import Permissions, PropertySheet
from Products.ERP5Type.Utils import deprecated
from erp5.component.document.Coordinate import Coordinate
from Products.ERP5.mixin.url import UrlMixin

from zLOG import LOG

_marker = object()

class Url(Coordinate, UrlMixin):
  """
  A Url is allows to represent in a standard way coordinates
  such as web sites, emails, ftp sites, etc.
  """

  meta_type = 'ERP5 Url'
  portal_type = 'Url'
  add_permission = Permissions.AddPortalContent

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Default Properties
  property_sheets = (   PropertySheet.Url
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
    if self.isDetailed():
      return self.getUrlString('')
    return self.getCoordinateText('')

  security.declareProtected(Permissions.ModifyPortalContent, 'fromText')
  @deprecated
  def fromText(self, text):
    """
    Sets url_string a.k.a. scheme-specific-part of a URL
    """
    self._setCoordinateText(text)
    self.setUrlString(text)

  security.declareProtected(Permissions.AccessContentsInformation,
                            'standardTextFormat')
  def standardTextFormat(self):
    """
    Returns the standard text formats for urls. The purpose
    of this method is unknown.
    """
    return ("http://www.erp5.org", "mailto:info@erp5.org")


  security.declareProtected(Permissions.AccessContentsInformation,
                            'getUrlString')
  def getUrlString(self, default=_marker):
    """Fallback on coordinate_text
    """
    if not self.hasUrlString():
      if default is _marker:
        return self.getCoordinateText()
      else:
        return self.getCoordinateText(default)
    else:
      if default is _marker:
        return self._baseGetUrlString()
      else:
        return self._baseGetUrlString(default)

  security.declareProtected(Permissions.AccessContentsInformation, 'isDetailed')
  def isDetailed(self):
    """
    """
    return self.hasUrlString()

  security.declareProtected(Permissions.UseMailhostServices, 'send')
  @deprecated
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
