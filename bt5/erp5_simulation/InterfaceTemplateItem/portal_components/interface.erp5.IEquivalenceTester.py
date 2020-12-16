# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2006-2009 Nexedi SA and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
#                    Rafael Monnerat <rafael@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly adviced to contract a Free Software
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
##############################################################################
"""
erp5.component.interface.IEquivalenceTester
"""

from zope.interface import Interface

class IEquivalenceTester(Interface):
  """
  Equivalence Tester interface specification

  All equivalence testers in ERP5 must implement IEquivalenceTester.
  IEquivalenceTester provides methods to test simulation movements
  equivalence with related delivery movements. A list of
  explanation messages can be generated if needed, and used
  to help users understand why a given delivery line and its related
  simulation movements are divergent.

  IEquivalenceTester also provides methods to match movements
  each other, based on comparison and hash keys. Movement matching
  is required by Rules to decide which simulation movements should
  be updated, deleted, or compensated.

  IEquivalenceTester provides helper methods to copy or update properties
  between movements, from simulation to deliveries or from deliveries to
  simulation.
  """

  # since we aldeary have test() in Predicate class, we use a different
  # method name to test a equivalence.
  def testEquivalence(simulation_movement):
    """
    Tests if simulation_movement is divergent. Returns False (0)
    or True (1).

    If decision_movement is a simulation movement, use
    the recorded properties instead of the native ones.

    simulation_movement -- a simulation movement
    """

  def explain(simulation_movement):
    """
    Returns a single message which explain the nature of
    the equivalence of simulation_movement with its related
    delivery movement.

    If decision_movement is a simulation movement, use
    the recorded properties instead of the native ones.

    simulation_movement -- a simulation movement

    NOTE: this approach is incompatible with previous
    API which was returning a list.

    NOTE: should we provide compatibility here ?
    """

  def generateHashKey(movement):
    """
    Returns a hash key which can be used to optimise the
    matching algorithm between movements. The purpose
    of this hash key is to reduce the size of lists of
    movements which need to be compared using the compare
    method (quadratic complexity).

    If decision_movement is a simulation movement, use
    the recorded properties instead of the native ones.
    """

  def compare(prevision_movement, decision_movement):
    """
    Returns True if prevision_movement and delivery_movement
    match. Returns False else. The method is asymmetric and
    the order of parameter matters. For example, a sourcing
    rule may use a tester which makes sure that movements are
    delivered no sooner than 2 weeks before production but
    no later than the production date.

    If decision_movement is a simulation movement, use
    the recorded properties instead of the native ones.

    This method is used in three cases:
    * an applied rule containted movement vs. a generated movement list
    * a delivery containted movement vs. a generated movement list
    * a delivery containted movement vs. an applied rule containted movement
    """

  def getUpdatablePropertyDict(prevision_movement, decision_movement):
    """
    Returns a list of properties to update on decision_movement
    prevision_movement so that next call to compare returns True.

    prevision_movement -- a simulation movement (prevision)

    decision_movement -- a delivery movement (decision)
    """

  def update(prevision_movement, decision_movement):
    """
    Updates decision_movement with properties from
    prevision_movement so that next call to
    compare returns True. This method is normally
    invoked to copy properties from simulation movements
    to delivery movements. It is also invoked to copy
    properties from temp simulation movements of
    Aggregated Amount Lists to pre-existing simulation
    movements.

    If decision_movement is a simulation movement, then
    do not update recorded properties.

    prevision_movement -- a simulation movement (prevision)

    decision_movement -- a delivery movement (decision)

    NOTE: recorded (forced) properties are not updated by
    expand.

    NOTE2: it is still unknown how to update properties from
    a simulation movement to the relevant level of
    delivery / line / cell.
    """
