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

from Globals import InitializeClass, PersistentMapping
from AccessControl import ClassSecurityInfo

from DateTime import DateTime
from string import capitalize

from Products.ERP5Type import Permissions, PropertySheet, Constraint, Interface
from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5Type.DateUtils import addToDate, getClosestDate, getIntervalBetweenDates 
from Products.ERP5Type.DateUtils import getMonthAndDaysBetween, getRoundedMonthBetween
from Products.ERP5Type.DateUtils import getMonthFraction, getYearFraction, getBissextilCompliantYearFraction
from Products.ERP5Type.DateUtils import same_movement_interval, number_of_months_in_year, centis, millis
from Products.ERP5.Document.Amount import Amount
from Products.ERP5Type.Base import WorkflowMethod
from Products.CMFCore.utils import getToolByName
from Products.ERP5.Document.ImmobilisableItem import ImmobilisationValidityError


from zLOG import LOG


NEGLIGEABLE_PRICE = 10e-8

class ImmobilisationDelivery(XMLObject):
    """
      An Immobilisation Delivery is an object whose role is to
      contain delivery movements which can immobilise items.
    """

    meta_type = 'ERP5 Immobilisation Delivery'
    portal_type = 'Immobilisation Delivery'
    add_permission = Permissions.AddPortalContent
    isPortalContent = 1
    isRADContent = 1

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

    def validate_immobilisation(self, **kw):
      pass
    def invalidate_immobilisation(self, **kw):
      pass
    def calculate_immobilisation_validity(self, **kw):
      pass
    
    validate_immobilisation = WorkflowMethod(validate_immobilisation)
    invalidate_immobilisation = WorkflowMethod(invalidate_immobilisation)
    calculate_immobilisation_validity = WorkflowMethod(calculate_immobilisation_validity)
    
    security.declareProtected(Permissions.View, 'updateImmobilisationState')
    def updateImmobilisationState(self,**kw):
      """
      This is often called as an activity, it will check if the
      delivery is valid as an immobilisation movement, and if so
      it will put the delivery in a valid state, if not valid in
      an invalid state
      """
      if self.getImmobilisationState() == 'calculating':
        try:
          if self.isValidImmobilisationMovement(**kw):
            self.validate_immobilisation()
          else:
            self.invalidate_immobilisation()
        except ImmobilisationValidityError:
          self.calculate_immobilisation_validity()

    security.declareProtected(Permissions.View, 'getImmobilisationState')
    def getImmobilisationState(self, id_only=1):
      """
      Returns the current state in immobilisation validity
      """
      portal_workflow = getToolByName(self, 'portal_workflow')
      wf = portal_workflow.getWorkflowById('immobilisation_workflow')
      return wf._getWorkflowStateOf(self, id_only=id_only)

    security.declareProtected(Permissions.View, 'getImmobilisationMovementList')
    def getImmobilisationMovementList(self, **kw):
      """
      Return regular movements + immobilisation movements like
      Immobilisation Line and Immobilisation Cell
      """
      return self.getMovementList(self.getPortalMovementTypeList() +
                 ('Immobilisation Line', 'Immobilisation Cell'), **kw)
      
    security.declareProtected(Permissions.View, 'checkImmobilisationConsistency')
    def checkImmobilisationConsistency(self, *args, **kw):
      """
      Check the consistency about immobilisation values
      """
      return_list = []
      for movement in self.getImmobilisationMovementList():
        return_list.extend(movement.checkImmobilisationConsistency())
      return return_list

    security.declareProtected(Permissions.View, 'isValidImmobilisationMovement')
    def isValidImmobilisationMovement(self, *args, **kw):
      """
      Return true if all submovements are valid in terms of immobilisation
      """
      error_list = self.checkImmobilisationConsistency(*args, **kw)
      if len(error_list) == 0:
        return 1
      return 0

    security.declareProtected(Permissions.View, 'isInvalidImmobilisationMovement')
    def isInvalidImmobilisationMovement(self, *args, **kw):
      """
      Return false if all submovements are valid in terms of immobilisation
      """
      return not self.isValidImmobilisationMovement(*args, **kw)

    security.declareProtected(Permissions.View, 'getAggregatedItemsNextImmobilisationMovementValueList')
    def getAggregatedItemsNextImmobilisationMovementValueList(self, **kw):
      """
      Return the list of each next immobilisation movement for each aggregated item
      """
      returned_list = []
      sub_movement_list = self.contentValues()
      for movement in self.getImmobilisationMovementList(**kw):
        for item in movement.getAggregateValueList():
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
      
