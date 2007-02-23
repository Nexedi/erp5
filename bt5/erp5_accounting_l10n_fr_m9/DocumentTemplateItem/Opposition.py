##############################################################################
#
# Copyright (c) 2006 Nexedi SA and Contributors. All Rights Reserved.
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
from Products.ERP5.Document.Path import Path
from Products.ERP5.Document.Predicate import Predicate

class Opposition(Path):
  """Opposition Document."""
  meta_type = 'ERP5 Opposition'
  portal_type = 'Opposition'
  isPortalContent = 1
  isRADContent = 1
  # XXX even if an Opposition is not conceptually a Movement, we want it
  # cataloged in the movement table, for access to quantity.
  isMovement = 1

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Default Properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.XMLObject
                    , PropertySheet.CategoryCore
                    , PropertySheet.DublinCore
                    , PropertySheet.Opposition
                    )

  def _edit(self, **kwd):
    """ Override to reset _identity_criterion & _range_criterion.
    This is maybe a Predicate bug XXX """
    self._identity_criterion = {}
    self._range_criterion = {}
    return Path._edit(self, **kwd)
  
  def validate(self):
    """ Override to reset _identity_criterion & _range_criterion.
    This is maybe a Predicate bug XXX """
    self._identity_criterion = {}
    self._range_criterion = {}

