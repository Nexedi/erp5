##############################################################################
#
# Copyright (c) 2009 Nexedi SA and Contributors. All Rights Reserved.
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

from Products.ERP5.Interface.IBusinessCompletable import IBusinessCompletable
from Products.ERP5.Interface.IBusinessBuildable import IBusinessBuildable

class IBusinessProcess(IBusinessCompletable, IBusinessBuildable):
  """Business Process interface specification
  """
  def getBuildablePathValueList(explanation):
    """Returns the list of Business Path which are buildable

    'explanation' is the Order or Item or Document which is the
    cause of a root applied rule in the simulation
    """

  def getCompletedStateValueList(explanation):
    """Returns the list of Business States which are completed

    'explanation' is the Order or Item or Document which is the
    cause of a root applied rule in the simulation
    """

  def getPartiallyCompletedStateValueList(explanation):
    """Returns the list of Business States which are partially 
    completed

    'explanation' is the Order or Item or Document which is the
    cause of a root applied rule in the simulation
    """

  def getLatestCompletedStateValue(explanation):
    """Returns a completed Business State with no succeeding
    completed Business Path

    'explanation' is the Order or Item or Document which is the
    cause of a root applied rule in the simulation
    """

  def getLatestPartiallyCompletedStateValue(explanation):
    """Returns a partially completed Business State with no
    succeeding partially completed Business Path

    'explanation' is the Order or Item or Document which is the
    cause of a root applied rule in the simulation
    """

  def getLatestCompletedStateValueList(explanation):
    """Returns all completed Business State with no succeeding
    completed Business Path

    'explanation' is the Order or Item or Document which is the
    cause of a root applied rule in the simulation
    """

  def getLatestPartiallyCompletedStateValueList(explanation):
    """Returns all partially completed Business State with no
    succeeding partially completed Business Path

    'explanation' is the Order or Item or Document which is the
    cause of a root applied rule in the simulation
    """
