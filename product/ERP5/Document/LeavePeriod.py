##############################################################################
#
# Copyright (c) 2007 Nexedi SARL and Contributors. All Rights Reserved.
#                    Courteaud Romain <romain@nexedi.com>
#                    
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

from Products.ERP5Type import Permissions, PropertySheet, Constraint, Interface
from Products.ERP5.Document.CalendarPeriod import CalendarPeriod

class LeavePeriod(CalendarPeriod):
  """
  Leave Period is used to remove available time of the user in a 
  period of Time
  """

  meta_type = 'ERP5 Leave Period'
  portal_type = 'Leave Period'

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Declarative properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.XMLObject
                    , PropertySheet.CategoryCore
                    , PropertySheet.DublinCore
                    , PropertySheet.Amount
                    , PropertySheet.Task
                    , PropertySheet.Movement
                    , PropertySheet.Arrow
                    , PropertySheet.Periodicity
                    , PropertySheet.Path
                    , PropertySheet.SortIndex
                    )

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getInventoriatedQuantity')
  def getInventoriatedQuantity(self, default=None, *args, **kw):
    """
    Surcharged accessor to calculate the Quantity in second.
    """
    quantity = CalendarPeriod.getInventoriatedQuantity(
                                            self, default=default,
                                            *args, **kw)
    return -quantity
