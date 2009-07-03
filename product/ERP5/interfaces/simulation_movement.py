##############################################################################
#
# Copyright (c) 2009 Nexedi SARL and Contributors. All Rights Reserved.
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

from zope.interface import Interface

class ISimulationMovement(Interface):
  """Simulation Movement interface specification

    The SimulationMovement interface introduces the option
    to define quantity errors between the simulation
    and the delivered reality.

    In short: parent applied rules use the Movement
    API to define quantity. Child applied rules
    should use the Delivered API to access appropriate
    quantity values which are take into account the
    delivery_error.

    DeliverySolver either solve divergence by
    setting the delivery_error (then no target
    solver needed, at least for quantity) or
    by changing the quantity (then TargetSolver
    is needed to backtrack the quantity).

    Equation:
      quantity(SM) + delivery_error (SM) =
        quantity(DL) * delivery_ratio(SM)
 
    TODO:
      1. unclear API remaining
 """

  # Delivery API
  def getDeliveryRatio():
    """
      Returns ratio to apply on the quantity
      property of the corresponding delivery
      to obtain the current quantity
    """

  def getDeliveryError():
    """
      Returns correction to make the match
      between delivery quantity and simulation
      quantity consistent
    """

  def getDeliveryQuantity():
    """
      Returns quantity which was actually shipped, taking
      into account the errors of the simulation fixed by
      the delivery

      quantity + delivery_error
    """

  def getDeliveryConvertedQuantity():
    """XXX - unclear
    """

  # Divergence API
  def isConvergent():
    """Tells whether the simulation movement is convergent
      or not, with related delivery
    """

  def isDivergent():
    """Tells whether the simulation movement is divergent
      or not, with related delivery
    """

  def getDivergenceList():
    """Returns a list of divergences 
    XXX - unclear, please explan what the returned documents
    or object are (type, class)
    """

  def isFrozen():
    """Tells whether the simulation movement is frozen.
    By default, looks up the related Business Process Path
    and tells if the simulation state is part of frozen
    states.

    Frozen simulation movement cannot be modified by expanding.
    """

  def isSimulated():
    """XXX - unclear
    """

