# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009 Nexedi SA and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
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

from zope.interface import Interface

class IDivergenceController(Interface):
  """Divergence Controller interface specification

  IDivergenceController provides methods to create new
  solver processes based on the current divergence of
  deliveries, movements, simulation movements.

  IDivergenceController must be provided by
  movements, deliveries and by the SolverTool.
  Actual implementation should be handled by SolverTool.

  Whenever movement is not provided, IDivergenceController
  instances should use the most appropriate document
  such as self for a delivery movement.

  Whenever divergence_tester is not provided, all
  applicable divergences are considered.
  """

  def isDivergent(movement=None):
    """
    Returns True if any of the movements provided
    in delivery_or_movement is divergent. Else return False.

    movement -- a movement, a delivery, a simulation movement,
                or a list thereof
    """

  def isConvergent(movement=None):
    """
    Returns False if any of the movements provided
    in delivery_or_movement is divergent. Else return True.

    movement -- a movement, a delivery, a simulation movement,
                or a list thereof
    """

  def getDivergenceList(movement=None):
    """
    Returns a list of divergences of the movements provided
    in delivery_or_movement.

    movement -- a movement, a delivery, a simulation movement,
                or a list thereof
    """

  def newSolverProcess(movement=None):
    """
    Builds a new solver process from the divergence
    analysis of delivery_or_movement. All movements
    which are not divergence are placed in a Solver
    Decision with no Divergence Tester specified.

    movement -- a movement, a delivery, a simulation movement,
                or a list thereof
    """

  def getSolverProcessValueList(movement=None, validation_state=None):
    """
    Returns the list of solver processes which are
    are in a given state and which apply to delivery_or_movement.
    This method is useful to find applicable solver processes
    for a delivery.

    movement -- a movement, a delivery, a simulation movement,
                or a list thereof

    validation_state -- a state of a list of states
                        to filter the result
    """

  def getSolverDecisionValueList(movement=None, validation_state=None):
    """
    Returns the list of solver decisions which apply
    to a given movement.

    movement -- a movement, a delivery, a simulation movement,
                or a list thereof

    validation_state -- a state of a list of states
                        to filter the result
    """

  def getSolvedPropertyApplicationValueList(movement=None, divergence_tester=None):
    """
    Returns the list of documents at which a given divergence resolution
    can be resolved at. For example, in most cases, date divergences can
    only be resolved at delivery level whereas quantities are usually
    resolved at cell level.

    The result of this method is a list of ERP5 documents.

    movement -- a movement, a delivery, a simulation movement,
                or a list thereof

    divergence_tester -- a divergence tester which creates a divergence
                         on movement
    """
