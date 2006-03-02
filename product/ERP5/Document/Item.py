##############################################################################
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
#                    Guillaume Michon        <guillaume@nexedi.com>
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
from Products.CMFCore.WorkflowCore import WorkflowMethod
from Products.CMFCore.utils import getToolByName
from Products.ERP5.Document.ImmobilisableItem import ImmobilisableItem

from zLOG import LOG


NEGLIGEABLE_PRICE = 10e-8


class Item(XMLObject, Amount, ImmobilisableItem):
    """
      Items in ERP5 are intended to provide a way to track objects
    """

    meta_type = 'ERP5 Item'
    portal_type = 'Item'
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
                      , PropertySheet.Price
                      , PropertySheet.Resource
                      , PropertySheet.Item
                      , PropertySheet.Amount
                      , PropertySheet.Reference
                      )

    security.declareProtected(Permissions.ModifyPortalContent,'generateNewId')
    def generateNewId(self, id_group='item_id_group', default=None, method=None):
      """
      We want a different id for all Item
      """
      return XMLObject.generateNewId(self, id_group=id_group, default=default, method=method)

