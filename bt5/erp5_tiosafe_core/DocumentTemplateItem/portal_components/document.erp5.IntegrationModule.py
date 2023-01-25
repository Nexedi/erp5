##############################################################################
#
# Copyright (c) 2002-2010 Nexedi SA and Contributors. All Rights Reserved.
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
##############################################################################

from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions, PropertySheet
from Products.ERP5Type.XMLObject import XMLObject

class IntegrationModule(XMLObject):
  # CMF Type Definition
  meta_type = 'TioSafe Integration Module'
  portal_type = 'Integration Module'

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Default Properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.XMLObject
                    , PropertySheet.CategoryCore
                    , PropertySheet.DublinCore
                    , PropertySheet.SortIndex
                    , PropertySheet.IntegrationModule
                    , PropertySheet.Arrow
                      )

  def checkConsistency(self, fixit=False, filter=None, **kw): # pylint: disable=redefined-builtin
    """
    consistency is checked through a web service request
    """
    # XXX-Aurel : result must be formatted here
    try:
      return self['checkDataConsistency']()
    except KeyError:
      # WSR not present
      return []

  def __call__(self, REQUEST=None, **kw):
    """
    calling this object will call :
    - retrieveObject if exists and parameters are pass
    - getObjectList in other cases
    as method to retrieve list of object can not always be used
    to retrieve just one object
    """
    if REQUEST is not None:
      return self.view()
    if len(kw) and getattr(self, "retrieveObject", None) is not None:
      return self.retrieveObject(**kw)
    else:
      return self.getObjectList(**kw)

  def __getitem__(self, item):
    """
    Simulate the traversable behaviour by retrieving the item through
    the web service
    """
    try:
      if getattr(self, "retrieveObject", None) is not None:
        return self.retrieveObject[item]
      else:
        if self.getObjectList.getPortalType() == 'Python Script':
          return self.getObjectList(id=item)
        else:
          return self.getObjectList[item]
    except ValueError as msg:
      raise KeyError(msg)

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getGIDFor')
  def getGIDFor(self, item):
    """
    Return the gid for a given local id
    """
    raise NotImplementedError

