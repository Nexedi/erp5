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

from Globals import InitializeClass
from AccessControl import ClassSecurityInfo

from Products.ERP5Type import Base, Permissions, PropertySheet, Constraint, interfaces
#from Products.ERP5.Core import MetaNode, MetaResource

from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5.Document.Amount import Amount
from Products.ERP5.Document.Movement import Movement
from Products.ERP5.Document.Delivery import Delivery

from string import capitalize
from zLOG import LOG

class Immobilisation(XMLObject, Delivery):
  """
    An Immobilisation object holds the information about
    an accounting immobilisation (in order to amortise an object)

    It is an instant movement without source or destination, but which
    implies a state change and a source_decision and a destination_decision
    Do not index in stock table
  """
  meta_type = 'ERP5 Immobilisation'
  portal_type = 'Immobilisation'
  add_permission = Permissions.AddPortalContent
  isPortalContent = 1
  isRADContent = 1
  isDelivery = 1
  isMovement = 0

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Declarative interfaces
  __implements__ = ( interfaces.IVariated, )

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
                      , PropertySheet.Comment
                      , PropertySheet.Amount
                      , PropertySheet.Price
                      , PropertySheet.Amortisation
                      )

  security.declareProtected(Permissions.View, 'isMovement')
  def isMovement(self, **kw):
    """
    An Immobilisation must not be indexed in stock table, so it is not a Movement
    """
    return 0
    
