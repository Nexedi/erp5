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

import zope.interface
from AccessControl import ClassSecurityInfo
from zExceptions import Forbidden

from Products.ERP5Type import Permissions, PropertySheet, interfaces
from Products.ERP5Type.Base import Base
from Products.ERP5Type.Utils import deprecated, formatRFC822Headers
import re

_marker = object()

class Coordinate(Base):
  """
        Coordinates is a mix-in class which is used to store elementary
        coordinates of an Entity (ex. Person, Organisation)

        UNKNOWN Coordinates are treated as a document
        with a subject (to find a given type of coordinate).

        Coordinates use a URL approach. Any coordinate can
        be rendered in a URL style. For example::

            - tel:+33(0)662057614

            - fax:+33(0)153010929

            - mailto:jp@nexedi.com

            - naf:722Z

            - smail://Nexedi/Jean-Paul Smets/943, av de la Republique/59700
                        Marcq-en-Baroeul/France

        Coordinates are stored as content within an Entity. Coordinate ids
        are generated as a combination of a so-called role (ex. shipping,
        billing, etc.) and a class string. This way, coordinates can
        be accessed as attributes of the containing Entity::

            - default_phone

            - default_fax

            - billing_address

            - shipping_address

        In order to be able to list all coordinates of an Entity,
        a list of Coordinate metatypes has to be defined and
        stored somewhere. (TODO)
  """

  meta_type = 'ERP5 Coordinate'
  portal_type = 'Coordinate'
  add_permission = Permissions.AddPortalContent

  # Declarative interface
  zope.interface.implements(interfaces.ICoordinate, )

  # Declarative security (replaces __ac_permissions__)
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Declarative properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.SimpleItem
                    , PropertySheet.Coordinate
                    )

  ### helper methods
  security.declareProtected( Permissions.AccessContentsInformation,
                             'getRegularExpressionFindAll')
  def getRegularExpressionFindAll(self, regular_expression, string):
    """
    allows call of re.findall in a python script used for Coordinate
    """
    return re.findall(regular_expression, string)

  security.declareProtected( Permissions.AccessContentsInformation,
                             'getRegularExpressionGroups')
  def getRegularExpressionGroups(self, regular_expression, string):
    """
    allows call of re.search.groups in a python script used for Coordinate
    """
    match = re.search(regular_expression, string)
    if match is None:
      return ()
    return re.search(regular_expression, string).groups()

  ### Mix-in methods
  security.declareProtected( Permissions.AccessContentsInformation,
                             'asText' )
  def asText(self):
    """
    returns the coordinate as a text string
    """
    script = self._getTypeBasedMethod('asText')
    if script is not None:
      return script()

  security.declareProtected( Permissions.AccessContentsInformation,
                             'getText')
  def getText(self):
    """
    calls asText
    """
    return self.asText()

  security.declareProtected( Permissions.AccessContentsInformation,
                             'hasText')
  def hasText(self):
    """
    calls asText
    """
    return bool(self.asText())

  security.declareProtected(Permissions.AccessContentsInformation, 'getCoordinateText')
  def getCoordinateText(self, default=_marker):
    """Fallback on splitted values (old API)
    """
    if not self.hasCoordinateText() and self.isDetailed():
      # Display old values (parsed ones)
      # empty value is None, not ''
      value = self.asText()
      if value:
        return value
      if default is _marker:
        return None
      else:
        return default
    if default is _marker:
      return self._baseGetCoordinateText()
    return self._baseGetCoordinateText(default)

  security.declareProtected( Permissions.ModifyPortalContent, 'fromText' )
  @deprecated
  def fromText(self, coordinate_text):
    """
    modifies the coordinate according to the input text
    must be implemented by subclasses
    """
    script = self._getTypeBasedMethod('fromText')
    if script is not None:
      return script(text=coordinate_text)

  security.declareProtected(Permissions.ModifyPortalContent, '_setText')
  def _setText(self, value):
    """
    calls fromText
    """
    return self.fromText(value)

  security.declareProtected( Permissions.AccessContentsInformation,
                             'standardTextFormat')
  def standardTextFormat(self):
    """
    Returns the standard text formats for telephone numbers
    """
    pass

  security.declareProtected(Permissions.AccessContentsInformation, 'isDetailed')
  def isDetailed(self):
    return False

  security.declarePrivate( '_writeFromPUT' )
  def _writeFromPUT( self, body ):
    headers = {}
    headers, body = parseHeadersBody(body, headers)
    lines = body.split( '\n' )
    self.edit( lines[0] )
    headers['Format'] = self.COORDINATE_FORMAT
    new_subject = keywordsplitter(headers)
    headers['Subject'] = new_subject or self.Subject()
    haveheader = headers.has_key
    for key, value in self.getMetadataHeaders():
      if key != 'Format' and not haveheader(key):
        headers[key] = value
    self._editMetadata(title=headers['Title'],
                       subject=headers['Subject'],
                       description=headers['Description'],
                       contributors=headers['Contributors'],
                       effective_date=headers['Effective_date'],
                       expiration_date=headers['Expiration_date'],
                       format=headers['Format'],
                       language=headers['Language'],
                       rights=headers['Rights'],
                       )

  ## FTP handlers
  security.declareProtected( Permissions.ModifyPortalContent, 'PUT')
  def PUT(self, REQUEST, RESPONSE):
    """
    Handle HTTP / WebDAV / FTP PUT requests.
    """
    self.dav__init(REQUEST, RESPONSE)
    self.dav__simpleifhandler(REQUEST, RESPONSE, refresh=1)
    if REQUEST.environ['REQUEST_METHOD'] != 'PUT':
      raise Forbidden, 'REQUEST_METHOD should be PUT.'
    body = REQUEST.get('BODY', '')
    try:
      self._writeFromPUT( body )
      RESPONSE.setStatus(204)
      return RESPONSE
    except ResourceLockedError:
      get_transaction().abort()
      RESPONSE.setStatus(423)
      return RESPONSE

  security.declareProtected( Permissions.View, 'manage_FTPget' )
  def manage_FTPget(self):
    """
    Get the coordinate as text for WebDAV src / FTP download.
    """
    hdrlist = self.getMetadataHeaders()
    hdrtext = formatRFC822Headers( hdrlist )
    bodytext = '%s\n\n%s' % ( hdrtext, self.asText() )

    return bodytext

  security.declareProtected( Permissions.View, 'get_size' )
  def get_size( self ):
    """
    Used for FTP and apparently the ZMI now too
    """
    return len(self.manage_FTPget())
