##############################################################################
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
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
# This proopgram is distributed in the hope that it will be useful,
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
from Products.CMFCore.WorkflowCore import WorkflowMethod
from Products.ERP5Type import Permissions, PropertySheet, Constraint, Interface
from Products.ERP5.Document.Delivery import Delivery
from Products.ERP5Type.Document.DeliveryCell import DeliveryCell
from Products.ERP5.Document.Movement import Movement
from Products.ERP5.Document.AccountingTransaction import AccountingTransaction

class BankingOperation(Delivery,AccountingTransaction):

    # CMF Type Definition
    meta_type = 'BAOBAB Banking Operation'
    portal_type = 'Banking Operation'
    isPortalContent = 1
    isRADContent = 1

    # Declarative security
    security = ClassSecurityInfo()
    security.declareObjectProtected(Permissions.View)

    # Default Properties
    property_sheets = ( PropertySheet.Base
                      , PropertySheet.XMLObject
                      , PropertySheet.CategoryCore
                      , PropertySheet.DublinCore
                      , PropertySheet.Task
                      , PropertySheet.Arrow
                      , PropertySheet.BankingOperation
                      , PropertySheet.ItemAggregation
                      , PropertySheet.Amount
                      )


    # Special index methods
    security.declareProtected(Permissions.View, 'getBaobabSourceUid')
    def getBaobabSourceUid(self):
        """
            Returns a calculated source
        """
        LOG("KevClasses>> Banking operation >>> getBaobabSourceUid ",0,repr(self))
        return self.getSourceUid()

    security.declareProtected(Permissions.View, 'getBaobabDestinationUid')
    def getBaobabDestinationUid(self):
        """
            Returns a calculated destination
        """
        LOG("KevClasses>> Banking operation >>> getBaobabDestinationUid ",0,repr(self))
        return self.getDestinationUid()

    security.declareProtected(Permissions.View, 'getBaobabSourceSectionUid')
    def getBaobabSourceSectionUid(self):
        """
            Returns a calculated source section
        """
        LOG("KevClasses>> Banking operation >>> getBaobabSourceSectionUid ",0,repr(self))
        return self.getSourceSectionUid()

    security.declareProtected(Permissions.View, 'getBaobabDestinationSectionUid')
    def getBaobabDestinationSectionUid(self):
        """
            Returns a calculated destination section
        """
        LOG("KevClasses>> Banking operation >>> getBaobabDestinationSectionUid ",0,repr(self))
        return self.getDestinationSectionUid()

# Dynamic patch
Delivery.getBaobabSource = lambda x: x.getSource()
Delivery.security.declareProtected(Permissions.View, 'getBaobabSource')
Delivery.getBaobabSourceUid = lambda x: x.getSourceUid()
Delivery.security.declareProtected(Permissions.View, 'getBaobabSourceUid')
Delivery.getBaobabDestinationUid = lambda x: x.getDestinationUid()
Delivery.security.declareProtected(Permissions.View, 'getBaobabDestinationUid')
Delivery.getBaobabSourceSectionUid = lambda x: x.getSourceSectionUid()
Delivery.security.declareProtected(Permissions.View, 'getBaobabSourceSectionUid')
Delivery.getBaobabDestinationSectionUid = lambda x: x.getDestinationSectionUid()
Delivery.security.declareProtected(Permissions.View, 'getBaobabDestinationSectionUid')


# Overload Movement
Movement.getBaobabSource = lambda x: x.getSource()
Movement.security.declareProtected(Permissions.View, 'getBaobabSource')
Movement.getBaobabSourceUid = lambda x: x.getSourceUid()
Movement.security.declareProtected(Permissions.View, 'getBaobabSourceUid')
Movement.getBaobabDestinationUid = lambda x: x.getDestinationUid()
Movement.security.declareProtected(Permissions.View, 'getBaobabDestinationUid')
Movement.getBaobabSourceSectionUid = lambda x: x.getSourceSectionUid()
Movement.security.declareProtected(Permissions.View, 'getBaobabSourceSectionUid')
Movement.getBaobabDestinationSectionUid = lambda x: x.getDestinationSectionUid()
Movement.security.declareProtected(Permissions.View, 'getBaobabDestinationSectionUid')

# Acquire Baobab source / destination uids from parent line
DeliveryCell.getBaobabSource = lambda x: x.aq_parent.getBaobabSource()
DeliveryCell.security.declareProtected(Permissions.View, 'getBaobabSource')
DeliveryCell.getBaobabSourceUid = lambda x: x.aq_parent.getBaobabSourceUid()
DeliveryCell.security.declareProtected(Permissions.View, 'getBaobabSourceUid')
DeliveryCell.getBaobabDestinationUid = lambda x: x.aq_parent.getBaobabDestinationUid()
DeliveryCell.security.declareProtected(Permissions.View, 'getBaobabDestinationUid')
DeliveryCell.getBaobabSourceSectionUid = lambda x: x.aq_parent.getBaobabSourceSectionUid()
DeliveryCell.security.declareProtected(Permissions.View, 'getBaobabSourceSectionUid')
DeliveryCell.BaobabDestinationSectionUid = lambda x: x.aq_parent.getBaobabDestinationSectionUid()
DeliveryCell.security.declareProtected(Permissions.View, 'getBaobabDestinationSectionUid')




