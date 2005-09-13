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

class Url(Coordinate, Base):
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
    security.declareObjectProtected(Permissions.View)

    # Default Properties
    property_sheets = ( PropertySheet.Base
                      , PropertySheet.SimpleItem
                      , PropertySheet.Url
                      )

    # Factory Type Information
    factory_type_information = \
      {    'id'             : portal_type
         , 'meta_type'      : meta_type
         , 'description'    : """\
A Url is allows to represent in a standard way coordinates
such as web sites, emails, ftp sites, etc."""
         , 'icon'           : 'url_icon.gif'
         , 'product'        : 'ERP5'
         , 'factory'        : 'addUrl'
         , 'immediate_view' : 'url_edit'
         , 'actions'        :
        ( { 'id'            : 'view'
          , 'name'          : 'View'
          , 'category'      : 'object_view'
          , 'action'        : 'url_edit'
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'print'
          , 'name'          : 'Print'
          , 'category'      : 'object_print'
          , 'action'        : 'url_print'
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'metadata'
          , 'name'          : 'Metadata'
          , 'category'      : 'object_view'
          , 'action'        : 'metadata_edit'
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'translate'
          , 'name'          : 'Translate'
          , 'category'      : 'object_action'
          , 'action'        : 'translation_template_view'
          , 'permissions'   : (
              Permissions.TranslateContent, )
          }
        )
      }

    security.declareProtected(Permissions.View, 'asText')
    def asText(self):
      return self.url_string

    security.declareProtected(Permissions.ModifyPortalContent, 'fromText')
    def fromText(self, text):
      self.url_string = text

    security.declareProtected(Permissions.View, 'standardTextFormat')
    def standardTextFormat(self):
      """
        Returns the standard text formats for urls
      """
      return ("http://www.erp5.org","mailto:info@erp5.org")

    def send(self, from_url=None, to_url=None, msg=None, subject=None):
        """
        This method was previously named 'SendMail'


        Send An Email
        """
        # We assume by default that we are replying to the sender
        if from_url == None:
          from_url = self.getUrlString()
        if to_url.find('@')>=0: # We will send an email
          if msg is not None and subject is not None:
            header = "From: %s\n" % from_url
            header += "To: %s\n" % to_url
            header += "Subject: %s\n" % subject
            header += "\n"
            msg = header + msg
            self.getPortalObject().MailHost.send( msg )

