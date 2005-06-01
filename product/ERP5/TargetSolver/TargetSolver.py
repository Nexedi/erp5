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


class TargetSolver:
  """
    TargetSolver changes target values of parent movement
    of applied rule based on new target provided on
    a single child movement.

    AppliedRules are considered to be linear. As
    a first approximation, TargetSolver will be independent
    of Applied Rules.

    Possible future solutions:

    - call solve on AppliedRule to allow overriding by
      AppliedRule

    - call 'updateNewTarget' on Applied rule
      to update parent target
  """

  def __init__(self, **kw):
    """
      Creates an instance of TargetSolver with parameters
    """
    self.__dict__.update(kw)
    self.previous_target = {}

  def savePreviousTarget(self, movement):
    from Products.ERP5.Tool.SimulationTool import Target
    # Saves ONCE ONLY the previous target of a given movement
    uid = movement.getUid()
    if not self.previous_target.has_key(uid):
      self.previous_target[uid] = Target(
             target_quantity = movement.getTargetQuantity(),
             target_start_date = movement.getTargetStartDate(),
             target_stop_date = movement.getTargetStopDate())

  def getPreviousTarget(self, movement):
    # Returns the previous target for a given movement
    # This is useful for the first movement solved for example
    self.savePreviousTarget(movement)
    return self.previous_target[movement.getUid()]

  def solve(self, simulation_movement):
    """
      Solve a simulation movement

      previous_target must be accumulated globaly by the solver.
      ie. the first time a target is changed, the previous
      target must be recorded by the solver.

      XXX: maybe we do not need to pass previous_target as parameter
      (since we accumulate it)
    """

  def solveDelivery(self, delivery):
    """
      Called in case it is needed for the solving process
    """
    # Then apply to all movements
    for movement in delivery.getMovementList():
      simulation_movement_list = movement.getDeliveryRelatedValueList(
           portal_type="Simulation Movement")
      for simulation_movement in simulation_movement_list:
        self.solve(simulation_movement)

  def close(self):
    """
      After resolution has taken place, solver
      may do some extra steps, such as create a new delivery
      with deliverable split movements.
    """
    # XXX this is not the job of TargetSolver to create new Delivery !
    pass


