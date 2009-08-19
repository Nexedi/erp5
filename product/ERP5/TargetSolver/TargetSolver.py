##############################################################################
#
# Copyright (c) 2002-2009 Nexedi SA and Contributors. All Rights Reserved.
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


class TargetSolver:
  """
    Target solver is used to do backtracking of solved movement up to
    simulation tree.  It is able to detect if parent movement is frozen on
    not, and take proper decision - invoke itself or compensate.

    Target solver is able to generate new simulation tree for:

     * split delivery
     * simple backtrack
     * loss generation
     * etc

    AppliedRules are considered to be linear. As a first approximation,
    TargetSolver will be independent of Applied Rules.

    Possible future solutions:

    - call solve on AppliedRule to allow overriding by
      AppliedRule

    - call 'updateNewTarget' on Applied rule
      to update parent target

    This class is the base class for all target solvers.
    It's virtual due to "solve", which needs to be overloaded.
  """

  def __init__(self, additional_parameters=None, activate_kw=None, **kw):
    """
      Creates an instance of TargetSolver with parameters
    """
    self.__dict__.update(kw)
    if additional_parameters is None:
      additional_parameters = {}
    self.additional_parameters = additional_parameters
    if activate_kw is None:
      activate_kw = {}
    self.activate_kw = activate_kw
    self.previous_target = {}

  def solve(self, simulation_movement):
    """
      Solve a simulation movement
      This function must be implemented by the actual solver which deviates
      from this class.
    """
    raise NotImplementedError

  def solveDelivery(self, delivery):
    """
      Solves the whole delivery.
    """
    # Then apply to all movements
    for movement in delivery.getMovementList():
      self.solveMovement(movement)

  def solveMovement(self, movement):
    """
      Solves a movement.
    """
    # Apply to all simulation movements
    simulation_movement_list = movement.getDeliveryRelatedValueList(
                                             portal_type="Simulation Movement")
    solved_movement_list = []
    for simulation_movement in simulation_movement_list:
      solved_movement_list.append(self.solve(simulation_movement))
    return solved_movement_list
