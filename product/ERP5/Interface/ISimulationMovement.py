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

from Interface import Interface

class ISimulationMovement(Interface):
  """
    The SimulationMovement interface
    introduces the possibility to define
    quantity errors between the simulation
    and the reality.

    In short: parent applied rules use the Movement
    API to define quantity.

    Child applied rules use the Delivered API
    to use appropriate values which include
    the delivery_error.

    DeliverySolver either solve divergence by
    setting the delivery_error (then no target
    solver needed, at least for quantity) or
    by changing the quantity (then TargetSolver
    is needed to backtrack the quantity).

    quantity(SM) + delivery_error (SM) =
      quantity(DL) * delivery_ratio(SM)
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
      Returns quantity which was actually
      shipped, taking into account the errors
      of the simulation fixed by the delivery

      quantity + delivery_error
    """

  def getDeliveryConvertedQuantity():
    """
      Returns delivery quantity converted by the resource
    """

  # Divergence API
  def isConvergent():
    """
      Returns the simulation movement is convergent
      or not, with related the delivery
    """

  def isDivergent():
    """
      Returns the simulation movement is divergent
      or not, to related the delivery
    """

  def getDivergenceList():
    """
      Returns listed divergences which is made by tester
      of parent applied rule
      Each divergence has why the delivery was judged
    """

  def isFrozen():
    """
      Returns status of the simulation movement, it is
      frozen or not, once it is frozen, all operations
      can not change anything of the simulation movement
    """

  def isSimulated():
    """
      Returns the simulation movement is simulated or not
      When the simulation movement is simulated, all operations
      can not remove it, but can update, because related delivery
      to be orphan, if can remove it
    """

