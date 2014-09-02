# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009 Nexedi KK, Nexedi SA and Contributors. All Rights Reserved.
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
from Products.ERP5.Document.Path import Path
from Products.ERP5.mixin.periodicity import PeriodicityMixin

class PeriodicityLineMixin(PeriodicityMixin):
  """
  A class extends PeriodicityMixin to add term.
  """

  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  property_sheets = ( PropertySheet.PeriodicityTerm,
                      PropertySheet.CategoryCore, )

  security.declareProtected(Permissions.AccessContentsInformation, 'getPeriodicityTermStopDate')
  def getPeriodicityTermStopDate(self, start_date, default=None):
    """Return periodicity term's stop_date by calculating periodicity term
    length with a start_date argument and other own properties.
    """
    length_number = self.getPeriodicityTermLengthNumber()
    time_scale = self.getPeriodicityTermTimeScale()
    scope_type = self.getPeriodicityTermScopeType()

    if scope_type:
      method = self._getTypeBasedMethod('calculateScopeTypeStopDate')
      if method is None:
        raise RuntimeError, 'Type based method calculateScopeTypeStopDate does not exist.'
      else:
        return method(scope_type, start_date)
    elif time_scale:
      if time_scale=='day':
        day = length_number
        return start_date+day
      else:
        raise RuntimeError, 'Unknown time scale: %s' % time_scale
    else:
      return None

class PeriodicityLine(Path, PeriodicityLineMixin):
  """
  A class defines how often an order is made.
  """

  meta_type = 'ERP5 Periodicity Line'
  portal_type = 'Periodicity Line'
  add_permission = Permissions.AddPortalContent

  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  property_sheets = Path.property_sheets+(PropertySheet.Periodicity,
                                          PropertySheet.PeriodicityTerm,
                                          )

  security.declareProtected(Permissions.AccessContentsInformation, 'getDatePeriodList')
  def getDatePeriodList(self, from_date, to_date):
    """
    Returns a list of a tuple of start_date and stop_date.
    """
    effective_date = self.getEffectiveDate()
    expiration_date = self.getExpirationDate()
    result = []

    if expiration_date is not None and to_date > expiration_date:
      to_date = expiration_date

    next_start_date = self.getNextPeriodicalDate(from_date)
    while next_start_date <= to_date:
      if next_start_date >= effective_date:
        result.append((next_start_date,
                       self.getPeriodicityTermStopDate(next_start_date)))

      new_next_start_date = self.getNextPeriodicalDate(next_start_date)
      if new_next_start_date==next_start_date:
        # prevent infinite loop.
        break
      else:
        next_start_date = new_next_start_date
    return result
