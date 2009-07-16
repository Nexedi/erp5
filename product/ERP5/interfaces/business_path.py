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

from Products.ERP5.interfaces.business_completable import IBusinessCompletable
from Products.ERP5.interfaces.business_buildable import IBusinessBuildable

class IBusinessPath(IBusinessCompletable, IBusinessBuildable):
  """Business Path interface specification
  """
  def getExpectedStartDate(task, predecessor_date=None):
    """Returns the expected start date for this
    path based on the task and provided predecessor_date.

    'task' is a document which follows the ITaskGetter interface
    (getStartDate, getStopDate) and defined the reference dates
    for the business process execution

    'predecessor_date' can be provided as predecessor date and
     to override the date provided in the task
    """

  def getExpectedStopDate(task, predecessor_date=None):
    """Returns the expected stop date for this
    path based on the task and provided predecessor_date.

    'task' is a document which follows the ITaskGetter interface
    (getStartDate, getStopDate) and defined the reference dates
    for the business process execution

    'predecessor_date' can be provided as predecessor date and
     to override the date provided in the task
    """

  def getRelatedSimulationMovementValueList(explanation):
    """Returns list of values of Simulation Movements related to self
    and delivery

    explanation - any document related to business path - which bootstraped
                  process or is related to build of one paths
    """

  def isMovementRelatedWithMovement(movement_value_a, movement_value_b)
    """Checks if self is parent or children to movement_value

    This logic is Business Process specific for Simulation Movements, as
    sequence of Business Process is not related appearance of Simulation Tree

    movement_value_a, movement_value_b - movements to check relation between
    """
