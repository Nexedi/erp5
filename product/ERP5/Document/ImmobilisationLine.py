##############################################################################
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
#                    Guillaume Michon <guillaume@nexedi.com>
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

from Products.ERP5Type.Globals import InitializeClass
from AccessControl import ClassSecurityInfo

from Products.ERP5Type import Base, Permissions, PropertySheet, Constraint, interfaces
#from Products.ERP5.Core import MetaNode, MetaResource

from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5.Document.Amount import Amount
from Products.ERP5.Document.Movement import Movement
from Products.ERP5.Document.ImmobilisationMovement import ImmobilisationMovement
from Products.ERP5.Document.DeliveryLine import DeliveryLine

from string import capitalize
from zLOG import LOG

class ImmobilisationLine(Movement, XMLObject, ImmobilisationMovement, DeliveryLine):
  """
  """
  meta_type = 'ERP5 Immobilisation Line'
  portal_type = 'Immobilisation Line'
  add_permission = Permissions.AddPortalContent
  isPortalContent = 1
  isRADContent = 1
  isMovement = 1
  isAccountable = 0 # It should not be indexed in stock table

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Declarative properties
  property_sheets = ( PropertySheet.Base
                      , PropertySheet.XMLObject
                      , PropertySheet.CategoryCore
                      , PropertySheet.DublinCore
                      , PropertySheet.Task
                      , PropertySheet.Arrow
                      , PropertySheet.Movement
                      , PropertySheet.Delivery
                      , PropertySheet.Reference
                      , PropertySheet.Amount
                      , PropertySheet.Price
                      , PropertySheet.Amortisation
                      )
