##############################################################################
#
# Copyright (c) 2009 Nexedi SA and Contributors. All Rights Reserved.
#                    Fabien Morin <fabien@nexedi.com>
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

from Products.ERP5Type import Permissions, PropertySheet
from Products.ERP5.Document.SubscriptionItem import SubscriptionItem
from AccessControl import ClassSecurityInfo
from Products.ERP5Type.DateUtils import addToDate, atTheEndOfPeriod
from DateTime import DateTime

from zLOG import LOG

class EmploymentContract(SubscriptionItem):
  """
    Employment Contracts in ERP5 are intended to store work contract properties
  """

  meta_type = 'ERP5 Employment Contract'
  portal_type = 'Employement Contract'

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Declarative properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.XMLObject
                    , PropertySheet.CategoryCore
                    , PropertySheet.DublinCore
                    , PropertySheet.Price
                    , PropertySheet.Item
                    , PropertySheet.Amount
                    , PropertySheet.Reference
                    , PropertySheet.ItemAggregation
                    )

  def assertMovementExists(self, applied_rule, start_date):
    """
      a movment exist if there is already a movement with the same 
      start_date and stop_date
    """
    movement_id = 'movement_%s_%s' % (start_date.year(), start_date.month())
    return len(applied_rule.searchFolder(id=movement_id))

  def expandOpenOrderRule(self, applied_rule, force=0, **kw):
    """
      Expand tries to find all applicable supply path and all
      applicable transformations. 
    """
    number_of_months_in_year = 12

    # get career list that use this employment contract :
    career_list = self.getAggregateRelatedValueList()
    current_date = DateTime()
    for career in career_list:
      employee = career.getParentRelativeUrl()
      employer = career.getSubordinationValue() is not None and career.getSubordinationValue().getRelativeUrl() or None
      start_date = career.getStartDate()
      stop_date = career.getStopDate()
      for year_count in range(stop_date.year() - start_date.year() + 1):
        for month_count in range(stop_date.month() - start_date.month()+1):
          # for first movement, we use the start_date day
          movement_start_date = addToDate(start_date, year=year_count, month=month_count)
          if month_count != 0 or year_count != 0:
            # if there is more than one movement in the period, start date is the begining of the month
            movement_start_date = DateTime(movement_start_date.strftime('%Y/%m/01 00:00:00'))
          movement_stop_date = atTheEndOfPeriod(movement_start_date, 'month')-1
          # create only one year in the future
          if movement_start_date > addToDate(current_date, year=1):
            break
          # if the stop_date is in not at the end of the month, use it
          if stop_date < movement_stop_date:
            movement_stop_date = stop_date
          if not self.assertMovementExists(applied_rule, movement_start_date) and\
              movement_stop_date.month() <= number_of_months_in_year:
            property_dict = dict()

            simulation_movement = applied_rule.newContent(
                id = 'movement_%s_%s' % (movement_start_date.year(), movement_stop_date.month()),
                start_date = movement_start_date,
                stop_date = movement_stop_date,
                source = employee,
                destination = employer,
                source_section = employee,
                destination_section = employer,
                quantity = self.getQuantity(),
                quantity_unit = self.getQuantityUnit(),
                resource = self.getResourceRelativeUrl()
                )
