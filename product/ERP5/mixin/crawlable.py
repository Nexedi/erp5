# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009 Nexedi SA and Contributors. All Rights Reserved.
#                    Ivan Tyagov <ivan@nexedi.com>
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

from AccessControl import ClassSecurityInfo, getSecurityManager
from Products.ERP5Type import Permissions

class CrawlableMixin:
  """
  Generic implementation of ICrawlable interface
  """
  # Declarative security
  security = ClassSecurityInfo()

  security.declareProtected(Permissions.AccessContentsInformation, 'getFrequencyIndex')
  def getFrequencyIndex(self):
    """
      Returns the document update frequency as an integer
      which is used by alamrs to decide which documents
      must be updates at which time. The index represents
      a time slot (ex. all days in a month, all hours in a week).
    """
    try:
      return self.getUpdateFrequencyValue().getIntIndex()
    except AttributeError:
      # Catch Attribute error or Key error - XXX not beautiful
      return 0

  security.declareProtected(Permissions.AccessContentsInformation, 'getCreationDateIndex')
  def getCreationDateIndex(self, at_date = None):
    """
    Returns the document Creation Date Index which is the creation
    date converted into hours modulo the Frequency Index.
    """
    frequency_index = self.getFrequencyIndex()
    if not frequency_index: return -1 # If not update frequency is provided, make sure we never update
    hour = convertDateToHour(date=self.getCreationDate())
    creation_date_index = hour % frequency_index
    # in the case of bisextile year, we substract 24 hours from the creation date,
    # otherwise updating documents (frequency=yearly update) created the last
    # 24 hours of bissextile year will be launched once every 4 years.
    if creation_date_index >= number_of_hours_in_year:
      creation_date_index = creation_date_index - number_of_hours_in_day

    return creation_date_index

  security.declareProtected(Permissions.AccessContentsInformation, 'isUpdatable')
  def isUpdatable(self):
    """
      This method is used to decide which document can be updated
      in the crawling process. This can depend for example on
      workflow states (publication state,
      validation state) or on roles on the document.
    """
    method = self._getTypeBasedMethod('isUpdatable',
        fallback_script_id = 'Document_isUpdatable')
    return method()
