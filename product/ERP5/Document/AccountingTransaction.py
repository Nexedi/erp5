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

from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions, PropertySheet, Constraint, interfaces
from Products.CMFCore.utils import getToolByName

from Products.ERP5.Document.Delivery import Delivery
from Acquisition import aq_base

class AccountingTransaction(Delivery):
    """
      A Transaction object allows to add
      elementary accounting transactions in the general ledger
    """

    # CMF Type Definition
    meta_type = 'ERP5 Accounting Transaction'
    portal_type = 'Accounting Transaction'
    add_permission = Permissions.AddPortalContent
    isPortalContent = 1
    isRADContent = 1
    isDelivery = 1

    # Declarative security
    security = ClassSecurityInfo()
    security.declareObjectProtected(Permissions.AccessContentsInformation)

    # Default Properties
    property_sheets = ( PropertySheet.Base
                      , PropertySheet.XMLObject
                      , PropertySheet.CategoryCore
                      , PropertySheet.DublinCore
                      , PropertySheet.Task
                      , PropertySheet.Arrow
                      , PropertySheet.Movement
                      , PropertySheet.Delivery
                      , PropertySheet.Order
                      , PropertySheet.Reference
                      , PropertySheet.Comment
                      , PropertySheet.PaymentCondition
                      )
    
    security.declareProtected(Permissions.AccessContentsInformation,
                              'hasSourceSectionAccounting')
    def hasSourceSectionAccounting(self):
      """Return true if we should take into account accounting for source
      section.
      """
      section = self.getSourceSectionValue()
      if section is not None:
        preference_tool = getToolByName(self, 'portal_preferences')
        preferred_section_category = preference_tool.\
                getPreferredAccountingTransactionSectionCategory()
        if preferred_section_category:
          if section.getPortalType() == 'Person':
            return 0
          return section.isMemberOf(preferred_section_category)
      return 0

    security.declareProtected(Permissions.AccessContentsInformation,
                              'hasDestinationSectionAccounting')
    def hasDestinationSectionAccounting(self):
      """Return true if we should take into account accounting for destination
      section.
      """
      section = self.getDestinationSectionValue()
      if section is not None:
        preference_tool = getToolByName(self, 'portal_preferences')
        preferred_section_category = preference_tool.\
                getPreferredAccountingTransactionSectionCategory()
        if preferred_section_category:
          if section.getPortalType() == 'Person':
            return 0
          return section.isMemberOf(preferred_section_category)
      return 0
    
    security.declareProtected(Permissions.AccessContentsInformation,
                              'SearchableText')
    def SearchableText(self):
      """Text for full text search"""
      text_list = []
      for prop in ( self.getTitle(),
                    self.getDescription(),
                    self.getComment(),
                    self.getReference(),
                    self.getSourceReference(),
                    self.getDestinationReference(),
                    self.getSourceSectionTitle(),
                    self.getDestinationSectionTitle(),
                    self.getStartDate(),
                    self.getStopDate(), ):
        if prop:
          text_list.append(str(prop))
      return ' '.join(text_list)

# Compatibility
# It may be necessary to create an alias after removing the Transaction class
# Products.ERP5Type.Document.Transaction = AccountingTransaction
