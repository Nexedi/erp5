##############################################################################
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
#                    Guillaume Michon        <guillaume.michon@e-asc.com>
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

from Products.ERP5Type import Permissions, PropertySheet
from Products.ERP5Type.XMLObject import XMLObject

class ImmobilisationDelivery(XMLObject):
    """
      An Immobilisation Delivery is an object whose role is to
      contain delivery movements which can immobilise items.
    """

    meta_type = 'ERP5 Immobilisation Delivery'
    portal_type = 'Immobilisation Delivery'
    add_permission = Permissions.AddPortalContent

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
                      )

    security.declareProtected(Permissions.AccessContentsInformation, 'updateImmobilisationState')
    def updateImmobilisationState(self, **kw):
      """
      This is often called as an activity, it will check if the
      delivery is valid as an immobilisation movement, and if so
      it will put the delivery in a valid state, if not valid in
      an invalid state
      """
      if self.getImmobilisationState() == 'calculating':
        from erp5.component.document.ImmobilisableItem import ImmobilisationValidityError
        try:
          if self.isValidImmobilisationMovement(**kw):
            self.validateImmobilisation()
          else:
            self.invalidateImmobilisation()
        except ImmobilisationValidityError:
          self.calculateImmobilisationValidity()

    security.declareProtected(Permissions.AccessContentsInformation, 'getImmobilisationMovementList')
    def getImmobilisationMovementList(self, **kw):
      """
      Return regular movements + immobilisation movements like
      Immobilisation Line and Immobilisation Cell
      """
      return self.getMovementList(self.getPortalMovementTypeList() +
                 ('Immobilisation Line', 'Immobilisation Cell'), **kw)

    security.declareProtected(Permissions.AccessContentsInformation, 'checkImmobilisationConsistency')
    def checkImmobilisationConsistency(self, *args, **kw):
      """
      Check the consistency about immobilisation values
      """
      return_list = []
      for movement in self.getImmobilisationMovementList():
        return_list.extend(movement.checkImmobilisationConsistency())
      return return_list

    security.declareProtected(Permissions.AccessContentsInformation, 'isValidImmobilisationMovement')
    def isValidImmobilisationMovement(self, *args, **kw):
      """
      Return true if all submovements are valid in terms of immobilisation
      """
      error_list = self.checkImmobilisationConsistency(*args, **kw)
      return len(error_list) == 0

    security.declareProtected(Permissions.AccessContentsInformation, 'isInvalidImmobilisationMovement')
    def isInvalidImmobilisationMovement(self, *args, **kw):
      """
      Return false if all submovements are valid in terms of immobilisation
      """
      return not self.isValidImmobilisationMovement(*args, **kw)

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getAggregatedItemsNextImmobilisationMovementValueList')
    def getAggregatedItemsNextImmobilisationMovementValueList(self, **kw):
      """
      Return the list of each next immobilisation movement for each aggregated item
      """
      from erp5.component.interface.IImmobilisationItem import IImmobilisationItem
      returned_list = []
      sub_movement_list = self.contentValues()
      for movement in self.getImmobilisationMovementList(**kw):
        for item in movement.getAggregateValueList():
          if IImmobilisationItem.providedBy(item):
            future_movement_list = item.getFutureImmobilisationMovementValueList(
                                       at_date = self.getStopDate(),
                                       from_movement = self,
                                       filter_valid = 0)
            if future_movement_list is not None:
              for next_movement in future_movement_list:
                if next_movement is not None and \
                   next_movement not in sub_movement_list and \
                   next_movement not in returned_list and \
                   next_movement.getStopDate() != self.getStopDate():
                  returned_list.append(next_movement)
      return returned_list

